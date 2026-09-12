// ==========================================
// TalentIQ AI Sidebar
// ==========================================

document.addEventListener("DOMContentLoaded", () => {

    const sidebar = document.querySelector(".sidebar");
    const toggle = document.getElementById("menu-toggle");

    if (!sidebar || !toggle) return;

    // Sidebar Toggle
    toggle.addEventListener("click", (e) => {

        e.preventDefault();

        if (window.innerWidth > 992) {

            sidebar.classList.toggle("collapsed");

        } else {

            sidebar.classList.toggle("mobile-open");

        }

    });

    // Close sidebar when clicking outside (Mobile)
    document.addEventListener("click", (e) => {

        if (window.innerWidth > 992) return;

        if (
            !sidebar.contains(e.target) &&
            !toggle.contains(e.target)
        ) {

            sidebar.classList.remove("mobile-open");

        }

    });

    // Automatically close mobile sidebar when resizing to desktop
    window.addEventListener("resize", () => {

        if (window.innerWidth > 992) {

            sidebar.classList.remove("mobile-open");

        }

    });

});