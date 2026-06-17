/**
 * CRM Comercial — modais e interações compartilhadas.
 */
(function (window) {
    "use strict";

    function openModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.style.display = "block";
    }

    function closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.style.display = "none";
    }

    function bindModalClose() {
        document.querySelectorAll("[data-close-modal]").forEach((btn) => {
            btn.addEventListener("click", () => closeModal(btn.dataset.closeModal));
        });
        window.addEventListener("click", (event) => {
            document.querySelectorAll(".modal").forEach((modal) => {
                if (event.target === modal) {
                    modal.style.display = "none";
                }
            });
        });
    }

    function bindGrantTypeToggle() {
        const typeSelect = document.getElementById("grant_type");
        if (!typeSelect) return;
        const groups = {
            user: document.querySelector('[name="user_id"]')?.closest(".form-group"),
            designation: document.querySelector('[name="designation_id"]')?.closest(".form-group"),
            customer_gai: document.querySelector('[name="customer_gai_id"]')?.closest(".form-group"),
            group: document.querySelector('[name="group_id"]')?.closest(".form-group"),
        };
        function sync() {
            const selected = typeSelect.value;
            Object.keys(groups).forEach((key) => {
                if (groups[key]) {
                    groups[key].style.display = key === selected ? "block" : "none";
                }
            });
        }
        typeSelect.addEventListener("change", sync);
        sync();
    }

    function bindColumnEdit() {
        const editForm = document.getElementById("formEditColumn");
        if (!editForm) return;

        document.querySelectorAll(".btn-edit-column").forEach((btn) => {
            btn.addEventListener("click", () => {
                const row = btn.closest("tr[data-column-id]");
                if (!row) return;
                editForm.querySelector('[name="column_id"]').value = row.dataset.columnId || "";
                const nameInput = editForm.querySelector('[name="name"]');
                if (nameInput) nameInput.value = row.dataset.name || "";
                const statusSelect = editForm.querySelector('[name="status_task_id"]');
                if (statusSelect && row.dataset.statusId) {
                    statusSelect.value = row.dataset.statusId;
                }
                const positionInput = editForm.querySelector('[name="position"]');
                if (positionInput) {
                    positionInput.value = row.dataset.position || "";
                }
                openModal("modalEditColumn");
            });
        });
    }

    function bindColumnReorder() {
        const tbody = document.getElementById("columns-sortable");
        if (!tbody || !tbody.querySelector("[data-column-id]")) return;

        const reorderUrl = tbody.dataset.reorderUrl;
        const csrf = tbody.dataset.csrf;
        if (!reorderUrl) return;

        let dragEl = null;
        tbody.querySelectorAll("tr[data-column-id]").forEach((row) => {
            row.setAttribute("draggable", "true");
            row.addEventListener("dragstart", () => {
                dragEl = row;
                row.classList.add("dragging");
            });
            row.addEventListener("dragend", () => {
                row.classList.remove("dragging");
                const ids = [...tbody.querySelectorAll("tr[data-column-id]")].map(
                    (item) => item.dataset.columnId,
                );
                fetch(reorderUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrf,
                    },
                    body: JSON.stringify({ column_ids: ids }),
                }).catch(() => {});
            });
            row.addEventListener("dragover", (event) => {
                event.preventDefault();
                const target = row;
                if (!dragEl || dragEl === target) return;
                const rect = target.getBoundingClientRect();
                const after = event.clientY - rect.top > rect.height / 2;
                tbody.insertBefore(dragEl, after ? target.nextSibling : target);
            });
        });
    }

    function bindAccessRemoveConfirm() {
        document.querySelectorAll(".btn-remove-access").forEach((btn) => {
            btn.addEventListener("click", (event) => {
                event.preventDefault();
                const form = btn.closest("form");
                if (!form) return;
                const target = btn.dataset.targetLabel || "este acesso";
                if (window.confirm(`Remover ${target}?`)) {
                    form.submit();
                }
            });
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        bindModalClose();
        bindGrantTypeToggle();
        bindColumnEdit();
        bindColumnReorder();
        bindAccessRemoveConfirm();
    });

    window.CrmComercial = {
        openModal,
        closeModal,
    };
})(window);
