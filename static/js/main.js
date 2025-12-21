// main.js
// Minimal JS. Clean. Purposeful. No React-induced headaches.

document.addEventListener("DOMContentLoaded", () => {
    fadeInPage();
    attachFormValidation();
});

/* -----------------------------
   Page Load Animation
------------------------------ */
function fadeInPage() {
    document.body.style.opacity = 0;
    document.body.style.transition = "opacity 0.6s ease-in-out";

    setTimeout(() => {
        document.body.style.opacity = 1;
    }, 100);
}

/* -----------------------------
   Form Validation
------------------------------ */
function attachFormValidation() {
    const form = document.querySelector("form");
    if (!form) return;

    form.addEventListener("submit", (e) => {
        const inputs = form.querySelectorAll("input");
        let valid = true;

        inputs.forEach(input => {
            const value = Number(input.value);

            if (isNaN(value) || value < 0) {
                valid = false;
                input.style.border = "1px solid #ef4444";
            } else {
                input.style.border = "1px solid #1e293b";
            }
        });

        if (!valid) {
            e.preventDefault();
            showToast("Please enter valid numeric values.");
        }
    });
}

/* -----------------------------
   Toast Notification
------------------------------ */
function showToast(message) {
    let toast = document.createElement("div");
    toast.innerText = message;

    toast.style.position = "fixed";
    toast.style.bottom = "30px";
    toast.style.right = "30px";
    toast.style.background = "#020617";
    toast.style.color = "#e5e7eb";
    toast.style.padding = "12px 18px";
    toast.style.borderRadius = "8px";
    toast.style.border = "1px solid #38bdf8";
    toast.style.boxShadow = "0 0 20px rgba(56,189,248,0.2)";
    toast.style.zIndex = 1000;
    toast.style.opacity = 0;
    toast.style.transition = "opacity 0.4s ease";

    document.body.appendChild(toast);

    setTimeout(() => toast.style.opacity = 1, 50);
    setTimeout(() => {
        toast.style.opacity = 0;
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}
