/**
 * CRM Comercial — modais e interações compartilhadas.
 */
(function (window) {
    "use strict";

    const modalStack = [];
    const BASE_Z_INDEX = 9999;

    function getModal(id) {
        return document.getElementById(id);
    }

    function getVisibleModals() {
        return modalStack
            .map((id) => getModal(id))
            .filter((modal) => modal && modal.style.display === "flex");
    }

    function syncModalLayers() {
        modalStack.forEach((id, index) => {
            const modal = getModal(id);
            if (!modal || modal.style.display !== "flex") return;
            modal.style.zIndex = String(BASE_Z_INDEX + index * 10);
            modal.classList.toggle("modal--stacked", index > 0);
        });
    }

    function openModal(id) {
        const modal = getModal(id);
        if (!modal) return;
        if (!modalStack.includes(id)) {
            modalStack.push(id);
        }
        modal.style.display = "flex";
        syncModalLayers();
    }

    function closeModal(id) {
        const modal = getModal(id);
        if (!modal) return;
        modal.style.display = "none";
        modal.classList.remove("modal--stacked");
        modal.style.zIndex = "";
        const index = modalStack.indexOf(id);
        if (index >= 0) {
            modalStack.splice(index, 1);
        }
        syncModalLayers();
    }

    function closeTopModal() {
        const visible = getVisibleModals();
        if (!visible.length) return;
        closeModal(visible[visible.length - 1].id);
    }

    function bindModalClose() {
        document.querySelectorAll("[data-close-modal]").forEach((btn) => {
            btn.addEventListener("click", () => closeModal(btn.dataset.closeModal));
        });
        window.addEventListener("click", (event) => {
            const visible = getVisibleModals();
            if (!visible.length) return;
            const topModal = visible[visible.length - 1];
            if (event.target === topModal) {
                closeModal(topModal.id);
            }
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                closeTopModal();
            }
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

    function showToast(message, level) {
        if (typeof Toastify === "undefined" || !message) return;
        const bg = level === "error" ? "#e74c3c" : "#2ecc71";
        Toastify({
            text: message,
            duration: 4000,
            gravity: "top",
            position: "right",
            backgroundColor: bg,
            stopOnFocus: true,
            close: true,
        }).showToast();
    }

    function updateColumnOrderNumbers(tbody) {
        tbody.querySelectorAll("tr[data-column-id]").forEach((row, index) => {
            const orderCell = row.querySelector("td");
            if (orderCell) orderCell.textContent = String(index + 1);
            row.dataset.position = String(index + 1);
        });
    }

    function bindColumnReorder() {
        const tbody = document.getElementById("columns-sortable");
        const saveBtn = document.getElementById("btnSaveColumnOrder");
        if (!tbody || !tbody.querySelector("[data-column-id]")) return;

        const reorderUrl = tbody.dataset.reorderUrl;
        const csrf = tbody.dataset.csrf;
        if (!reorderUrl) return;

        let dragEl = null;
        let savedOrder = [];

        function currentColumnIds() {
            return [...tbody.querySelectorAll("tr[data-column-id]")].map(
                (item) => item.dataset.columnId,
            );
        }

        function setSaveButtonDirty(isDirty) {
            if (!saveBtn) return;
            saveBtn.disabled = !isDirty;
            saveBtn.classList.toggle("btn-primary", isDirty);
            saveBtn.classList.toggle("btn-secondary", !isDirty);
            const statusEl = document.getElementById("columns-order-status");
            if (statusEl) {
                statusEl.textContent = isDirty
                    ? "Ordem alterada — clique em Salvar ordem."
                    : "Nenhuma alteração pendente.";
            }
        }

        function restoreOrder(order) {
            order.forEach((id) => {
                const row = tbody.querySelector(`tr[data-column-id="${id}"]`);
                if (row) tbody.appendChild(row);
            });
            updateColumnOrderNumbers(tbody);
        }

        function markDirtyIfChanged() {
            const changed = currentColumnIds().join("|") !== savedOrder.join("|");
            setSaveButtonDirty(changed);
            tbody.classList.toggle("columns-order-dirty", changed);
            return changed;
        }

        savedOrder = currentColumnIds();
        setSaveButtonDirty(false);

        function persistColumnOrder() {
            const ids = currentColumnIds();
            if (!ids.length) return Promise.resolve();

            if (saveBtn) {
                saveBtn.disabled = true;
                saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Salvando...';
            }

            return fetch(reorderUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrf,
                },
                body: JSON.stringify({ column_ids: ids }),
            })
                .then((response) => response.json().then((payload) => ({
                    ok: response.ok,
                    payload,
                })))
                .then(({ ok, payload }) => {
                    if (!ok || !payload.ok) {
                        throw new Error(payload.detail || "Não foi possível reordenar as colunas.");
                    }
                    savedOrder = ids.slice();
                    setSaveButtonDirty(false);
                    tbody.classList.remove("columns-order-dirty");
                    showToast("Ordem das colunas salva.", "success");
                    window.location.reload();
                })
                .catch((error) => {
                    showToast(error.message || "Erro ao reordenar colunas.", "error");
                    restoreOrder(savedOrder);
                    setSaveButtonDirty(false);
                })
                .finally(() => {
                    if (saveBtn) {
                        saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Salvar ordem';
                    }
                });
        }

        if (saveBtn) {
            saveBtn.addEventListener("click", () => {
                if (!markDirtyIfChanged()) return;
                persistColumnOrder();
            });
        }

        tbody.querySelectorAll("tr[data-column-id]").forEach((row) => {
            row.setAttribute("draggable", "true");

            row.addEventListener("dragstart", (event) => {
                if (event.target.closest(".btn-edit-column")) {
                    event.preventDefault();
                    return;
                }
                dragEl = row;
                row.classList.add("dragging");
                event.dataTransfer.effectAllowed = "move";
                event.dataTransfer.setData("text/plain", row.dataset.columnId || "");
            });

            row.addEventListener("dragend", () => {
                row.classList.remove("dragging");
                dragEl = null;
                updateColumnOrderNumbers(tbody);
                markDirtyIfChanged();
            });

            row.addEventListener("dragover", (event) => {
                event.preventDefault();
                event.dataTransfer.dropEffect = "move";
                const target = row;
                if (!dragEl || dragEl === target) return;
                const rect = target.getBoundingClientRect();
                const after = event.clientY - rect.top > rect.height / 2;
                tbody.insertBefore(dragEl, after ? target.nextSibling : target);
            });
        });

        tbody.addEventListener("dragover", (event) => {
            event.preventDefault();
            if (!dragEl) return;
            const rows = [...tbody.querySelectorAll("tr[data-column-id]")];
            const lastRow = rows[rows.length - 1];
            if (lastRow && dragEl !== lastRow && event.target === tbody) {
                tbody.appendChild(dragEl);
            }
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
