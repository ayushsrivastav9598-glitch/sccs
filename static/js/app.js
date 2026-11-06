/**
 * Smart Campus Classroom System (SCCS)
 * Frontend Application Controller - Clean Minimalist Black/White/Grey Edition
 */

const API_BASE = "";

// State
let currentUser = {
    id: 2,
    name: "Dr. R. K. Sharma",
    email: "prof.sharma@ddugu.ac.in",
    role: "faculty",
    branch: "CSE",
    year: 0,
    section: "ALL",
    token: ""
};

let currentBuilding = "IET";
let currentFloor = "1st Floor";
let blueprintCache = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    initClock();
    setupEventListeners();
    // Default demo login as Faculty for immediate full functionality
    loginAs("faculty");
    loadBlueprints();
    loadTimetable();
    loadNotices();
});

function initClock() {
    const clockEl = document.getElementById("live-clock");
    const update = () => {
        const now = new Date();
        if (clockEl) {
            clockEl.textContent = now.toLocaleDateString('en-IN', {
                weekday: 'short', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit', second: '2-digit'
            });
        }
    };
    update();
    setInterval(update, 1000);
}

function setupEventListeners() {
    // Nav tabs
    document.querySelectorAll(".nav-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            const target = tab.dataset.tab;
            switchTab(target);
        });
    });

    // Today's date default
    const today = new Date().toISOString().split("T")[0];
    const dateInputs = document.querySelectorAll("input[type='date']");
    dateInputs.forEach(i => { if (!i.value) i.value = today; });
}

function switchTab(tabId) {
    document.querySelectorAll(".nav-tab").forEach(t => t.classList.toggle("active", t.dataset.tab === tabId));
    document.querySelectorAll(".tab-pane").forEach(p => p.classList.toggle("active", p.id === tabId));

    if (tabId === "tab-blueprints") loadBlueprints();
    else if (tabId === "tab-timetable") loadTimetable();
    else if (tabId === "tab-notices") loadNotices();
    else if (tabId === "tab-reports") loadReports();
    else if (tabId === "tab-audit") loadAudit();
}

// Quick Demo Authentication Switcher
async function loginAs(role) {
    let email = "prof.sharma@ddugu.ac.in";
    let pwd = "faculty123";

    if (role === "student") {
        email = "student.cse@ddugu.ac.in";
        pwd = "student123";
    } else if (role === "admin") {
        email = "admin@ddugu.ac.in";
        pwd = "admin123";
    }

    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password: pwd })
        });
        const data = await res.json();
        if (res.ok) {
            currentUser = data.user;
            currentUser.token = data.token;
            updateUserUI();
            showToast(`Active persona: ${currentUser.name} (${currentUser.role.toUpperCase()})`);
        } else {
            console.error("Login failed:", data.detail);
        }
    } catch (err) {
        console.error("Auth error:", err);
    }
}

function updateUserUI() {
    const nameEl = document.getElementById("user-display-name");
    const rolePill = document.getElementById("user-role-pill");
    const branchEl = document.getElementById("user-branch-display");

    if (nameEl) nameEl.textContent = currentUser.name;
    if (rolePill) {
        rolePill.textContent = currentUser.role.toUpperCase();
        rolePill.className = `role-pill role-${currentUser.role}`;
    }
    if (branchEl) {
        branchEl.textContent = currentUser.branch ? `(${currentUser.branch})` : "";
    }

    // Role-dependent controls
    const facultySections = document.querySelectorAll(".faculty-only");
    const adminSections = document.querySelectorAll(".admin-only");

    facultySections.forEach(el => {
        el.style.display = (currentUser.role === "faculty" || currentUser.role === "admin") ? "block" : "none";
    });
    adminSections.forEach(el => {
        el.style.display = (currentUser.role === "admin") ? "block" : "none";
    });
}

function getAuthHeader() {
    return currentUser.token ? { "Authorization": `Bearer ${currentUser.token}` } : {};
}

// ==================== Blueprints Module ====================
async function loadBlueprints() {
    const dateInput = document.getElementById("bp-date-filter");
    const timeInput = document.getElementById("bp-time-filter");
    const date = dateInput ? dateInput.value : new Date().toISOString().split("T")[0];
    const time = timeInput ? timeInput.value : "10:00";

    try {
        const res = await fetch(`${API_BASE}/rooms/blueprints?date=${date}&time_slot=${time}`);
        const data = await res.json();
        blueprintCache = data;
        renderBlueprints();
    } catch (err) {
        console.error("Error loading blueprints:", err);
    }
}

