document.addEventListener("DOMContentLoaded", function () {
    const configEl = document.getElementById("crm-contract-list-config");
    if (!configEl) return;

    let config = {};
    try {
        config = JSON.parse(configEl.textContent || "{}");
    } catch (e) {
        return;
    }

    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    const csrfToken = csrfInput ? csrfInput.value : "";
    const serviceTypes = config.service_types || [];

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

    window.openCreateContractModal = function () {
        openModal("modalCreateContract");
    };
    window.resetCreateContractForm = function () {
        const form = document.getElementById("formCreateContract");
        if (form) {
            form.reset();
            refreshServiceTypeSelect(
                form.querySelector('[name="service_type_id"]'),
                form.querySelector('[name="client_gai_id"]')?.value,
            );
        }
    };

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

    function serviceTypesForGai(gaiId) {
        if (!gaiId) return serviceTypes;
        const gaiKey = String(gaiId);
        return serviceTypes.filter((item) => {
            const clientId = item.client_id;
            return clientId === null || clientId === undefined || clientId === "" || String(clientId) === gaiKey;
        });
    }

    function refreshServiceTypeSelect(selectEl, gaiId, selectedId) {
        if (!selectEl) return;
        const current = selectedId !== undefined ? String(selectedId || "") : selectEl.value;
        const options = serviceTypesForGai(gaiId);
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

    function bindGaiServiceTypeFilter(gaiSelect, serviceSelect) {
        if (!gaiSelect || !serviceSelect) return;
        gaiSelect.addEventListener("change", () => {
            refreshServiceTypeSelect(serviceSelect, gaiSelect.value);
        });
        refreshServiceTypeSelect(serviceSelect, gaiSelect.value);
    }

    const createForm = document.getElementById("formCreateContract");
    if (createForm) {
        bindGaiServiceTypeFilter(
            createForm.querySelector('[name="client_gai_id"]'),
            createForm.querySelector('[name="service_type_id"]'),
        );
    }

    const editGaiSelect = document.getElementById("edit_client_gai_id");
    const editServiceSelect = document.getElementById("edit_service_type_id");
    if (editGaiSelect && editServiceSelect) {
        bindGaiServiceTypeFilter(editGaiSelect, editServiceSelect);
        populateClientSelect(editGaiSelect);
    }

    function populateClientSelect(selectEl) {
        const createSelect = createForm?.querySelector('[name="client_gai_id"]');
        if (!selectEl || !createSelect) return;
        selectEl.innerHTML = createSelect.innerHTML;
    }

    function setText(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value || "-";
    }

    function renderViewModal(contract) {
        setText("viewContractId", contract.id);
        setText("viewContractNumero", contract.numero);
        setText("viewContractTitulo", contract.titulo);
        setText("viewContractCliente", contract.display_customer);
        setText("viewContractServiceType", contract.display_service_type);
        setText("viewContractStatus", contract.status);
        setText("viewContractInicio", contract.data_inicio);
        setText("viewContractFim", contract.data_fim);
        setText("viewContractValor", contract.valor);
        setText("viewContractDescricao", contract.descricao || "Sem descrição.");

        const detailBtn = document.getElementById("btnOpenDetailFromView");
        if (detailBtn) {
            detailBtn.href = urlFor("detail_contract", contract.id);
        }
    }

    function fillEditForm(contract) {
        document.getElementById("editContractId").value = contract.id;
        document.getElementById("edit_client_gai_id").value = contract.client_gai_id || "";
        document.getElementById("edit_titulo").value = contract.titulo || "";
        document.getElementById("edit_numero").value = contract.numero || "";
        document.getElementById("edit_status").value = contract.status || "";
        document.getElementById("edit_data_inicio").value = normalizeDateInput(contract.data_inicio);
        document.getElementById("edit_data_fim").value = normalizeDateInput(contract.data_fim);
        document.getElementById("edit_valor").value = contract.valor || "";
        document.getElementById("edit_descricao").value = contract.descricao || "";
        refreshServiceTypeSelect(
            editServiceSelect,
            contract.client_gai_id,
            contract.service_type_id,
        );
        document.getElementById("editContractError").hidden = true;
        document.getElementById("editContractError").textContent = "";
    }

    function normalizeDateInput(value) {
        if (!value) return "";
        return String(value).slice(0, 10);
    }

    async function fetchContract(contractId) {
        const resp = await fetch(urlFor("get_contract", contractId), {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const data = await resp.json();
        if (!resp.ok || !data.ok) {
            throw new Error(data.detail || "Não foi possível carregar o contrato.");
        }
        return data.contract;
    }

    function updateTableRow(contract) {
        const row = document.querySelector(`tr[data-contract-id="${contract.id}"]`);
        if (!row) return;
        const cells = row.querySelectorAll("td");
        if (cells.length >= 9) {
            cells[1].textContent = contract.numero || "-";
            cells[2].textContent = contract.titulo || "-";
            cells[3].textContent = contract.display_customer || "-";
            cells[4].textContent = contract.display_service_type || "-";
            cells[5].textContent = contract.data_inicio || "-";
            cells[6].textContent = contract.data_fim || "-";
            cells[7].textContent = contract.valor || "-";
            cells[8].innerHTML = `<span class="tag">${contract.status || "-"}</span>`;
        }
    }

    document.querySelectorAll(".btn-view-contract").forEach((btn) => {
        btn.addEventListener("click", async () => {
            try {
                const contract = await fetchContract(btn.dataset.contractId);
                renderViewModal(contract);
                openModal("modalViewContract");
            } catch (err) {
                alert(err.message);
            }
        });
    });

    document.querySelectorAll(".btn-edit-contract").forEach((btn) => {
        btn.addEventListener("click", async () => {
            try {
                const contract = await fetchContract(btn.dataset.contractId);
                fillEditForm(contract);
                openModal("modalEditContract");
            } catch (err) {
                alert(err.message);
            }
        });
    });

    document.getElementById("btnOpenEditContractFromView")?.addEventListener("click", async () => {
        const contractId = document.getElementById("viewContractId")?.textContent;
        if (!contractId || contractId === "-") return;
        closeModal("modalViewContract");
        if (!config.perms?.change) return;
        try {
            const contract = await fetchContract(contractId);
            fillEditForm(contract);
            openModal("modalEditContract");
        } catch (err) {
            alert(err.message);
        }
    });

    document.getElementById("formEditContract")?.addEventListener("submit", async (event) => {
        event.preventDefault();
        const contractId = document.getElementById("editContractId").value;
        const errorEl = document.getElementById("editContractError");
        const form = event.target;
        const payload = Object.fromEntries(new FormData(form).entries());

        try {
            const resp = await fetch(urlFor("update_contract", contractId), {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });
            const data = await resp.json();
            if (!resp.ok || !data.ok) {
                errorEl.textContent = data.detail || "Erro ao salvar contrato.";
                errorEl.hidden = false;
                return;
            }
            updateTableRow(data.contract);
            closeModal("modalEditContract");
        } catch (err) {
            errorEl.textContent = "Erro ao salvar contrato.";
            errorEl.hidden = false;
        }
    });

    if (config.open_contract) {
        fetchContract(config.open_contract)
            .then(renderViewModal)
            .then(() => openModal("modalViewContract"))
            .catch((err) => alert(err.message));
    } else if (config.open_edit && config.perms?.change) {
        fetchContract(config.open_edit)
            .then(fillEditForm)
            .then(() => openModal("modalEditContract"))
            .catch((err) => alert(err.message));
    }
});
