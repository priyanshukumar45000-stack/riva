document.addEventListener("DOMContentLoaded", () => {
    // ---- default dates: 30 days out, 5-day trip ----
    const startInput = document.getElementById("startDate");
    const endInput = document.getElementById("endDate");
    const today = new Date();
    const start = new Date(today); start.setDate(start.getDate() + 30);
    const end = new Date(today); end.setDate(end.getDate() + 35);
    startInput.value = toISODate(start);
    endInput.value = toISODate(end);

    // ---- API key check ----
    fetch("/api/status")
        .then(r => r.json())
        .then(data => {
            if (!data.configured) {
                document.getElementById("apiKeyWarning").classList.remove("hidden");
                document.getElementById("generateBtn").disabled = true;
            }
        })
        .catch(() => {});

    // ---- interest chip toggles ----
    document.querySelectorAll(".chip").forEach(chip => {
        chip.addEventListener("click", () => chip.classList.toggle("selected"));
    });

    // ---- tab switching ----
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
        });
    });

    // ---- form submit ----
    document.getElementById("tripForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        await generateItinerary();
    });
});

function toISODate(d) {
    return d.toISOString().split("T")[0];
}

function showError(msg) {
    const el = document.getElementById("formError");
    el.textContent = msg;
    el.classList.remove("hidden");
}

function clearError() {
    document.getElementById("formError").classList.add("hidden");
}

async function generateItinerary() {
    clearError();

    const destination = document.getElementById("destination").value.trim();
    const origin = document.getElementById("origin").value.trim();
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;
    const travelers = document.getElementById("travelers").value;
    const budgetTier = document.getElementById("budgetTier").value;
    const pace = document.getElementById("pace").value;
    const model = document.getElementById("model").value;
    const interests = Array.from(document.querySelectorAll(".chip.selected")).map(c => c.dataset.value);

    if (!destination) { showError("Please enter a destination."); return; }
    if (new Date(endDate) < new Date(startDate)) { showError("End date must be after start date."); return; }

    const btn = document.getElementById("generateBtn");
    btn.disabled = true;

    document.getElementById("placeholder").classList.add("hidden");
    document.getElementById("results").classList.add("hidden");
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("loadingText").textContent = `Planning your trip to ${destination} with ${model}...`;

    try {
        const resp = await fetch("/api/plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                destination, origin, start_date: startDate, end_date: endDate,
                travelers, budget_tier: budgetTier, interests, pace, model,
            }),
        });

        const data = await resp.json();

        if (!resp.ok) {
            throw new Error(data.error || "Something went wrong.");
        }

        renderResults(data);
    } catch (err) {
        showError("AI generation failed: " + err.message);
        document.getElementById("placeholder").classList.remove("hidden");
    } finally {
        document.getElementById("loading").classList.add("hidden");
        btn.disabled = false;
    }
}

function renderResults(data) {
    document.getElementById("resultsTitle").textContent =
        `${data.meta.destination} — ${data.meta.num_days} days`;

    const summaryEl = document.getElementById("destinationSummary");
    if (data.itinerary.destination_summary) {
        summaryEl.textContent = data.itinerary.destination_summary;
        summaryEl.classList.remove("hidden");
    } else {
        summaryEl.classList.add("hidden");
    }

    renderDays(data.itinerary.days);
    renderTips("packingTips", "🎒 Packing tips", data.itinerary.packing_tips);
    renderTips("localTips", "💡 Local tips", data.itinerary.local_tips);
    renderWeather(data.weather);
    renderBudget(data.budget);
    renderBookingLinks(data.links);

    document.getElementById("results").classList.remove("hidden");
}

function renderDays(days) {
    const container = document.getElementById("dayList");
    container.innerHTML = "";

    days.forEach((day, idx) => {
        const row = document.createElement("div");
        row.className = "day-row";

        const badge = document.createElement("div");
        badge.className = "stamp-badge";
        badge.innerHTML = `DAY<br>${day.day}`;

        const card = document.createElement("div");
        card.className = "day-card" + (idx === 0 ? " expanded" : "");

        const header = document.createElement("button");
        header.className = "day-header";
        header.type = "button";
        header.innerHTML = `<span>${escapeHtml(day.title)}</span><span class="arrow">&#9656;</span>`;
        header.addEventListener("click", () => card.classList.toggle("expanded"));

        const body = document.createElement("div");
        body.className = "day-body";
        let bodyHtml = `
            <p><strong>🌅 Morning:</strong> ${escapeHtml(day.morning)}</p>
            <p><strong>☀️ Afternoon:</strong> ${escapeHtml(day.afternoon)}</p>
            <p><strong>🌆 Evening:</strong> ${escapeHtml(day.evening)}</p>
        `;
        if (day.meal_suggestions && day.meal_suggestions.length) {
            bodyHtml += `<p><strong>🍴 Meal ideas:</strong> ${escapeHtml(day.meal_suggestions.join(", "))}</p>`;
        }
        if (day.notes) {
            bodyHtml += `<div class="day-note">${escapeHtml(day.notes)}</div>`;
        }
        body.innerHTML = bodyHtml;

        card.appendChild(header);
        card.appendChild(body);
        row.appendChild(badge);
        row.appendChild(card);
        container.appendChild(row);
    });
}

function renderTips(containerId, heading, tips) {
    const el = document.getElementById(containerId);
    if (!tips || !tips.length) { el.innerHTML = ""; return; }
    const items = tips.map(t => `<li>${escapeHtml(t)}</li>`).join("");
    el.innerHTML = `<h3>${heading}</h3><ul>${items}</ul>`;
}

function renderWeather(forecast) {
    const grid = document.getElementById("weatherGrid");
    const empty = document.getElementById("weatherEmpty");
    grid.innerHTML = "";

    if (!forecast || !forecast.length) {
        empty.classList.remove("hidden");
        return;
    }
    empty.classList.add("hidden");

    forecast.forEach(day => {
        const card = document.createElement("div");
        card.className = "weather-card";
        card.innerHTML = `
            <div class="weather-date">${day.date}</div>
            <div class="weather-temp">${Math.round(day.temp_max)}° / ${Math.round(day.temp_min)}°C</div>
            <div class="weather-desc">${escapeHtml(day.description)}</div>
            <div class="weather-precip">☔ ${day.precip_chance}%</div>
        `;
        grid.appendChild(card);
    });
}

function renderBudget(budget) {
    document.getElementById("budgetTotal").textContent = budget.total;

    const table = document.getElementById("budgetTable");
    let html = "<thead><tr><th>Category</th><th>Per day (group)</th><th>Total</th></tr></thead><tbody>";
    budget.table.forEach(row => {
        html += `<tr><td>${escapeHtml(row.Category)}</td><td>${escapeHtml(row["Per day (group)"])}</td><td>${escapeHtml(row.Total)}</td></tr>`;
    });
    html += "</tbody>";
    table.innerHTML = html;
}

function renderBookingLinks(links) {
    const container = document.getElementById("bookingLinks");
    container.innerHTML = "";
    links.forEach(link => {
        const a = document.createElement("a");
        a.className = "booking-link";
        a.href = link.url;
        a.target = "_blank";
        a.rel = "noopener";
        a.textContent = link.label;
        container.appendChild(a);
    });
}

function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    const div = document.createElement("div");
    div.textContent = String(str);
    return div.innerHTML;
}