function selectBuilding(bId) {
    currentBuilding = bId;
    document.querySelectorAll(".building-tab-btn").forEach(b => b.classList.toggle("active", b.dataset.building === bId));

    if (bId === "IET") {
        currentFloor = "1st Floor";
    } else {
        currentFloor = "Ground";
    }
    renderFloorButtons();
    renderBlueprints();
}

function selectFloor(floorName) {
    currentFloor = floorName;
    renderFloorButtons();
    renderBlueprints();
}

function renderFloorButtons() {
    const container = document.getElementById("floor-buttons-container");
    if (!container) return;

    let floors = [];
    if (currentBuilding === "IET") {
        floors = ["Ground", "1st Floor", "2nd Floor"];
    } else {
        floors = ["Ground", "1st Floor"];
    }

    container.innerHTML = floors.map(fl => `
        <button class="floor-btn ${fl === currentFloor ? 'active' : ''}" onclick="selectFloor('${fl}')">
            ${fl}
        </button>
    `).join("");
}

function renderBlueprints() {
    if (!blueprintCache) return;
    const canvas = document.getElementById("blueprint-rooms-container");
    const infoHeader = document.getElementById("blueprint-floor-info");

    const building = blueprintCache.buildings.find(b => b.id === currentBuilding);
    if (!building) return;

    if (infoHeader) {
        const distNote = building.distance_from_iet_meters > 0 ? ` (~${building.distance_from_iet_meters}m from IET Main)` : " (Main Complex)";
        infoHeader.innerHTML = `<strong>${building.name}</strong> &mdash; ${currentFloor} ${distNote}`;
    }

    const rooms = (building.floors && building.floors[currentFloor]) ? building.floors[currentFloor] : [];
    if (rooms.length === 0) {
        canvas.innerHTML = `<div style="color: #6b7280; padding: 2rem;">No rooms registered on this floor.</div>`;
        return;
    }

    canvas.innerHTML = rooms.map(r => {
        const isOccupied = r.is_occupied;
        const statusClass = isOccupied ? "occupied" : "vacant";
        const tagText = isOccupied ? "Occupied" : "Vacant";
        const tagClass = isOccupied ? "status-occupied" : "status-vacant";

        let occDetail = "";
        if (isOccupied && r.current_booking) {
            const cb = r.current_booking;
            const testBadge = cb.is_test_data ? `<span class="badge badge-test">[TEST]</span> ` : "";
            occDetail = `<div style="font-size:0.75rem; color:#4b5563; margin-top:0.35rem; border-top:1px dashed #e5e7eb; padding-top:0.25rem;">
                ${testBadge}<strong>${escapeHtml(cb.title)}</strong><br/>
                ${escapeHtml(cb.booked_by)} (${cb.time})
            </div>`;
        }

        return `
            <div class="room-node ${statusClass}" onclick="openRoomModal('${r.id}')" title="Click for details & booking">
                <div class="code">${r.code}</div>
                <div class="meta">${escapeHtml(r.name)}</div>
                <div class="meta">Cap: <strong>${r.capacity}</strong> &bull; ${r.room_type}</div>
                <span class="status-tag ${tagClass}">${tagText}</span>
                ${occDetail}
            </div>
        `;
    }).join("");
}

// Room Details Modal
async function openRoomModal(roomId) {
    try {
        const res = await fetch(`${API_BASE}/rooms/${roomId}`);
        const room = await res.json();

        document.getElementById("modal-room-title").textContent = `${room.name} (${room.code})`;
        document.getElementById("modal-room-building").textContent = `${room.building_id} - ${room.floor}`;
        document.getElementById("modal-room-capacity").textContent = `${room.capacity} Students`;
        document.getElementById("modal-room-type").textContent = room.room_type;
        document.getElementById("modal-room-facilities").textContent = room.facilities || "Standard Audio-Visual";
        document.getElementById("modal-room-permitted").textContent = room.permitted_uses || "General Academic";

        // Prepopulate booking form room input
        const bookRoomInput = document.getElementById("book-room-id");
        if (bookRoomInput) bookRoomInput.value = room.id;

        // Schedule table in modal
        const schedBody = document.getElementById("modal-room-schedule");
        if (schedBody) {
            if (room.schedule && room.schedule.length > 0) {
                schedBody.innerHTML = room.schedule.map(b => `
                    <tr>
                        <td>${b.date}</td>
                        <td>${b.start_time} - ${b.end_time}</td>
                        <td><strong>${escapeHtml(b.title)}</strong> ${b.is_test_data ? '<span class="badge badge-test">TEST</span>' : ''}</td>
                        <td>${escapeHtml(b.booked_by_name)}</td>
                        <td>${b.purpose}</td>
                    </tr>
                `).join("");
            } else {
                schedBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#6b7280;">No bookings for selected date. Room is fully vacant.</td></tr>`;
            }
        }

        document.getElementById("room-modal").classList.add("active");
    } catch (err) {
        console.error("Error opening room modal:", err);
    }
}

