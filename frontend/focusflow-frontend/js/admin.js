/* FocusFlow admin: accounts list. */

(async function () {
    const notice = document.getElementById("adminNotice");
    const panel = document.getElementById("adminPanel");
    const table = document.getElementById("userTable");

    let me = null;
    let users = [];

    function render() {
        table.innerHTML = users
            .map((user) => {
                const own = me && user.id === me.id;
                return (
                    "<tr>" +
                    '<td class="cell-name">' + escapeHtml(user.name) + "</td>" +
                    '<td class="cell-email">' + escapeHtml(user.email) + "</td>" +
                    "<td>" +
                    '<span class="chip' + (user.role === "admin" ? " chip-admin" : "") + '">' +
                    escapeHtml(user.role) +
                    "</span></td>" +
                    "<td>" +
                    '<span class="chip">' + (user.is_active ? "Active" : "Inactive") + "</span>" +
                    "</td>" +
                    "<td>" +
                    '<button class="btn btn-quiet btn-sm" type="button" data-del="' + user.id + '"' +
                    (own ? " disabled title=\"You can't delete your own account.\"" : "") +
                    ">Delete</button>" +
                    "</td></tr>"
                );
            })
            .join("");
    }

    try {
        me = await API.me();
    } catch (error) {
        if (error.status === 401) return;
        notice.hidden = false;
        notice.querySelector(".empty-title").textContent = "We couldn't check your account.";
        notice.querySelector("p:not(.empty-title)").textContent = error.message;
        return;
    }

    if (me.role !== "admin") {
        notice.hidden = false;
        return;
    }

    panel.hidden = false;

    try {
        users = await API.users();
        render();
    } catch (error) {
        toast(error.message, "err");
    }

    table.addEventListener("click", async (event) => {
        const button = event.target.closest("[data-del]");
        if (!button || button.disabled) return;

        const id = Number(button.getAttribute("data-del"));
        const user = users.find((item) => item.id === id);
        if (!user) return;

        const goAhead = await confirmAction({
            title: "Delete “" + user.name + "”?",
            body: "Delete fails if they still have projects or tasks. This cannot be undone.",
            confirmLabel: "Delete account"
        });
        if (!goAhead) return;

        try {
            await API.deleteUser(id);
            toast("Account deleted.");
            users = await API.users();
            render();
        } catch (error) {
            toast(error.message, "err");
        }
    });
})();
