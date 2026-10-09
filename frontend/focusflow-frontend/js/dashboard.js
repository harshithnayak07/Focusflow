/* FocusFlow dashboard: the staff, the queue, the projects. */

(function () {
    const queueEl = document.getElementById("queue");
    const queueEmpty = document.getElementById("queueEmpty");
    const dashProjects = document.getElementById("dashProjects");
    const projectsEmpty = document.getElementById("projectsEmpty");

    let projects = [];
    let tasks = [];

    function projectName(projectId) {
        const project = projects.find((item) => item.id === projectId);
        return project ? project.name : "No project";
    }

    /* ---------- gauge ---------- */

    function paintGauge() {
        const total = tasks.length;
        const done = tasks.filter((task) => task.is_completed).length;
        const percent = total ? Math.round((done / total) * 100) : 0;

        document.getElementById("gaugeFill").style.width = percent + "%";
        const marker = document.getElementById("gaugeMarker");
        if (marker) marker.style.left = percent + "%";
        document.getElementById("gaugeValue").textContent = percent + "%";
        document.getElementById("gauge").setAttribute(
            "aria-label",
            done + " of " + total + " tasks done, " + percent + " percent"
        );

        const note = document.getElementById("gaugeNote");
        if (!total) {
            note.textContent = "No tasks yet. Add one to start tracking.";
        } else {
            note.innerHTML =
                "<b>" + done + " of " + total + "</b> tasks done across " +
                plural(projects.length, "project", "projects") + ".";
        }
    }

    /* ---------- queue ---------- */

    function queueMarkup(task) {
        const done = task.is_completed;
        const label = done
            ? "Mark “" + task.name + "” as not done"
            : "Mark “" + task.name + "” as done";

        return (
            '<li class="q-item' + (done ? " is-done" : "") + '" data-id="' + task.id + '">' +
            '<label class="q-check">' +
            '<input type="checkbox" data-toggle="' + task.id + '"' + (done ? " checked" : "") +
            ' aria-label="' + escapeHtml(label) + '">' +
            '<span class="q-mark" aria-hidden="true">' +
            '<svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" ' +
            'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">' +
            '<path d="M3 8.4l3.3 3.3L13 4.9"/></svg>' +
            "</span></label>" +
            '<div class="q-body">' +
            '<p class="q-name">' + escapeHtml(task.name) + "</p>" +
            '<p class="q-meta">' + escapeHtml(projectName(task.project_id)) + "</p>" +
            "</div></li>"
        );
    }

    function paintQueue() {
        const open = tasks.filter((task) => !task.is_completed);
        const finished = tasks.filter((task) => task.is_completed);
        const ordered = open.concat(finished);

        queueEl.innerHTML = ordered.map(queueMarkup).join("");
        queueEl.hidden = ordered.length === 0;
        queueEmpty.hidden = ordered.length > 0;

        if (!ordered.length) {
            document.getElementById("queueEmptyTitle").textContent = tasks.length
                ? "All caught up."
                : "Nothing open.";
            document.getElementById("queueEmptyText").textContent = tasks.length
                ? "Every task you had is done."
                : "Add a task and it appears here.";
        }
    }

    /* ---------- projects ---------- */

    function paintProjects() {
        dashProjects.innerHTML = projects
            .map((project) => {
                const own = tasks.filter((task) => task.project_id === project.id);
                const done = own.filter((task) => task.is_completed).length;
                const percent = own.length ? Math.round((done / own.length) * 100) : 0;
                return (
                    '<div class="mini">' +
                    '<div class="mini-head">' +
                    '<span class="mini-name">' + escapeHtml(project.name) + "</span>" +
                    '<span class="mini-count">' + done + "/" + own.length + " done</span>" +
                    "</div>" +
                    '<div class="bar"><i style="width:' + percent + '%"></i></div>' +
                    "</div>"
                );
            })
            .join("");

        dashProjects.hidden = projects.length === 0;
        projectsEmpty.hidden = projects.length > 0;
    }

    /* ---------- interaction ---------- */

    queueEl.addEventListener("change", async (event) => {
        const input = event.target.closest("[data-toggle]");
        if (!input) return;

        const id = Number(input.getAttribute("data-toggle"));
        const task = tasks.find((item) => item.id === id);
        if (!task) return;

        const next = input.checked;
        const item = input.closest(".q-item");

        item.classList.toggle("is-done", next);
        task.is_completed = next;
        paintGauge();

        try {
            await API.updateTask(id, { name: task.name, is_completed: next });
            toast(next ? "Task marked done." : "Task reopened.");
            paintQueue();
        } catch (error) {
            task.is_completed = !next;
            input.checked = !next;
            item.classList.toggle("is-done", !next);
            paintGauge();
            toast(error.message, "err");
        }
    });

    /* ---------- boot ---------- */

    function paintGreeting() {
        const hour = new Date().getHours();
        const part = hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
        const name = document.querySelector("[data-user-name]");
        const who = name && name.textContent !== "Signed in" ? name.textContent.split(" ")[0] : "";
        document.getElementById("greeting").textContent =
            "Good " + part + (who ? ", " + who + "." : ".");
        document.getElementById("todayLine").textContent = new Date().toLocaleDateString(undefined, {
            weekday: "long",
            day: "numeric",
            month: "long"
        });
    }

    document.addEventListener("ff:user", paintGreeting);

    (async function load() {
        paintGreeting();
        try {
            const [projectData, taskData] = await Promise.all([API.projects(), API.tasks()]);
            projects = projectData;
            tasks = taskData;
            paintGauge();
            paintQueue();
            paintProjects();
        } catch (error) {
            if (error.status === 401) return;
            toast(error.message, "err");
            document.getElementById("gaugeNote").textContent = "Nothing loaded yet.";
        }
    })();
})();