function closeRoomModal() {
    document.getElementById("room-modal").classList.remove("active");
}

function quickBookFromModal() {
    closeRoomModal();
    switchTab("tab-booking");
}

// ==================== Availability Search ====================
async function searchAvailability() {
    const date = document.getElementById("avail-date").value;
    const start_time = document.getElementById("avail-time").value;
    const duration = parseInt(document.getElementById("avail-duration").value) || 60;
    const building_id = document.getElementById("avail-building").value || null;
    const room_type = document.getElementById("avail-type").value || null;
    const required_capacity = parseInt(document.getElementById("avail-capacity").value) || null;

    const payload = {
        date,
        start_time,
        duration_minutes: duration,
        building_id: building_id === "ALL" ? null : building_id,
        room_type: room_type === "ALL" ? null : room_type,
        required_capacity: required_capacity > 0 ? required_capacity : null
    };

    try {
        const res = await fetch(`${API_BASE}/rooms/availability`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        renderAvailabilityResults(data);
    } catch (err) {
        console.error("Search error:", err);
    }
}

function renderAvailabilityResults(data) {
    const container = document.getElementById("avail-results-container");
    if (!container) return;

    if (!data.results || data.results.length === 0) {
        container.innerHTML = `<div class="card" style="text-align:center; color:#6b7280;">No matching rooms found for the selected criteria.</div>`;
        return;
    }

    container.innerHTML = `
        <div style="margin-bottom: 0.65rem; font-size: 0.8rem; color: #4b5563;">
            Found <strong>${data.available_rooms_count}</strong> vacant out of ${data.total_rooms_checked} checked rooms on <strong>${data.date} (${data.time_slot})</strong>
        </div>
        <div class="grid-3">
            ${data.results.map(item => {
                const r = item.room;
                const isAvail = item.is_available;
                return `
                    <div class="card" style="border: 1px solid ${isAvail ? '#d1d5db' : '#e5e7eb'}; background: ${isAvail ? '#ffffff' : '#fafafa'};">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <h4 style="font-size:0.95rem; font-weight:700;">${r.code} - ${escapeHtml(r.name)}</h4>
                                <div style="font-size:0.75rem; color:#6b7280;">${r.building_id} (${r.floor}) &bull; Cap: ${r.capacity}</div>
                            </div>
                            <span class="status-tag ${isAvail ? 'status-vacant' : 'status-occupied'}">
                                ${isAvail ? 'Vacant' : 'Booked'}
                            </span>
                        </div>
                        <div style="font-size:0.75rem; margin:0.4rem 0; color:#4b5563;">
                            ${escapeHtml(r.facilities || 'Standard equipment')}
                        </div>
                        ${!isAvail ? `<div style="font-size:0.75rem; color:#b91c1c; margin-bottom:0.4rem;">${escapeHtml(item.conflict_reason || '')}</div>` : ''}
                        <button class="btn btn-sm ${isAvail ? 'btn-primary' : 'btn-secondary'}" onclick="prefillBooking('${r.id}', '${r.capacity}')">
                            ${isAvail ? 'Select Room' : 'View Schedule'}
                        </button>
                    </div>
                `;
            }).join("")}
        </div>
    `;
}

function prefillBooking(roomId, capacity) {
    const roomSelect = document.getElementById("book-room-id");
    const capInput = document.getElementById("book-expected-students");
    if (roomSelect) roomSelect.value = roomId;
    if (capInput && capacity) capInput.value = capacity;
    switchTab("tab-booking");
    document.getElementById("booking-form-card")?.scrollIntoView({ behavior: 'smooth' });
}

// ==================== Booking Submission & Conflict Handling ====================
async function handleBookingSubmit(e) {
    e.preventDefault();
    const conflictBox = document.getElementById("booking-conflict-alert");
    conflictBox.style.display = "none";

    const payload = {
        room_id: document.getElementById("book-room-id").value,
        title: document.getElementById("book-title").value,
        purpose: document.getElementById("book-purpose").value,
        date: document.getElementById("book-date").value,
        start_time: document.getElementById("book-start-time").value,
        duration_minutes: parseInt(document.getElementById("book-duration").value) || 60,
        branch: document.getElementById("book-branch").value,
        year: parseInt(document.getElementById("book-year").value) || 0,
        section: document.getElementById("book-section").value,
        expected_students: parseInt(document.getElementById("book-expected-students").value) || 75,
        notes: document.getElementById("book-notes").value,
        is_test_data: document.getElementById("book-is-test").checked
    };

    try {
        const res = await fetch(`${API_BASE}/bookings`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeader()
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.status === 201) {
            showToast("Booking confirmed successfully!");
            document.getElementById("booking-form").reset();
            loadBlueprints();
            loadTimetable();
            loadAudit();
        } else if (res.status === 409 || res.status === 400) {
            // Conflict or Capacity Warning
            displayConflictAlert(data);
        } else {
            showToast(data.detail || "Booking failed");
        }
    } catch (err) {
        console.error("Booking error:", err);
        showToast("Error processing reservation");
    }
}

function displayConflictAlert(conflictData) {
    const alertBox = document.getElementById("booking-conflict-alert");
    alertBox.style.display = "block";

    let html = `
        <div class="conflict-box">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.4rem;">
                <h4 style="font-size:0.95rem; font-weight:700; color:#111827;">Room Conflict Warning</h4>
                <span class="badge" style="background:#111827; color:#ffffff;">409 CONFLICT</span>
            </div>
            <p style="color:#4b5563; font-size:0.85rem; margin-bottom:0.85rem; line-height:1.4;">
                ${escapeHtml(conflictData.detail)}
            </p>
    `;

    if (conflictData.alternative_rooms && conflictData.alternative_rooms.length > 0) {
        html += `
            <div style="border-top:1px solid #e5e7eb; padding-top:0.75rem;">
                <div style="font-size:0.8rem; font-weight:700; color:#111827; margin-bottom:0.5rem;">
                    Suggested Available Venues for Same Time Slot:
                </div>
                <div style="display:flex; flex-direction:column; gap:0.4rem;">
        `;

        conflictData.alternative_rooms.forEach(alt => {
            const isDB = alt.building_id === "DEEKSHA_BHAWAN";
            html += `
                <div class="alt-item">
                    <div>
                        <div style="font-size:0.85rem; font-weight:700;">
                            ${alt.code} - ${escapeHtml(alt.name)}
                            <span class="badge" style="margin-left:0.35rem;">${isDB ? 'Deeksha Bhawan (~100m)' : 'IET Main'}</span>
                        </div>
                        <div style="font-size:0.75rem; color:#6b7280; margin-top:0.15rem;">
                            ${escapeHtml(alt.reason)}
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span class="alt-score">Fit: ${alt.fit_score}%</span>
                        <button class="btn btn-sm btn-primary" type="button" onclick="chooseAlternative('${alt.room_id}')">
                            Select Room
                        </button>
                    </div>
                </div>
            `;
        });

        html += `</div></div>`;
    }

    html += `</div>`;
    alertBox.innerHTML = html;
    alertBox.scrollIntoView({ behavior: 'smooth' });
}

function chooseAlternative(altRoomId) {
    document.getElementById("book-room-id").value = altRoomId;
    document.getElementById("booking-conflict-alert").style.display = "none";
    showToast(`Switched room to ${altRoomId}. Click 'Confirm Room Booking' to finalize.`);
}

// ==================== Timetable Module ====================
async function loadTimetable() {
    const branch = document.getElementById("tt-branch")?.value || "CSE";
    const year = document.getElementById("tt-year")?.value || 3;
    const section = document.getElementById("tt-section")?.value || "A";

    try {
        const res = await fetch(`${API_BASE}/schedules/timetable?branch=${branch}&year=${year}&section=${section}`);
        const list = await res.json();
        renderTimetable(list);
    } catch (err) {
        console.error("Timetable error:", err);
    }
}

function downloadTimetable(format = 'csv') {
    const branch = document.getElementById("tt-branch")?.value || "ALL";
    const year = document.getElementById("tt-year")?.value || 0;
    const section = document.getElementById("tt-section")?.value || "ALL";
    const url = `${API_BASE}/schedules/export?branch=${branch}&year=${year}&section=${section}&export_format=${format}`;
    window.open(url, '_blank');
}

function renderTimetable(list) {
    const tbody = document.getElementById("timetable-tbody");
    if (!tbody) return;

    if (!list || list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#6b7280; padding:2rem;">No scheduled lectures or exams found for this branch & year.</td></tr>`;
        return;
    }

    tbody.innerHTML = list.map(b => {
        const isExam = b.purpose.toLowerCase().includes("exam");
        const examBadge = isExam ? `<span class="badge badge-exam">MINOR EXAM</span>` : `<span class="badge">${b.purpose}</span>`;
        const testBadge = b.is_test_data ? `<span class="badge badge-test">[TEST]</span>` : '';

        return `
            <tr style="${isExam ? 'background:#fafafa;' : ''}">
                <td style="font-weight:600;">${b.date}</td>
                <td><strong>${b.start_time} - ${b.end_time}</strong></td>
                <td>
                    <strong>${b.room_code}</strong> (${escapeHtml(b.room_name)})<br/>
                    <span style="font-size:0.75rem; color:#6b7280;">${b.building_id} - ${b.floor}</span>
                </td>
                <td>
                    ${testBadge} <strong>${escapeHtml(b.title)}</strong><br/>
                    <span style="font-size:0.75rem; color:#6b7280;">Expected: ${b.expected_students} students</span>
                </td>
                <td>${examBadge}</td>
                <td>${escapeHtml(b.booked_by_name)}</td>
            </tr>
        `;
    }).join("");
}

// ==================== Academic Notices Module ====================
async function loadNotices() {
    try {
        const res = await fetch(`${API_BASE}/notices`);
        const notices = await res.json();
        renderNotices(notices);
    } catch (err) {
        console.error("Notices error:", err);
    }
}

function renderNotices(notices) {
    const feed = document.getElementById("notices-feed");
    if (!feed) return;

    if (!notices || notices.length === 0) {
        feed.innerHTML = `<div style="text-align:center; color:#6b7280; padding:2rem;">No announcements currently posted.</div>`;
        return;
    }

    feed.innerHTML = notices.map(n => {
        let pBadge = `<span class="badge">${n.priority}</span>`;
        if (n.priority === "URGENT") pBadge = `<span class="badge badge-urgent">URGENT</span>`;
        else if (n.priority === "HIGH") pBadge = `<span class="badge badge-exam">HIGH PRIORITY</span>`;

        return `
            <div class="card" style="margin-bottom:0.75rem; border-left: 3px solid ${n.priority === 'URGENT' ? '#111827' : '#9ca3af'};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
                    <div style="display:flex; align-items:center; gap:0.4rem;">
                        ${pBadge}
                        <h4 style="font-size:0.95rem; font-weight:700; color:#111827;">${escapeHtml(n.title)}</h4>
                    </div>
                    <span style="font-size:0.75rem; color:#6b7280;">Target: ${n.target_branch} (Yr ${n.target_year || 'All'})</span>
                </div>
                <p style="color:#4b5563; font-size:0.85rem; line-height:1.4;">${escapeHtml(n.content)}</p>
                <div style="font-size:0.75rem; color:#6b7280; margin-top:0.5rem; display:flex; justify-content:space-between; border-top:1px solid #f3f4f6; padding-top:0.35rem;">
                    <span>By: <strong>${escapeHtml(n.published_by_name || 'Academic Office')}</strong></span>
                    <span>${new Date(n.created_at).toLocaleDateString('en-IN')}</span>
                </div>
            </div>
        `;
    }).join("");
}

async function handleNoticeSubmit(e) {
    e.preventDefault();
    const payload = {
        title: document.getElementById("notice-title").value,
        content: document.getElementById("notice-content").value,
        notice_type: document.getElementById("notice-type").value,
        target_branch: document.getElementById("notice-branch").value,
        target_year: parseInt(document.getElementById("notice-year").value) || 0,
        priority: document.getElementById("notice-priority").value
    };

    try {
        const res = await fetch(`${API_BASE}/notices`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeader()
            },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            showToast("Notice published successfully!");
            document.getElementById("notice-form").reset();
            loadNotices();
        } else {
            const err = await res.json();
            showToast(err.detail || "Failed to publish notice");
        }
    } catch (err) {
        showToast("Error creating notice");
    }
}

