// =========================================================
// SIDEBAR MENU
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    const sidebarLinks = document.querySelectorAll(".sidebar-menu a");

    sidebarLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            sidebarLinks.forEach(function (item) {
                item.classList.remove("active");
            });

            this.classList.add("active");
        });

    });


    // =====================================================
    // CONFIRM DELETE
    // =====================================================

    const deleteButtons = document.querySelectorAll(
        ".delete-btn"
    );

    deleteButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const confirmed = confirm(
                "Are you sure you want to delete this record?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    // =====================================================
    // CONFIRM ACTION
    // =====================================================

    const confirmButtons = document.querySelectorAll(
        ".confirm-btn"
    );

    confirmButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const message =
                this.dataset.message ||
                "Are you sure you want to continue?";

            const confirmed = confirm(message);

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    // =====================================================
    // AUTO HIDE MESSAGES
    // =====================================================

    const messages = document.querySelectorAll(
        ".message"
    );

    if (messages.length > 0) {

        setTimeout(function () {

            messages.forEach(function (message) {

                message.style.transition = "opacity 0.5s ease";

                message.style.opacity = "0";

                setTimeout(function () {
                    message.remove();
                }, 500);

            });

        }, 4000);
    }


    // =====================================================
    // FORM SUBMIT BUTTON
    // =====================================================

    const forms = document.querySelectorAll(
        "form"
    );

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton =
                form.querySelector(
                    'button[type="submit"]'
                );

            if (submitButton) {

                submitButton.disabled = true;

                submitButton.dataset.originalText =
                    submitButton.innerText;

                submitButton.innerText =
                    "Please wait...";

            }

        });

    });

});