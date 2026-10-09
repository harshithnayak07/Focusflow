/* FocusFlow tasks: filters, groups on the staff, create, edit, delete. */

(function () {
    const groupsEl = document.getElementById("taskGroups");
    const emptyEl = document.getElementById("tasksEmpty");
    const emptyTitle = document.getElementById("tasksEmptyTitle");
    const emptyText = document.getElementById("tasksEmptyText");
    const emptyAction = document.getElementById("tasksEmptyAction");
    const sub = document.getElementById("tasksSub");

    const search = document.getElementById("taskSearch");
    const projectFilter = document.getElementById("taskProjectFilter");
    const statusButtons = Array.from(document.querySelectorAll(".seg [data-status]"));

    const modal = document.getElementById("taskModal");
    const form = document.getElementById("taskForm");
    const message = document.getElementById("taskMessage");
    const modalTitle = document.getElementById("taskModalTitle");
    const submit = document.getElementById("taskSubmit");
    const projectField = document.getElementById("taskProject");

    let tasks = [];
    let projects = [];
    let editingId = null;
    let emptyMode = "task";

    const filters = { search: "", project: "", status: "all" };

    /* ---------- helpers ---------- */

    function projectName(projectId) {
        const project = projects.find((item) => item.id === projectId);
        return project ? project.name : "No project";
    }

    function taskMarkup(task) {
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
            '<div class="q-body"><p class="q-name">' + escapeHtml(task.name) + "</p></div>" +
            '<div class="q-actions">' +
            '<button class="icon-btn" type="button" data-edit aria-label="Edit “' + escapeHtml(task.name) + '”">' +
            '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" ' +
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' +
            '<path d="M11.3 2.7a1.6 1.6 0 0 1 2.3 2.3L5.6 13 2.5 13.8l.8-3.1z"/></svg>' +
            "</button>" +
            '<button class="icon-btn danger" type="button" data-del aria-label="Delete “' +
            escapeHtml(task.name) + '”">' +
            '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" ' +
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' +
            '<path d="M2.8 4.3h10.4M6.4 4.3V2.9h3.2v1.4M4.2 4.3l.6 8.4h6.4l.6-8.4"/></svg>' +
            "</button></div></li>"
        );
    }

    function visibleTasks() {
        const needle = filters.search.trim().toLowerCase();
        return tasks.filter((task) => {
            if (filters.project && String(task.project_id) !== filters.project) return false;
            if (filters.status === "open" && task.is_completed) return false;
            if (filters.status === "done" && !task.is_completed) return false;
            if (needle && task.name.toLowerCase().indexOf(needle) === -1) return false;
            return true;
        });
    }

    function setEmpty(mode, title, text, action) {
        emptyMode = mode;
        emptyTitle.textContent = title;
        emptyText.textContent = text;
        emptyAction.textContent = action;
    }

    function render() {
        const shown = visibleTasks();
        const openCount = tasks.filter((task) => !task.is_completed).length;

        sub.textContent = tasks.length
            ? plural(tasks.length, "task", "tasks") + ", " + plural(openCount, "left to do", "left to do")
            : "Mark work done as you go.";

        const order = projects.map((project) => project.id);
        const buckets = [];

        shown.forEach((task) => {
            let bucket = buckets.find((item) => item.key === task.project_id);
            if (!bucket) {
                bucket = { key: task.project_id, items: [] };
                buckets.push(bucket);
            }
            bucket.items.push(task);
        });

        buckets.sort((a, b) => {
            const ai = order.indexOf(a.key);
            const bi = order.indexOf(b.key);
            return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
        });

        groupsEl.innerHTML = buckets
            .map((bucket) => {
                const done = bucket.items.filter((task) => task.is_completed).length;
                return (
                    '<section class="t-group">' +
                    '<div class="t-group-head">' +
                    "<h2>" + escapeHtml(projectName(bucket.key)) + "</h2>" +
                    '<span class="t-group-count">' + done + "/" + bucket.items.length + " done</span>" +
                    "</div>" +
                    '<ol class="queue">' + bucket.items.map(taskMarkup).join("") + "</ol>" +
                    "</section>"
                );
            })
            .join("");

        if (!projects.length) {
            setEmpty(
                "no-projects",
                "No projects yet.",
                "Tasks live inside a project, so create one first.",
                "Create a project"
            );
        } else if (!tasks.length) {
            setEmpty("task", "No tasks yet.", "Add a task and it shows up here.", "New task");
        } else if (!shown.length) {
            setEmpty("clear", "No tasks match.", "Clear the filters to see everything again.", "Clear filters");
        }

        emptyEl.hidden = shown.length > 0;
        groupsEl.hidden = shown.length === 0;
    }

    /* ---------- filters ---------- */

    function fillProjectOptions(select, withAll) {
        const current = select.value;
        select.innerHTML = "";
        if (withAll) {
            const all = document.createElement("option");
            all.value = "";
            all.textContent = "All projects";
            select.appendChild(all);
        }
        projects.forEach((project) => {
            const option = document.createElement("option");
            option.value = String(project.id);
            option.textContent = project.name;
            select.appendChild(option);
        });
        if (current) select.value = current;
    }

    search.addEventListener("input", () => {
        filters.search = search.value;
        render();
    });

    projectFilter.addEventListener("change", () => {
        filters.project = projectFilter.value;
        render();
    });

    statusButtons.forEach((button) => {
        button.addEventListener("click", () => {
            filters.status = button.dataset.status;
            statusButtons.forEach((other) => {
                other.setAttribute("aria-pressed", String(other === button));
            });
            render();
        });
    });

    emptyAction.addEventListener("click", () => {
        if (emptyMode === "no-projects") {
            window.location.href = "projects.html";
        } else if (emptyMode === "clear") {
            filters.search = "";
            filters.project = "";
            filters.status = "all";
            search.value = "";
            projectFilter.value = "";
            statusButtons.forEach((button) => {
                button.setAttribute("aria-pressed", String(button.dataset.status === "all"));
            });
            render();
        } else {
            openCreate();
        }
    });

    /* ---------- modal ---------- */

    function openCreate() {
        if (!projects.length) {
            window.location.href = "projects.html";
            return;
        }
        editingId = null;
        form.reset();
        message.textContent = "";
        projectField.closest(".field").querySelector(".field-hint")?.remove();
        projectField.disabled = false;
        fillProjectOptions(projectField, false);
        modalTitle.textContent = "New task";
        submit.textContent = "Add task";
        openModal("taskModal");
    }

    function openEdit(task) {
        editingId = task.id;
        form.reset();
        message.textContent = "";
        fillProjectOptions(projectField, false);
        projectField.value = String(task.project_id);
        projectField.disabled = true;
        let hint = projectField.closest(".field").querySelector(".field-hint");
        if (!hint) {
            hint = document.createElement("p");
            hint.className = "field-hint";
            projectField.closest(".field").appendChild(hint);
        }
        hint.textContent = "A task stays in the project it was created in.";
        document.getElementById("taskName").value = task.name;
        modalTitle.textContent = "Edit task";
        submit.textContent = "Save changes";
        openModal("taskModal");
    }

    function close() {
        closeModal(modal);
    }

    document.getElementById("newTask").addEventListener("click", openCreate);
    modal.querySelector("[data-close]").addEventListener("click", close);

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        message.textContent = "";

        const name = document.getElementById("taskName").value.trim();
        if (!name) {
            message.textContent = "Write what needs doing.";
            return;
        }

        submit.disabled = true;
        try {
            if (editingId === null) {
                await API.createTask({
                    name: name,
                    project_id: Number(projectField.value)
                });
                toast("Task added.");
            } else {
                const task = tasks.find((item) => item.id === editingId);
                await API.updateTask(editingId, {
                    name: name,
                    is_completed: task ? task.is_completed : false
                });
                toast("Changes saved.");
            }
            form.reset();
            close();
            await load();
        } catch (error) {
            message.textContent = error.message;
        } finally {
            submit.disabled = false;
        }
    });

    /* ---------- row actions ---------- */

    groupsEl.addEventListener("change", async (event) => {
        const input = event.target.closest("[data-toggle]");
        if (!input) return;

        const id = Number(input.getAttribute("data-toggle"));
        const task = tasks.find((item) => item.id === id);
        if (!task) return;

        const next = input.checked;
        const item = input.closest(".q-item");
        item.classList.toggle("is-done", next);
        task.is_completed = next;

        try {
            await API.updateTask(id, { name: task.name, is_completed: next });
            toast(next ? "Task marked done." : "Task reopened.");
            render();
        } catch (error) {
            task.is_completed = !next;
            input.checked = !next;
            item.classList.toggle("is-done", !next);
            toast(error.message, "err");
        }
    });

    groupsEl.addEventListener("click", async (event) => {
        const row = event.target.closest(".q-item");
        if (!row) return;
        const id = Number(row.dataset.id);
        const task = tasks.find((item) => item.id === id);
        if (!task) return;

        if (event.target.closest("[data-edit]")) {
            openEdit(task);
            return;
        }

        if (event.target.closest("[data-del]")) {
            const goAhead = await confirmAction({
                title: "Delete “" + task.name + "”?",
                body: "This can't be undone.",
                confirmLabel: "Delete task"
            });
            if (!goAhead) return;
            try {
                await API.deleteTask(id);
                toast("Task deleted.");
                await load();
            } catch (error) {
                toast(error.message, "err");
            }
        }
    });

    /* ---------- boot ---------- */

    async function load() {
        try {
            const [taskData, projectData] = await Promise.all([API.tasks(), API.projects()]);
            tasks = taskData;
            projects = projectData;
            fillProjectOptions(projectFilter, true);
            render();
        } catch (error) {
            if (error.status === 401) return;
            toast(error.message, "err");
        }
    }

    load();
})();