// ==================== Student Reports Module ====================
async function loadReports() {
    try {
        const res = await fetch(`${API_BASE}/reports`, {
            headers: getAuthHeader()
        });
        const reports = await res.json();
        renderReports(reports);
    } catch (err) {
        console.error("Reports error:", err);
    }
}

function renderReports(reports) {
    const listEl = document.getElementById("reports-list");
    if (!listEl) return;

    if (!reports || reports.length === 0) {
        listEl.innerHTML = `<div style="text-align:center; color:#6b7280; padding:1.5rem;">No conflict or grievance reports submitted.</div>`;
        return;
    }

    listEl.innerHTML = reports.map(r => {
        let statusBadge = `<span class="badge">OPEN</span>`;
        if (r.status === "RESOLVED") statusBadge = `<span class="badge badge-urgent">RESOLVED</span>`;
        else if (r.status === "DISMISSED") statusBadge = `<span class="badge">DISMISSED</span>`;

        const canResolve = (currentUser.role === "admin" || currentUser.role === "faculty");

        return `
            <div class="card" style="margin-bottom:0.75rem;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <h4 style="font-size:0.9rem; font-weight:700; color:#111827;">${escapeHtml(r.title)}</h4>
                        <div style="font-size:0.75rem; color:#6b7280;">
                            Filed by ${escapeHtml(r.student_name)} &bull; ${r.report_type}
                        </div>
                    </div>
                    ${statusBadge}
                </div>
                <p style="font-size:0.8rem; color:#4b5563; margin:0.4rem 0;">${escapeHtml(r.description)}</p>
                ${r.admin_notes ? `<div style="background:#f9fafb; border:1px solid #e5e7eb; padding:0.4rem; border-radius:4px; font-size:0.75rem; color:#111827;"><strong>Staff Response:</strong> ${escapeHtml(r.admin_notes)}</div>` : ''}

                ${canResolve && r.status === 'OPEN' ? `
                    <div style="margin-top:0.5rem; display:flex; gap:0.4rem;">
                        <button class="btn btn-sm btn-primary" onclick="resolveReport(${r.id}, 'RESOLVED')">Mark Resolved</button>
                        <button class="btn btn-sm btn-secondary" onclick="resolveReport(${r.id}, 'DISMISSED')">Dismiss</button>
                    </div>
                ` : ''}
            </div>
        `;
    }).join("");
}

