document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modalCreateTask");
    if (!modal) return;

    function openModal() {
        modal.style.display = "block";
        if (window.CrmSearchSelect) {
            CrmSearchSelect.initAll(modal);
        }
    }

    function closeModal() {
        modal.style.display = "none";
    }

    window.openCreateTaskModal = openModal;

    document.querySelectorAll("[data-open-task-modal]").forEach((btn) => {
        btn.addEventListener("click", openModal);
    });

    document.querySelectorAll("[data-close-modal]").forEach((btn) => {
        btn.addEventListener("click", () => closeModal(btn.dataset.closeModal));
    });

    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    window.resetCreateTaskForm = function () {
        const form = document.getElementById("formCreateTask");
        if (!form) return;
        form.reset();
        if (window.CrmSearchSelect) {
            form.querySelectorAll("select.js-crm-search-select").forEach((select) => {
                select.dispatchEvent(new Event("change", { bubbles: true }));
            });
        }
    };

    if (window.CrmSearchSelect) {
        CrmSearchSelect.initAll(modal);
    }

    if (modal.dataset.showOnLoad === "true") {
        openModal();
    }
});
