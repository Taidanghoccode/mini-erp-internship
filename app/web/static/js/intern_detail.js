function getInternIdFromPath() {
    const parts = window.location.pathname.split("/").filter(Boolean);
    return parseInt(parts[parts.length - 1], 10);
}

function openAssign() {
    document.getElementById("assignModal").style.display = "flex";
    loadProjectsToSelect();
}

function closeAssign() {
    document.getElementById("assignModal").style.display = "none";
}

async function loadProjectsToSelect() {
    const select = document.getElementById("assign-project-select");
    select.innerHTML = `<option>Loading...</option>`;

    try {
        const res = await fetch("/api/projects/");
        const data = await res.json();

        select.innerHTML = "";
        data.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.id;
            opt.textContent = p.title;
            select.appendChild(opt);
        });

        if (data.length === 0) {
            select.innerHTML = `<option value="">No projects</option>`;
        }
    } catch (e) {
        console.error(e);
        select.innerHTML = `<option value="">Error loading</option>`;
    }
}

async function assignProject() {
    const intern_id = getInternIdFromPath();
    const project_id = parseInt(document.getElementById("assign-project-select").value, 10);
    const role = document.getElementById("assign-role").value || "Member";

    if (!project_id) {
        alert("Please choose a project");
        return;
    }

    const res = await fetch("/api/intern-projects/assign", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            intern_id,
            project_id,
            role,
            user_id: 0
        })
    });

    const result = await res.json();

    if (!res.ok) {
        alert("❌ " + (result.error || "Assign failed"));
        return;
    }

    alert("✅ Assigned!");
    closeAssign();
    location.reload();
}
