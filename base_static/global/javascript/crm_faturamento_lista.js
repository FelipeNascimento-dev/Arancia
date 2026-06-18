document.addEventListener("DOMContentLoaded", function () {
    const configEl = document.getElementById("crm-billing-list-config");
    if (!configEl) return;

    let config = {};
    try {
        config = JSON.parse(configEl.textContent || "{}");
    } catch (e) {
        return;
    }

    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    const csrfToken = csrfInput ? csrfInput.value : "";
    let currentViewBillingId = null;
    let clients = [];
    let contracts = [];
    let lookupsLoaded = false;
    let lookupsLoading = null;

    function urlFor(key, id) {
        const pattern = (config.urls || {})[key] || "";
        return pattern.replace("{id}", String(id));
    }

    function openModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.style.display = "flex";
    }

    function closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.style.display = "none";
    }

    function setText(elementId, value) {
        const el = document.getElementById(elementId);
        if (el) el.textContent = value || "-";
    }

    function showFormError(message) {
        const el = document.getElementById("billingFormError");
        if (!el) return;
        if (message) {
            el.textContent = message;
            el.hidden = false;
        } else {
            el.textContent = "";
            el.hidden = true;
        }
    }

    function formatApiErrors(data) {
        if (!data) return "Erro ao salvar faturamento.";
        if (data.errors && typeof data.errors === "object") {
            const parts = [];
            Object.keys(data.errors).forEach((field) => {
                const messages = data.errors[field];
                if (Array.isArray(messages)) {
                    messages.forEach((msg) => parts.push(`${field}: ${msg}`));
                } else if (messages) {
                    parts.push(`${field}: ${messages}`);
                }
            });
            if (parts.length) {
                return parts.join("\n");
            }
        }
        return data.detail || data.message || "Erro ao salvar faturamento.";
    }

    function showBillingToast(message, level) {
        if (typeof Toastify === "undefined" || !message) return;
        const bg = level === "error" ? "#e74c3c" : "#2ecc71";
        Toastify({
            text: message,
            duration: 5000,
            gravity: "top",
            position: "right",
            backgroundColor: bg,
            stopOnFocus: true,
            close: true,
        }).showToast();
    }

    function redirectAfterSave(isUpdate) {
        const suffix = isUpdate ? "?updated=1" : "?created=1";
        window.location.href = window.location.pathname + suffix;
    }

    function ensureBillingLookups() {
        if (lookupsLoaded) {
            return Promise.resolve({ clients, contracts });
        }
        if (lookupsLoading) {
            return lookupsLoading;
        }
        const lookupsUrl = (config.urls || {}).lookups;
        if (!lookupsUrl) {
            return Promise.resolve({ clients: [], contracts: [] });
        }
        lookupsLoading = fetch(lookupsUrl, {
            headers: { Accept: "application/json" },
            credentials: "same-origin",
        })
            .then((response) => response.json().then((payload) => ({ ok: response.ok, payload })))
            .then(({ ok, payload }) => {
                if (!ok || !payload.ok) {
                    throw new Error(payload.detail || "Não foi possível carregar opções.");
                }
                clients = payload.clients || [];
                contracts = payload.contracts || [];
                lookupsLoaded = true;
                populateClientSelect();
                return { clients, contracts };
            })
            .finally(() => {
                lookupsLoading = null;
            });
        return lookupsLoading;
    }

    function populateClientSelect() {
        const selectEl = document.getElementById("billing_client_gai_id");
        if (!selectEl) return;
        const current = selectEl.value;
        selectEl.innerHTML = '<option value="">---------</option>';
        clients.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = String(item.id);
            opt.textContent = item.label || String(item.id);
            selectEl.appendChild(opt);
        });
        if (current) {
            selectEl.value = current;
        }
    }

    function contractsForGai(gaiId) {
        if (!gaiId) return contracts;
        const gaiKey = String(gaiId);
        return contracts.filter((item) => {
            const clientId = item.client_gai_id;
            return clientId === null || clientId === undefined || clientId === "" || String(clientId) === gaiKey;
        });
    }

    function refreshContractSelect(gaiId, selectedId) {
        const selectEl = document.getElementById("billing_contract_id");
        if (!selectEl) return;

        const current = selectedId !== undefined ? String(selectedId || "") : selectEl.value;
        let options = contractsForGai(gaiId);
        if (current && !options.some((item) => String(item.id) === current)) {
            const fallback = contracts.find((item) => String(item.id) === current);
            if (fallback) {
                options = [fallback, ...options];
            }
        }
        selectEl.innerHTML = '<option value="">---------</option>';
        options.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = String(item.id);
            opt.textContent = item.label || String(item.id);
            selectEl.appendChild(opt);
        });
        if (current && options.some((item) => String(item.id) === current)) {
            selectEl.value = current;
        } else {
            selectEl.value = "";
        }
    }

    function populateBillingForm(data) {
        const formData = data || {};
        document.getElementById("billingFormId").value = formData.id || "";
        document.getElementById("billing_client_gai_id").value = formData.client_gai_id || "";
        refreshContractSelect(formData.client_gai_id, formData.contract_id || "");
        document.getElementById("billing_referencia").value = formData.referencia || "";
        document.getElementById("billing_valor").value = formData.valor || "";
        document.getElementById("billing_data_vencimento").value = formData.data_vencimento || "";
        document.getElementById("billing_status").value = formData.status || "";
        document.getElementById("billing_observacoes").value = formData.observacoes || "";
        showFormError("");
    }

    function collectBillingFormData() {
        return {
            client_gai_id: document.getElementById("billing_client_gai_id").value,
            contract_id: document.getElementById("billing_contract_id").value,
            referencia: document.getElementById("billing_referencia").value,
            valor: document.getElementById("billing_valor").value,
            data_vencimento: document.getElementById("billing_data_vencimento").value,
            status: document.getElementById("billing_status").value,
            observacoes: document.getElementById("billing_observacoes").value,
        };
    }

    window.openCreateBillingModal = function () {
        ensureBillingLookups()
            .then(() => {
                populateBillingForm({});
                document.getElementById("modalFormBillingTitle").innerHTML =
                    '<i class="fa-solid fa-plus"></i> Novo Faturamento';
                openModal("modalFormBilling");
            })
            .catch((err) => showBillingToast(err.message || "Erro ao carregar opções.", "error"));
    };

    window.resetBillingForm = function () {
        const billingId = document.getElementById("billingFormId").value;
        if (billingId) {
            openEditBillingModal(billingId);
        } else {
            populateBillingForm({});
        }
    };

    function fillViewBilling(item) {
        currentViewBillingId = item.id;
        setText("viewBillingReferencia", item.display_referencia);
        setText("viewBillingCliente", item.display_customer);
        setText("viewBillingPeriodStart", item.display_period_start);
        setText("viewBillingPeriodEnd", item.display_period_end);
        setText("viewBillingPlanned", item.display_planned_amount);
        setText("viewBillingActual", item.display_actual_amount);
        setText("viewBillingValor", item.display_valor);
        setText("viewBillingVencimento", item.display_vencimento);
        setText("viewBillingStatus", item.display_status);
        setText("viewBillingObservacoes", item.display_observacoes);

        const contractEl = document.getElementById("viewBillingContrato");
        if (contractEl) {
            contractEl.textContent = item.display_contract || "-";
        }

        const contractBtn = document.getElementById("btnOpenContractFromView");
        if (contractBtn) {
            if (item.display_contract_id) {
                contractBtn.href = urlFor("contract_detail", item.display_contract_id);
                contractBtn.hidden = false;
            } else {
                contractBtn.hidden = true;
            }
        }
    }

    function openViewBilling(billingId) {
        openModal("modalViewBilling");
        fillViewBilling({ id: billingId });

        fetch(urlFor("get", billingId), {
            headers: { Accept: "application/json" },
            credentials: "same-origin",
        })
            .then((response) => response.json().then((payload) => ({ ok: response.ok, payload })))
            .then(({ ok, payload }) => {
                if (!ok || !payload.ok) {
                    const message = payload.detail || "Não foi possível carregar o faturamento.";
                    showBillingToast(message, "error");
                    closeModal("modalViewBilling");
                    return;
                }
                const item = payload.billing || {};
                item.id = billingId;
                fillViewBilling(item);
            })
            .catch(() => {
                showBillingToast("Erro ao carregar faturamento.", "error");
                closeModal("modalViewBilling");
            });
    }

    function openEditBillingModal(billingId) {
        closeModal("modalViewBilling");
        showFormError("");
        document.getElementById("modalFormBillingTitle").innerHTML =
            '<i class="fa-solid fa-pencil"></i> Editar Faturamento';
        openModal("modalFormBilling");

        Promise.all([
            ensureBillingLookups(),
            fetch(urlFor("get", billingId), {
                headers: { Accept: "application/json" },
                credentials: "same-origin",
            }).then((response) => response.json().then((payload) => ({ ok: response.ok, payload }))),
        ])
            .then(([, billingResult]) => {
                const { ok, payload } = billingResult;
                if (!ok || !payload.ok) {
                    const message = payload.detail || "Não foi possível carregar o faturamento.";
                    showFormError(message);
                    showBillingToast(message, "error");
                    return;
                }
                const formData = payload.form || {};
                formData.id = billingId;
                populateBillingForm(formData);
            })
            .catch(() => {
                const message = "Erro ao carregar faturamento.";
                showFormError(message);
                showBillingToast(message, "error");
            });
    }

    document.querySelectorAll(".btn-view-billing").forEach((btn) => {
        btn.addEventListener("click", () => openViewBilling(btn.dataset.billingId));
    });

    document.querySelectorAll(".btn-edit-billing").forEach((btn) => {
        btn.addEventListener("click", () => openEditBillingModal(btn.dataset.billingId));
    });

    const editFromViewBtn = document.getElementById("btnOpenEditBillingFromView");
    if (editFromViewBtn) {
        editFromViewBtn.addEventListener("click", () => {
            if (currentViewBillingId) {
                openEditBillingModal(currentViewBillingId);
            }
        });
    }

    const clientSelect = document.getElementById("billing_client_gai_id");
    if (clientSelect) {
        clientSelect.addEventListener("change", () => {
            refreshContractSelect(clientSelect.value);
        });
    }

    const billingForm = document.getElementById("formBilling");
    if (billingForm) {
        billingForm.addEventListener("submit", (event) => {
            event.preventDefault();
            showFormError("");

            const billingId = document.getElementById("billingFormId").value;
            const payload = collectBillingFormData();
            const url = billingId ? urlFor("update", billingId) : urlFor("create", "");
            const createUrl = (config.urls || {}).create || "";
            const targetUrl = billingId ? url : createUrl;

            fetch(targetUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                    "X-CSRFToken": csrfToken,
                },
                credentials: "same-origin",
                body: JSON.stringify(payload),
            })
                .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
                .then(({ ok, data }) => {
                    if (!ok || !data.ok) {
                        showFormError(formatApiErrors(data));
                        showBillingToast(formatApiErrors(data), "error");
                        return;
                    }
                    closeModal("modalFormBilling");
                    showBillingToast(
                        data.message || (billingId ? "Faturamento atualizado com sucesso!" : "Faturamento criado com sucesso!"),
                        "success",
                    );
                    setTimeout(() => redirectAfterSave(Boolean(billingId)), 500);
                })
                .catch(() => {
                    const message = "Erro ao salvar faturamento.";
                    showFormError(message);
                    showBillingToast(message, "error");
                });
        });
    }

    document.querySelectorAll("[data-close-modal]").forEach((btn) => {
        btn.addEventListener("click", () => closeModal(btn.dataset.closeModal));
    });

    window.addEventListener("click", function (event) {
        document.querySelectorAll(".modal").forEach((modal) => {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    });
});
