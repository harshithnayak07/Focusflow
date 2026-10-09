/* FocusFlow sign in and account creation. */

(function () {
    const message = document.getElementById("formMessage");
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    function fail(text) {
        message.textContent = text;
    }

    function busy(form, isBusy) {
        const button = form.querySelector('button[type="submit"]');
        button.disabled = isBusy;
        button.textContent = isBusy ? "Working…" : button.dataset.label || button.textContent;
    }

    if (loginForm) {
        const submit = loginForm.querySelector('button[type="submit"]');
        submit.dataset.label = "Sign in";

        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            message.textContent = "";

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;

            if (!email || !password) {
                fail("Enter your email and password.");
                return;
            }

            busy(loginForm, true);
            try {
                const data = await API.login(email, password);
                setToken(data.access_token);
                window.location.href = "dashboard.html";
            } catch (error) {
                fail(error.message);
                busy(loginForm, false);
            }
        });
    }

    if (registerForm) {
        const submit = registerForm.querySelector('button[type="submit"]');
        submit.dataset.label = "Create account";

        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            message.textContent = "";

            const name = document.getElementById("name").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const password2 = document.getElementById("password2").value;

            if (!name || !email) {
                fail("Fill in your name and email.");
                return;
            }
            if (password.length < 8) {
                fail("Use a password of at least 8 characters.");
                return;
            }
            if (password !== password2) {
                fail("The two passwords don't match.");
                return;
            }

            busy(registerForm, true);
            try {
                await API.register({ name: name, email: email, password: password });
                window.location.href = "login.html";
            } catch (error) {
                fail(error.message);
                busy(registerForm, false);
            }
        });
    }
})();
