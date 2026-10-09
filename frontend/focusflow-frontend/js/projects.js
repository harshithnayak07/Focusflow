/* FocusFlow projects: list, create, edit, delete. */

(function () {
    const list = document.getElementById("projectList");
    const empty = document.getElementById("projectsEmpty");
    const sub = document.getElementById("projectsSub");
    const modal = document.getElementById("projectModal");
    const form = document.getElementById("projectForm");
    const message = document.getElementById("projectMessage");
    const modalTitle = document.getElementById("projectModalTitle");
    const submit = document.getElementById("projectSubmit");

    let projects = [];
    let tasks = [];
    let editingId = null;

    /* ---------- render ---------- */

    function rowMarkup(project) {
        const own = tasks.filter((task) => task.project_id === project.id);
        const done = own.filter((task) => task.is_completed).length;
        const percent = own.length ? Math.round((done / own.length) * 100) : 0;

        return (
            '<li class="p-row" data-id="' + project.id + '">' +
            '<div class="p-main">' +
            '<h3 class="p-name">' + escapeHtml(project.name) + "</h3>" +
            '<p class="p-desc">' +
            escapeHtml(project.description || "No description.") +
            "</p></div>" +
            '<div class="p-stat">' +
            '<div class="bar"><i style="width:' + percent + '%"></i></div>' +
            '<span class="p-count">' + (own.length
                ? done + " of " + own.length + " tasks done"
                : "No tasks yet") +
            "</span></div>" +
            '<div class="row-actions">' +
            '<button class="btn btn-quiet btn-sm" type="button" data-edit>Edit</button>' +
            '<button class="btn btn-quiet btn-sm" type="button" data-del>Delete</button>' +
            "</div></li>"
        );
    }

    function render() {
        list.innerHTML = projects.map(rowMarkup).join("");
        list.hidden = projects.length === 0;
        empty.hidden = projects.length > 0;
        sub.textContent = projects.length
            ? plural(projects.length, "project", "projects") + ", " +
            plural(tasks.length, "task", "tasks")
            : "Everything you are working on.";
    }

    async function load() {
        try {
            const [projectData, taskData] = await Promise.all([API.projects(), API.tasks()]);
            projects = projectData;
            tasks = taskData;
            render();
        } catch (error) {
            if (error.status === 401) return;
            toast(error.message, "err");
        }
    }

    /* ---------- modal ---------- */

    function openCreate() {
        editingId = null;
        form.reset();
        message.textContent = "";
        modalTitle.textContent = "New project";
        submit.textContent = "Create project";
        openModal("projectModal");
    }

    function openEdit(project) {
        editingId = project.id;
        form.reset();
        message.textContent = "";
        document.getElementById("projectName").value = project.name;
        document.getElementById("projectDescription").value = project.description || "";
        modalTitle.textContent = "Edit project";
        submit.textContent = "Save changes";
        openModal("projectModal");
    }

    function close() {
        closeModal(modal);
    }

    document.getElementById("newProject").addEventListener("click", openCreate);
    empty.querySelector("[data-new-project]").addEventListener("click", openCreate);
    modal.querySelector("[data-close]").addEventListener("click", close);

    /* ---------- submit ---------- */

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        message.textContent = "";

        const name = document.getElementById("projectName").value.trim();
        const description = document.getElementById("projectDescription").value.trim();

        if (!name) {
            message.textContent = "Give the project a name.";
            return;
        }

        submit.disabled = true;
        try {
            if (editingId === null) {
                await API.createProject({ name: name, description: description || null });
                toast("Project created.");
            } else {
                await API.updateProject(editingId, { name: name, description: description || null });
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

    list.addEventListener("click", async (event) => {
        const row = event.target.closest(".p-row");
        if (!row) return;
        const id = Number(row.dataset.id);
        const project = projects.find((item) => item.id === id);
        if (!project) return;

        if (event.target.closest("[data-edit]")) {
            openEdit(project);
            return;
        }

        if (event.target.closest("[data-del]")) {
            const own = tasks.filter((task) => task.project_id === id);
            const goAhead = await confirmAction({
                title: "Delete “" + project.name + "”?",
                body: own.length
                    ? "Its " + plural(own.length, "task", "tasks") + " are deleted with it. This can't be undone."
                    : "This can't be undone.",
                confirmLabel: "Delete project"
            });
            if (!goAhead) return;

            try {
                for (const task of own) {
                    await API.deleteTask(task.id);
                }
                await API.deleteProject(id);
                toast("Project deleted.");
                await load();
            } catch (error) {
                toast(error.message, "err");
            }
        }
    });

    load();
})();