async function handleStudentReportSubmit(e) {
    e.preventDefault();
    const payload = {
        title: document.getElementById("rep-title").value,
        report_type: document.getElementById("rep-type").value,
        description: document.getElementById("rep-desc").value
    };

    try {
        const res = await fetch(`${API_BASE}/reports`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeader()
            },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            showToast("Report submitted for review.");
            document.getElementById("report-form").reset();
            loadReports();
        } else {
            const err = await res.json();
            showToast(err.detail || "Failed to submit report");
        }
    } catch (err) {
        showToast("Network error submitting report");
    }
}

async function resolveReport(reportId, status) {
    const notes = prompt("Enter resolution notes:", "Schedule verified and updated.");
    if (notes === null) return;

    try {
        const res = await fetch(`${API_BASE}/reports/${reportId}/resolve`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeader()
            },
            body: JSON.stringify({ status, admin_notes: notes })
        });
        if (res.ok) {
            showToast(`Report updated to ${status}`);
            loadReports();
        }
    } catch (err) {
        showToast("Error updating report");
    }
}

// ==================== AI Assistant Module ====================
async function askAI(quickQuery = null) {
    const input = document.getElementById("ai-prompt-input");
    const query = quickQuery || (input ? input.value : "");
    if (!query) return;

    const resultBox = document.getElementById("ai-response-box");
    resultBox.innerHTML = `<div style="padding:1.5rem; text-align:center; color:#111827;">Analyzing campus constraints & schedule records...</div>`;

    try {
        const res = await fetch(`${API_BASE}/ai/assist`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
        const data = await res.json();
        renderAIResponse(data);
    } catch (err) {
        resultBox.innerHTML = `<div style="color:#b91c1c; padding:1rem;">Failed to get AI assistance.</div>`;
    }
}

function renderAIResponse(data) {
    const resultBox = document.getElementById("ai-response-box");
    if (!resultBox) return;

    let html = `
        <div style="background:#ffffff; border:1px solid #d1d5db; border-radius:6px; padding:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem; border-bottom:1px solid #e5e7eb; padding-bottom:0.5rem;">
                <h4 style="color:#111827; font-size:0.95rem; font-weight:700;">AI Optimization Results</h4>
                <span class="badge">Rule-Based Solver</span>
            </div>
            <div style="background:#f9fafb; border:1px solid #e5e7eb; padding:0.5rem 0.75rem; border-radius:4px; font-size:0.8rem; color:#4b5563; margin-bottom:0.75rem;">
                <strong>Intent:</strong> ${escapeHtml(data.parsed_intent)}<br/>
                <strong>Parameters:</strong> Date: ${data.extracted_params.date} &bull; Time: ${data.extracted_params.start_time} &bull; Capacity: ${data.extracted_params.capacity} seats
            </div>
            <div style="font-size:0.8rem; font-weight:700; color:#111827; margin-bottom:0.4rem;">Optimal Venues:</div>
            <div style="display:flex; flex-direction:column; gap:0.4rem;">
    `;

    if (data.recommended_rooms && data.recommended_rooms.length > 0) {
        data.recommended_rooms.forEach(alt => {
            const isDB = alt.building_id === "DEEKSHA_BHAWAN";
            html += `
                <div class="alt-item">
                    <div>
                        <strong>${alt.code} - ${escapeHtml(alt.name)}</strong>
                        <span class="badge" style="margin-left:0.35rem;">
                            ${isDB ? 'Deeksha Bhawan (~100m)' : 'IET Main'}
                        </span>
                        <div style="font-size:0.75rem; color:#6b7280; margin-top:0.15rem;">${escapeHtml(alt.reason)}</div>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span class="alt-score">Match: ${alt.fit_score}%</span>
                        <button class="btn btn-sm btn-primary" onclick="prefillBooking('${alt.room_id}', '${data.extracted_params.capacity}')">
                            Select Room
                        </button>
                    </div>
                </div>
            `;
        });
    } else {
        html += `<div style="color:#6b7280; font-size:0.8rem;">No rooms vacant at this exact slot. Alternative times: ${data.available_time_slots.slice(0, 3).join(", ")}</div>`;
    }

    html += `</div></div>`;
    resultBox.innerHTML = html;
}

// ==================== Audit Module ====================
async function loadAudit() {
    try {
        const res = await fetch(`${API_BASE}/audit?limit=25`, {
            headers: getAuthHeader()
        });
        const logs = await res.json();
        renderAudit(logs);
    } catch (err) {
        console.error("Audit error:", err);
    }
}

function renderAudit(logs) {
    const list = document.getElementById("audit-timeline");
    if (!list) return;

    if (!logs || logs.length === 0) {
        list.innerHTML = `<div style="text-align:center; color:#6b7280; padding:1.5rem;">No audit logs recorded yet.</div>`;
        return;
    }

    list.innerHTML = logs.map(l => `
        <div class="timeline-item">
            <div class="meta">${new Date(l.timestamp).toLocaleDateString('en-IN')} ${new Date(l.timestamp).toLocaleTimeString('en-IN')} &bull; User: <strong>${escapeHtml(l.user_name || 'System')}</strong> (${l.user_role || 'system'})</div>
            <div class="title">[${l.action}] ${escapeHtml(l.entity_type)} #${l.entity_id}</div>
            <div style="font-size:0.8rem; color:#4b5563; margin-top:0.15rem;">${escapeHtml(l.details)}</div>
        </div>
    `).join("");
}

// Helpers
function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showToast(message) {
    const toast = document.createElement("div");
    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.right = "20px";
    toast.style.background = "#111827";
    toast.style.color = "#ffffff";
    toast.style.padding = "0.6rem 1rem";
    toast.style.borderRadius = "4px";
    toast.style.border = "1px solid #374151";
    toast.style.boxShadow = "0 4px 12px rgba(0,0,0,0.12)";
    toast.style.zIndex = "9999";
    toast.style.fontSize = "0.85rem";
    toast.style.fontWeight = "500";
    toast.textContent = message;

    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.25s ease";
        setTimeout(() => toast.remove(), 250);
    }, 2800);
}
