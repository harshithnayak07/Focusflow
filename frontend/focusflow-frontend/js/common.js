/* FocusFlow shared shell: auth guard, user badge, modals, toasts, confirms. */

function escapeHtml(value) {
    return String(value == null ? "" : value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function plural(count, one, many) {
    return count + " " + (count === 1 ? one : many);
}

/* ---------- toast ---------- */

function toast(message, kind) {
    const wrap = document.getElementById("toasts");
    if (!wrap) return;
    const item = document.createElement("div");
    item.className = "toast" + (kind === "err" ? " err" : "");
    item.textContent = message;
    wrap.appendChild(item);
    window.setTimeout(() => item.remove(), 3600);
}

/* ---------- modal ---------- */

let lastFocused = null;

function openModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    lastFocused = document.activeElement;
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
    const first = modal.querySelector("input, textarea, select, button");
    if (first) first.focus();
}

function closeModal(id) {
    const modal = typeof id === "string" ? document.getElementById(id) : id;
    if (!modal) return;
    modal.classList.remove("open");
    document.body.style.overflow = "";
    if (lastFocused && document.contains(lastFocused)) lastFocused.focus();
    lastFocused = null;
}

function openModals() {
    return Array.from(document.querySelectorAll(".modal.open"));
}

document.addEventListener("keydown", (event) => {
    const open = openModals();
    if (!open.length) return;
    const modal = open[open.length - 1];

    if (event.key === "Escape") {
        event.preventDefault();
        closeModal(modal);
        return;
    }

    if (event.key === "Tab") {
        const focusable = Array.from(
            modal.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])')
        ).filter((el) => el.offsetParent !== null);
        if (!focusable.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }
});

document.addEventListener("mousedown", (event) => {
    if (event.target.classList && event.target.classList.contains("modal")) {
        closeModal(event.target);
    }
});

/* ---------- confirm ---------- */

function confirmAction({ title, body, confirmLabel }) {
    return new Promise((resolve) => {
        const modal = document.createElement("div");
        modal.className = "modal open";
        modal.innerHTML =
            '<div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="confirmTitle">' +
            '<h2 id="confirmTitle">' + escapeHtml(title) + "</h2>" +
            '<p class="modal-text">' + escapeHtml(body) + "</p>" +
            '<div class="modal-actions">' +
            '<button type="button" class="btn btn-quiet" data-no>Cancel</button>' +
            '<button type="button" class="btn btn-danger" data-yes>' + escapeHtml(confirmLabel) + "</button>" +
            "</div></div>";
        document.body.appendChild(modal);
        document.body.style.overflow = "hidden";

        const finish = (result) => {
            modal.remove();
            document.body.style.overflow = "";
            resolve(result);
        };

        modal.querySelector("[data-no]").addEventListener("click", () => finish(false));
        modal.querySelector("[data-yes]").addEventListener("click", () => finish(true));
        modal.addEventListener("mousedown", (event) => {
            if (event.target === modal) finish(false);
        });
        modal.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                event.preventDefault();
                finish(false);
            }
        });
        modal.querySelector("[data-yes]").focus();
    });
}

/* ---------- shell boot ---------- */

(function bootNav() {
    const rail = document.querySelector(".rail");
    const toggle = document.querySelector("[data-nav-toggle]");
    const scrim = document.querySelector("[data-nav-scrim]");
    if (!rail || !toggle) return;

    function setOpen(open) {
        rail.classList.toggle("is-open", open);
        toggle.setAttribute("aria-expanded", String(open));
        if (scrim) {
            scrim.hidden = !open;
            scrim.classList.toggle("is-on", open);
        }
        document.body.style.overflow = open ? "hidden" : "";
    }

    toggle.addEventListener("click", () => {
        setOpen(!rail.classList.contains("is-open"));
    });
    if (scrim) {
        scrim.addEventListener("click", () => setOpen(false));
    }
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && rail.classList.contains("is-open")) {
            setOpen(false);
        }
    });
    rail.querySelectorAll("nav a").forEach((link) => {
        link.addEventListener("click", () => setOpen(false));
    });
})();

(function bootShell() {
    if (!document.querySelector(".rail")) return;

    if (!getToken()) {
        window.location.replace("login.html");
        return;
    }

    document.querySelectorAll("[data-logout]").forEach((button) => {
        button.addEventListener("click", () => {
            clearToken();
            window.location.href = "login.html";
        });
    });

    API.me()
        .then((user) => {
            document.querySelectorAll("[data-user-name]").forEach((el) => {
                el.textContent = user.name;
            });
            if (user.role === "admin") {
                const adminLink = document.getElementById("navAdmin");
                if (adminLink) adminLink.hidden = false;
                document.querySelectorAll("[data-user-role]").forEach((el) => {
                    el.hidden = false;
                });
            }
            document.dispatchEvent(new CustomEvent("ff:user", { detail: user }));
        })
        .catch((error) => {
            if (error.status !== 401) toast(error.message, "err");
        });
})();
