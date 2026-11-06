import sqlite3
from fastapi import APIRouter, HTTPException, Depends, status
from ..database import get_db
from ..models import UserRegister, UserLogin, UserOut, AuthResponse
from ..auth import hash_password, verify_password, create_access_token, get_current_user
from ..engine import log_audit

router = APIRouter(tags=["Authentication"])

@router.post("/auth/register", response_model=AuthResponse)
def register(user: UserRegister):
    hashed_pwd = hash_password(user.password)
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, password, role, branch, year, section, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user.name, user.email, hashed_pwd, user.role, user.branch, user.year, user.section, user.department))
        user_id = cursor.lastrowid

        # Keep students table synced
        cursor.execute("""
            INSERT OR REPLACE INTO students (id, name, email, password, role, branch, year, section, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, user.name, user.email, hashed_pwd, user.role, user.branch, user.year, user.section, user.department))
        conn.commit()

        token = create_access_token(user_id, user.email, user.role, user.name)
        user_out = UserOut(
            id=user_id,
            name=user.name,
            email=user.email,
            role=user.role,
            branch=user.branch,
            year=user.year,
            section=user.section,
            department=user.department
        )

        log_audit("USER_REGISTERED", "USER", str(user_id), f"User {user.name} ({user.email}) registered with role {user.role}", user_out.model_dump())

        return AuthResponse(
            message=f"{user.role.capitalize()} registered successfully!",
            token=token,
            user=user_out
        )

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in system"
        )
    finally:
        conn.close()

@router.post("/auth/login", response_model=AuthResponse)
def login(login_data: UserLogin):
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (login_data.email,)
        ).fetchone()

        if user is None:
            # Fallback to students table if not yet copied
            user = conn.execute(
                "SELECT * FROM students WHERE email = ?",
                (login_data.email,)
            ).fetchone()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(user["password"], login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        role = user["role"] if ("role" in user.keys() and user["role"]) else "student"
        token = create_access_token(user["id"], user["email"], role, user["name"])

        user_out = UserOut(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            role=role,
            branch=user["branch"] if "branch" in user.keys() else None,
            year=user["year"] if "year" in user.keys() else None,
            section=user["section"] if "section" in user.keys() else None,
            department=user["department"] if "department" in user.keys() else None,
            created_at=str(user["created_at"]) if "created_at" in user.keys() else None
        )

        return AuthResponse(
            message="Login successful!",
            token=token,
            user=user_out
        )
    finally:
        conn.close()

@router.get("/auth/me", response_model=UserOut)
def get_profile(current_user: dict = Depends(get_current_user)):
    return UserOut(**current_user)

@router.get("/auth/users")
def list_users(current_user: dict = Depends(get_current_user)):
    # Faculty and Admin can inspect users
    if current_user["role"] not in ["faculty", "admin"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    conn = get_db()
    users = conn.execute(
        "SELECT id, name, email, role, branch, year, section, department, created_at FROM users"
    ).fetchall()
    conn.close()
    return [dict(u) for u in users]

