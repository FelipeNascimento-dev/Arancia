document.addEventListener("DOMContentLoaded", function () {
    const configEl = document.getElementById("crm-client-list-config");
    if (!configEl) return;

    let config = {};
    try {
        config = JSON.parse(configEl.textContent || "{}");
    } catch (e) {
        return;
    }

    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    const csrfToken = csrfInput ? csrfInput.value : "";

    function urlFor(key, id) {
        const pattern = (config.urls || {})[key] || "";
        return pattern.replace("{id}", String(id));
    }

    function openModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.style.display = "block";
    }

    function closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.style.display = "none";
    }

    window.openCreateClientModal = function () {
        openModal("modalCreateClient");
    };
    window.closeCreateClientModal = function () {
        closeModal("modalCreateClient");
    };
    window.resetCreateClientForm = function () {
        const form = document.getElementById("formCreateClient");
        if (form) form.reset();
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

    function setText(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value || "-";
    }

    function renderViewModal(client) {
        setText("viewClientGai", client.gai_id);
        setText("viewClientNome", client.nome);
        setText("viewClientRazao", client.razao_social);
        setText("viewClientCnpj", client.cnpj);
        setText("viewClientCanal", client.sales_channel);
        setText("viewClientIata", client.cod_iata);
        setText("viewClientEmail", client.email);
        setText("viewClientTelefone", client.telefone);
        setText("viewClientNotes", client.notes || "Sem observações.");

        const contactsBody = document.getElementById("viewClientContactsBody");
        const addressesBody = document.getElementById("viewClientAddressesBody");
        if (contactsBody) {
            const contacts = client.contacts || [];
            contactsBody.innerHTML = contacts.length
                ? contacts.map((c) => `
                    <tr>
                        <td>${escapeHtml(c.nome)}</td>
                        <td>${escapeHtml(c.email)}</td>
                        <td>${escapeHtml(c.telefone)}</td>
                        <td>${escapeHtml(c.cargo)}</td>
                    </tr>`).join("")
                : '<tr><td colspan="4" class="muted text-center">Nenhum contato cadastrado.</td></tr>';
        }
        if (addressesBody) {
            const addresses = client.addresses || [];
            addressesBody.innerHTML = addresses.length
                ? addresses.map((a) => `
                    <tr>
                        <td>${escapeHtml(a.logradouro)} ${escapeHtml(a.numero)}</td>
                        <td>${escapeHtml(a.cidade)}</td>
                        <td>${escapeHtml(a.uf)}</td>
                        <td>${escapeHtml(a.cep)}</td>
                    </tr>`).join("")
                : '<tr><td colspan="4" class="muted text-center">Nenhum endereço cadastrado.</td></tr>';
        }

        document.querySelectorAll("#modalViewClient .tab-btn").forEach((btn, idx) => {
            btn.classList.toggle("active", idx === 0);
        });
        document.querySelectorAll("#modalViewClient .tab-content").forEach((panel, idx) => {
            panel.classList.toggle("active", idx === 0);
        });
    }

    function fillEditForm(client) {
        const map = {
            edit_nome: client.nome,
            edit_razao_social: client.razao_social,
            edit_cnpj: client.cnpj,
            edit_email: client.email,
            edit_telefone: client.telefone,
            edit_sales_channel: client.sales_channel,
            edit_cod_iata: client.cod_iata,
            edit_notes: client.notes,
        };
        Object.entries(map).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) el.value = value || "";
        });
        document.getElementById("editClientGaiId").value = client.gai_id;
        document.getElementById("editClientError").hidden = true;
        document.getElementById("editClientError").textContent = "";
    }

    function escapeHtml(value) {
        return String(value || "-")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    async function fetchClient(gaiId) {
        const resp = await fetch(urlFor("get_client", gaiId), {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const data = await resp.json();
        if (!resp.ok || !data.ok) {
            throw new Error(data.detail || "Não foi possível carregar o cliente.");
        }
        return data.client;
    }

    function updateTableRow(client) {
        const row = document.querySelector(`tr[data-gai-id="${client.gai_id}"]`);
        if (!row) return;
        const cells = row.querySelectorAll("td");
        if (cells.length >= 5) {
            cells[1].textContent = client.nome || "-";
            cells[2].textContent = client.cnpj || "-";
            cells[3].textContent = client.sales_channel || "-";
            cells[4].textContent = client.cod_iata || "-";
        }
        row.dataset.clientName = client.nome || "";
    }

    document.querySelectorAll(".btn-view-client").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const gaiId = btn.dataset.gaiId;
            try {
                const client = await fetchClient(gaiId);
                renderViewModal(client);
                openModal("modalViewClient");
            } catch (err) {
                alert(err.message);
            }
        });
    });

    document.querySelectorAll(".btn-edit-client").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const gaiId = btn.dataset.gaiId;
            try {
                const client = await fetchClient(gaiId);
                fillEditForm(client);
                openModal("modalEditClient");
            } catch (err) {
                alert(err.message);
            }
        });
    });

    document.getElementById("btnOpenEditFromView")?.addEventListener("click", async () => {
        const gaiId = document.getElementById("viewClientGai")?.textContent;
        if (!gaiId || gaiId === "-") return;
        closeModal("modalViewClient");
        if (!config.perms?.change) return;
        try {
            const client = await fetchClient(gaiId);
            fillEditForm(client);
            openModal("modalEditClient");
        } catch (err) {
            alert(err.message);
        }
    });

    document.getElementById("formEditClient")?.addEventListener("submit", async (event) => {
        event.preventDefault();
        const gaiId = document.getElementById("editClientGaiId").value;
        const errorEl = document.getElementById("editClientError");
        const form = event.target;
        const payload = Object.fromEntries(new FormData(form).entries());

        try {
            const resp = await fetch(urlFor("update_client", gaiId), {
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
                errorEl.textContent = data.detail || "Erro ao salvar cliente.";
                errorEl.hidden = false;
                return;
            }
            updateTableRow(data.client);
            closeModal("modalEditClient");
        } catch (err) {
            errorEl.textContent = "Erro ao salvar cliente.";
            errorEl.hidden = false;
        }
    });

    let pendingDelete = null;

    document.querySelectorAll(".btn-delete-client").forEach((btn) => {
        btn.addEventListener("click", () => {
            pendingDelete = {
                gaiId: btn.dataset.gaiId,
                row: btn.closest("tr"),
                name: btn.dataset.clientName || btn.dataset.gaiId,
            };
            setText("deleteClientName", pendingDelete.name);
            setText("deleteClientGai", pendingDelete.gaiId);
            document.getElementById("deleteClientError").hidden = true;
            openModal("modalDeleteClient");
        });
    });

    document.getElementById("btnConfirmDeleteClient")?.addEventListener("click", async () => {
        if (!pendingDelete) return;
        const errorEl = document.getElementById("deleteClientError");
        try {
            const resp = await fetch(urlFor("delete_client", pendingDelete.gaiId), {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            const data = await resp.json();
            if (!resp.ok || !data.ok) {
                errorEl.textContent = data.detail || "Não foi possível desativar o cliente.";
                errorEl.hidden = false;
                return;
            }
            pendingDelete.row?.remove();
            pendingDelete = null;
            closeModal("modalDeleteClient");
        } catch (err) {
            errorEl.textContent = "Erro ao desativar cliente.";
            errorEl.hidden = false;
        }
    });

    document.querySelectorAll("#modalViewClient .tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const modal = document.getElementById("modalViewClient");
            modal.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
            modal.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(btn.dataset.tab)?.classList.add("active");
        });
    });

    if (config.open_client) {
        fetchClient(config.open_client)
            .then(renderViewModal)
            .then(() => openModal("modalViewClient"))
            .catch((err) => alert(err.message));
    } else if (config.open_edit && config.perms?.change) {
        fetchClient(config.open_edit)
            .then(fillEditForm)
            .then(() => openModal("modalEditClient"))
            .catch((err) => alert(err.message));
    }
});
