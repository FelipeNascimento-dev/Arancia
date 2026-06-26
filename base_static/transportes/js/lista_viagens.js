(function () {
    function getCfg() {
        var el = document.getElementById("lista-viagens-config");
        return el ? JSON.parse(el.textContent) : {};
    }
    var cfg = getCfg();
    function initListaViagens() {
        const toggleBtn = document.getElementById("toggleFilters");
        const sidebar = document.getElementById("filtersSidebar");
        const layout = document.getElementById("pageLayout");
        if (toggleBtn && sidebar && layout) {
            toggleBtn.addEventListener("click", function () {
                sidebar.classList.toggle("is-hidden");
                layout.classList.toggle("filters-hidden");
                const hidden = sidebar.classList.contains("is-hidden");
                this.innerHTML = hidden
                    ? '<i class="fa-solid fa-sliders"></i> Mostrar filtros <span class="filter-count">' + cfg.filtros_ativos + '</span>'
                    : '<i class="fa-solid fa-sliders"></i> Ocultar filtros <span class="filter-count">' + cfg.filtros_ativos + '</span>';
            });
        }

        const eventsModal = document.getElementById("travelEventsDetailModal");
        const eventsCloseBtn = document.getElementById("closeTravelEventsDetailModal");
        const content = document.getElementById("travelEventsModalContent");
        const title = document.getElementById("travelEventsModalTitle");
        const openButtons = document.querySelectorAll(".btn-open-events-modal");

        if (eventsModal && content && title) {

    function closeEventsModal() {
        eventsModal.classList.remove("show");
    }

    function safe(value) {
        if (value === null || value === undefined || value === "") return "-";
        return String(value);
    }

    function buildOccurrence(evento) {
        const nome = evento.evento_nome || (evento.evento && evento.evento.name) || "Evento";
        const descricao = evento.evento_descricao || (evento.evento && evento.evento.description) || evento.description || "-";
        const data = evento.created_at_formatada || evento.created_at || "-";
        const criadoPor = evento.created_by || "-";
        const lat = evento.location_lat || "-";
        const lng = evento.location_long || "-";
        const imgUrl = evento.img_url || "";
        const eventId = evento.id || "-";

        return `
            <div class="occurrence-item">
                <div class="occurrence-icon-wrap">
                    <div class="occurrence-icon">
                        <i class="fa-solid fa-check"></i>
                    </div>
                </div>

                <div class="occurrence-content">
                    <div class="occurrence-top">
                        <div class="occurrence-title-block">
                            <div class="occurrence-title">${safe(nome)}</div>
                            <div class="occurrence-subtitle">${safe(descricao)}</div>
                        </div>

                        <div class="occurrence-date">${safe(data)}</div>
                    </div>

                    <div class="occurrence-grid">
                        <div class="occurrence-field">
                            <strong>ID evento:</strong> ${safe(eventId)}
                        </div>

                        <div class="occurrence-field">
                            <strong>Criado por:</strong> ${safe(criadoPor)}
                        </div>

                        <div class="occurrence-field">
                            <strong>Latitude:</strong> ${safe(lat)}
                        </div>

                        <div class="occurrence-field">
                            <strong>Longitude:</strong> ${safe(lng)}
                        </div>
                    </div>

                    ${
                        imgUrl && imgUrl !== "string"
                            ? `
                            <div class="occurrence-img">
                                <strong>Imagem:</strong><br>
                                <a href="${imgUrl}" target="_blank">
                                    <img src="${imgUrl}" alt="Imagem do evento">
                                </a>
                            </div>
                            `
                            : ""
                    }
                </div>
            </div>
        `;
    }

    openButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const travelId = this.dataset.travelId;
            const targetId = this.dataset.eventsTarget;
            const jsonEl = document.getElementById(targetId);

            let events = [];

            console.log("travelId:", travelId);
            console.log("targetId:", targetId);
            console.log("jsonEl:", jsonEl);

            try {
                events = jsonEl ? JSON.parse(jsonEl.textContent.trim()) : [];
                console.log("Eventos carregados:", events);
            } catch (e) {
                console.error("Erro ao converter eventos:", e);
                events = [];
            }

            title.textContent = `Ocorrências da viagem ${travelId}`;

            if (!events.length) {
                content.innerHTML = `<div class="empty-events">Nenhuma ocorrência encontrada para esta viagem.</div>`;
            } else {
                content.innerHTML = `
                    <div class="occurrences-list">
                        ${events.map(buildOccurrence).join("")}
                    </div>
                `;
            }

            eventsModal.classList.add("show");
        });
    });

    if (eventsCloseBtn) {
        eventsCloseBtn.addEventListener("click", closeEventsModal);
    }

    eventsModal.addEventListener("click", function (e) {
        if (e.target === eventsModal) {
            closeEventsModal();
        }
    });

        }


        const driverModal = document.getElementById("driverAssignModal");
        const driverOpenBtn = document.getElementById("openDriverModalBtn");
        const driverCloseBtn = document.getElementById("closeDriverAssignModal");

        const selectedInputsBox = document.getElementById("driverSelectedTravelsInputs");
        const selectedText = document.getElementById("driverSelectedTravelsText");
        const selectedBox = document.getElementById("driverSelectedTravelsBox");

        const carrierSelect = document.getElementById("modal_carrier_id");
        const paSelect = document.getElementById("modal_pa_id");
        const paHidden = document.getElementById("modal_pa_hidden");
        const podeEscolherTransportadora = cfg.pode_escolher_transportadora;
        const paTravada = cfg.pa_travada;
        const input = document.getElementById("modal_driver_nome");
        const resultsBox = document.getElementById("modalDriverResults");
        const hiddenId = document.getElementById("modal_driver_id");

        if (driverModal && driverOpenBtn && driverCloseBtn && selectedInputsBox && selectedText && selectedBox) {

    function getSelectedTravelIds() {
        const checked = document.querySelectorAll(".card-select-checkbox:checked");
        const ids = [];

        checked.forEach((checkbox) => {
            if (checkbox.value && !ids.includes(checkbox.value)) {
                ids.push(checkbox.value);
            }
        });

        return ids;
    }

    function fillSelectedTravels(ids) {
        selectedInputsBox.innerHTML = "";

        ids.forEach((id) => {
            const inputHidden = document.createElement("input");
            inputHidden.type = "hidden";
            inputHidden.name = "travels_selecionadas";
            inputHidden.value = id;
            selectedInputsBox.appendChild(inputHidden);
        });

        if (ids.length) {
            selectedText.textContent = ids.join(", ");
            selectedBox.style.display = "block";
        } else {
            selectedText.textContent = "";
            selectedBox.style.display = "none";
        }
    }

    function limparResultados() {
        if (resultsBox) {
            resultsBox.innerHTML = "";
            resultsBox.style.display = "none";
        }
    }

    function getPaId() {
        if (paHidden && paHidden.value) {
            return paHidden.value;
        }
        return paSelect ? paSelect.value : "";
    }

    function podeBuscarMotorista() {
        return Boolean(getPaId());
    }

    function atualizarCampoMotorista() {
        if (!input) return;

        if (podeBuscarMotorista()) {
            input.disabled = false;
            input.placeholder = "Digite o nome do motorista...";
        } else {
            input.disabled = true;
            input.placeholder = "Selecione a PA primeiro...";
        }
    }

    function limparMotorista() {
        if (input) input.value = "";
        if (hiddenId) hiddenId.value = "";
        limparResultados();
    }

    function openModal() {
        const ids = getSelectedTravelIds();

        if (!ids.length) {
            alert("Selecione pelo menos uma viagem.");
            return;
        }

        fillSelectedTravels(ids);

        limparMotorista();

        if (carrierSelect) {
            carrierSelect.value = "";
        }

        if (paSelect && !paTravada) {
            paSelect.value = "";
        }

        atualizarCampoMotorista();

        driverModal.classList.add("show");
    }

    function closeModal() {
        driverModal.classList.remove("show");
    }

    driverOpenBtn.addEventListener("click", openModal);
    driverCloseBtn.addEventListener("click", closeModal);

    driverModal.addEventListener("click", function (e) {
        if (e.target === driverModal) {
            closeModal();
        }
    });

    if (carrierSelect && input) {
        carrierSelect.addEventListener("change", function () {
            limparMotorista();
            atualizarCampoMotorista();
            if (podeBuscarMotorista()) {
                input.focus();
            }
        });
    }

    if (paSelect && !paTravada) {
        paSelect.addEventListener("change", function () {
            limparMotorista();
            atualizarCampoMotorista();
            if (podeBuscarMotorista()) {
                input.focus();
            }
        });
    }

    if (paTravada) {
        atualizarCampoMotorista();
    }

    if (input && resultsBox && hiddenId && (!podeEscolherTransportadora || carrierSelect)) {

    let timeout = null;

    input.addEventListener("keyup", function () {
        const query = this.value.trim();
        const carrierId = carrierSelect ? carrierSelect.value : "";
        const paId = getPaId();

        clearTimeout(timeout);

        if (!podeBuscarMotorista()) {
            hiddenId.value = "";
            limparResultados();
            return;
        }

        if (query.length < 2) {
            hiddenId.value = "";
            limparResultados();
            return;
        }

        timeout = setTimeout(() => {
            let url = cfg.urls.buscar_motoristas + "?nome=" +
                encodeURIComponent(query) +
                "&gai_id=" +
                encodeURIComponent(paId);

            if (podeEscolherTransportadora && carrierId) {
                url += "&carrier_id=" + encodeURIComponent(carrierId);
            }

            fetch(url)
                .then(res => res.json())
                .then(data => {
                    resultsBox.innerHTML = "";

                    if (!data.items || !data.items.length) {
                        limparResultados();
                        return;
                    }

                    data.items.forEach(driver => {
                        const div = document.createElement("div");
                        div.classList.add("driver-item");
                        div.innerText = driver.name || "Motorista";

                        div.addEventListener("mousedown", function (e) {
                            e.preventDefault();

                            input.value = driver.name || "";
                            hiddenId.value = driver.uid || "";

                            limparResultados();
                        });

                        resultsBox.appendChild(div);
                    });

                    resultsBox.style.display = "block";
                })
                .catch(() => {
                    limparResultados();
                });
        }, 300);
    });

    input.addEventListener("input", function () {
        if (!this.value.trim()) {
            hiddenId.value = "";
            limparResultados();
        }
    });

    input.addEventListener("blur", function () {
        setTimeout(() => {
            if (!hiddenId.value) {
                input.value = "";
            }

            limparResultados();
        }, 150);
    });

    document.addEventListener("click", function (e) {
        if (!resultsBox.contains(e.target) && e.target !== input) {
            limparResultados();
        }
    });

    }

        }


        const modalEventosTravel = document.getElementById("modalEventosTravel");

        if (modalEventosTravel) {

    window.fecharModalEventosTravel = function () {
        modalEventosTravel.classList.remove("show");
    };

    modalEventosTravel.addEventListener("click", function (e) {
        if (e.target === modalEventosTravel) {
            fecharModalEventosTravel();
        }
    });

        }


const tiposPorClienteEl = document.getElementById("tipos-por-cliente");
    const statusPorTipoEl = document.getElementById("status-por-tipo");
    if (tiposPorClienteEl && statusPorTipoEl) {
    const tiposPorCliente = JSON.parse(tiposPorClienteEl.textContent);
    const statusPorTipo = JSON.parse(statusPorTipoEl.textContent);

    const clienteSelect = document.getElementById("id_cliente");
    const tipoServicoSelect = document.getElementById("id_tipo_servico");
    const statusSelect = document.getElementById("id_status_list");

    if (clienteSelect && tipoServicoSelect && statusSelect) {

    function preencherTipos(clienteId, tiposSelecionados = []) {
        tipoServicoSelect.innerHTML = "";
        statusSelect.innerHTML = "";

        const tipos = tiposPorCliente[clienteId] || [];
        const tiposJaAdicionados = new Set();

        tipos.forEach(item => {
            const itemId = String(item.id);
            if (tiposJaAdicionados.has(itemId)) return;
            tiposJaAdicionados.add(itemId);

            const option = document.createElement("option");
            option.value = itemId;
            option.textContent = item.description && item.description !== item.type
                ? `${item.type} - ${item.description}`
                : item.type;

            if (tiposSelecionados.includes(itemId)) {
                option.selected = true;
            }

            tipoServicoSelect.appendChild(option);
        });

        tipoServicoSelect.dispatchEvent(new CustomEvent("tipo:updated"));
    }

    function preencherStatus(tiposIds = [], statusesSelecionados = []) {
        statusSelect.innerHTML = "";

        const statusKeysAdicionados = new Set();

        tiposIds.forEach(tipoId => {
            const statuses = statusPorTipo[String(tipoId)] || [];

            statuses.forEach(item => {
                const itemId = String(item.id || "").trim();
                const itemType = String(item.type || "").trim();
                const itemDescription = String(item.description || "").trim();

                const label = itemDescription && itemDescription !== itemType
                    ? `${itemType} - ${itemDescription}`
                    : itemType;

                const uniqueKey = `${itemId}||${label.toLowerCase()}`;

                if (!itemId || statusKeysAdicionados.has(uniqueKey)) return;
                statusKeysAdicionados.add(uniqueKey);

                const option = document.createElement("option");
                option.value = itemId;
                option.textContent = label;

                if (statusesSelecionados.includes(itemId)) {
                    option.selected = true;
                }

                statusSelect.appendChild(option);
            });
        });

        statusSelect.dispatchEvent(new CustomEvent("status:updated"));
    }

    const clienteInicial = clienteSelect.value;
    const tiposIniciais = Array.from(tipoServicoSelect.selectedOptions).map(opt => opt.value);
    const statusesIniciais = Array.from(statusSelect.selectedOptions).map(opt => opt.value);

    if (clienteInicial) {
        preencherTipos(clienteInicial, tiposIniciais);
        preencherStatus(tiposIniciais, statusesIniciais);
    }

    clienteSelect.addEventListener("change", function () {
        preencherTipos(this.value, []);
        preencherStatus([], []);
    });

    tipoServicoSelect.addEventListener("change", function () {
        const tiposSelecionados = Array.from(this.selectedOptions).map(opt => opt.value);
        preencherStatus(tiposSelecionados, []);
    });

    }

    }


const filterDriverInput = document.getElementById("id_driver_nome");
    const filterDriverResults = document.getElementById("driverResults");
    const filterDriverHiddenId = document.getElementById("id_driver_id");
    const filterCarrierSelect = document.getElementById("id_transportadora");

    if (filterDriverInput && filterDriverResults && filterDriverHiddenId) {

    let timeout = null;

    function limparResultados() {
        filterDriverResults.innerHTML = "";
        filterDriverResults.style.display = "none";
    }

    filterDriverInput.addEventListener("keyup", function () {
        const query = this.value.trim();
        const carrierId = filterCarrierSelect ? filterCarrierSelect.value : "";

        clearTimeout(timeout);

        if (query.length < 2) {
            filterDriverHiddenId.value = "";
            limparResultados();
            return;
        }

        timeout = setTimeout(() => {
            const url = cfg.urls.buscar_motoristas + "?nome=" +
                encodeURIComponent(query) +
                "&carrier_id=" +
                encodeURIComponent(carrierId);

            fetch(url)
                .then(res => res.json())
                .then(data => {
                    console.log("Motoristas retornados:", data);
                    filterDriverResults.innerHTML = "";

                    if (!data.items || !data.items.length) {
                        limparResultados();
                        return;
                    }

                    data.items.forEach(driver => {
                        const div = document.createElement("div");
                        div.classList.add("driver-item");
                        div.innerText = driver.name || "Motorista";

                        div.addEventListener("mousedown", function (e) {
                            e.preventDefault();
                            filterDriverInput.value = driver.name || "";
                            filterDriverHiddenId.value = driver.uid || "";
                            console.log("UID selecionado:", filterDriverHiddenId.value);
                            limparResultados();
                        });

                        filterDriverResults.appendChild(div);
                    });

                    filterDriverResults.style.display = "block";
                })
                .catch((err) => {
                    console.error("Erro ao buscar motoristas:", err);
                    limparResultados();
                });
        }, 300);
    });

    filterDriverInput.addEventListener("input", function () {
        if (!this.value.trim()) {
            filterDriverHiddenId.value = "";
            limparResultados();
        }
    });

    filterDriverInput.addEventListener("blur", function () {
        setTimeout(() => {
            if (!filterDriverHiddenId.value) {
                filterDriverInput.value = "";
            }
            limparResultados();
        }, 150);
    });

    if (filterCarrierSelect) {
        filterCarrierSelect.addEventListener("change", function () {
            filterDriverInput.value = "";
            filterDriverHiddenId.value = "";
            limparResultados();
        });
    }

    document.addEventListener("click", function (e) {
        if (!filterDriverResults.contains(e.target) && e.target !== filterDriverInput) {
            limparResultados();
        }
    });

    }


const checkboxes = document.querySelectorAll(".card-select-checkbox");
    const bulkBar = document.getElementById("bulkActionsBar");
    const countEl = document.getElementById("selectedCardsCount");
    const clearBtn = document.getElementById("clearCardSelection");

    function updateSelectedState() {
        let selectedCount = 0;

        checkboxes.forEach((checkbox) => {
            const card = checkbox.closest(".card");

            if (checkbox.checked) {
                selectedCount++;
                card?.classList.add("is-selected");
            } else {
                card?.classList.remove("is-selected");
            }
        });

        if (countEl) {
            countEl.textContent = selectedCount;
        }

        if (bulkBar) {
            bulkBar.classList.toggle("is-visible", selectedCount > 0);
        }
    }

    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", updateSelectedState);
    });

    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            checkboxes.forEach((checkbox) => {
                checkbox.checked = false;
            });
            updateSelectedState();
        });
    }

    updateSelectedState();


const printBtn = document.getElementById("printOsBtn");
    if (printBtn) {

    printBtn.addEventListener("click", function () {
        const checked = document.querySelectorAll(".card-select-checkbox:checked");
        const ids = [];

        checked.forEach((checkbox) => {
            if (checkbox.value && !ids.includes(checkbox.value)) {
                ids.push(checkbox.value);
            }
        });

        if (!ids.length) {
            alert("Selecione pelo menos uma viagem.");
            return;
        }

        const url = cfg.urls.imprimir_os + "?ids=" + ids.join(",") + "&auto=1";
        window.open(url, "_blank");
    });

    }


    // Visão cards/tabela: alternância server-side (links com view_mode na URL).

const eventTypeWrapper = document.getElementById("eventTypeSingleSearch");
    const eventTypeInput = document.getElementById("event_type_search_input");
    const eventTypeDropdown = document.getElementById("eventTypeDropdown");
    const eventTypeHiddenInput = document.getElementById("eventTypeId");

    if (eventTypeWrapper && eventTypeInput && eventTypeDropdown && eventTypeHiddenInput) {

    const items = Array.from(eventTypeDropdown.querySelectorAll(".single-search-item"));

    function openDropdown() {
        eventTypeWrapper.classList.add("is-open");
        filterItems(eventTypeInput.value);
    }

    function closeDropdown() {
        eventTypeWrapper.classList.remove("is-open");
    }

    function filterItems(term) {
        const value = (term || "").trim().toLowerCase();
        let visible = 0;

        items.forEach(item => {
            const haystack = (item.dataset.search || "").toLowerCase();
            const match = !value || haystack.includes(value);
            item.style.display = match ? "" : "none";
            if (match) visible++;
        });

        let emptyEl = eventTypeDropdown.querySelector(".single-search-empty-dynamic");

        if (!visible) {
            if (!emptyEl) {
                emptyEl = document.createElement("div");
                emptyEl.className = "single-search-empty single-search-empty-dynamic";
                emptyEl.textContent = "Nenhum tipo de evento encontrado";
                eventTypeDropdown.appendChild(emptyEl);
            }
        } else if (emptyEl) {
            emptyEl.remove();
        }
    }

    function selectItem(item) {
        eventTypeHiddenInput.value = item.dataset.value || "";
        eventTypeInput.value = item.dataset.label || "";

        items.forEach(opt => opt.classList.remove("is-selected"));
        item.classList.add("is-selected");

        closeDropdown();
    }

    eventTypeInput.addEventListener("focus", function () {
        openDropdown();
    });

    eventTypeInput.addEventListener("click", function () {
        openDropdown();
    });

    eventTypeInput.addEventListener("input", function () {
        eventTypeHiddenInput.value = "";
        items.forEach(opt => opt.classList.remove("is-selected"));
        openDropdown();
        filterItems(this.value);
    });

    items.forEach(item => {
        item.addEventListener("click", function () {
            selectItem(this);
        });
    });

    document.addEventListener("click", function (e) {
        if (!eventTypeWrapper.contains(e.target)) {
            closeDropdown();
        }
    });

    }


const statusSelectEl = document.getElementById("id_status_list");
    if (statusSelectEl) {

    const parent = statusSelectEl.parentNode;

    const wrapper = document.createElement("div");
    wrapper.className = "multi-search";

    const box = document.createElement("div");
    box.className = "multi-search-box";

    const chips = document.createElement("div");
    chips.className = "multi-chips-wrap";
    chips.style.display = "contents";

    const input = document.createElement("input");
    input.type = "text";
    input.className = "multi-search-input";
    input.placeholder = "Digite para buscar status...";

    const dropdown = document.createElement("div");
    dropdown.className = "multi-search-dropdown";

    parent.insertBefore(wrapper, statusSelectEl);
    wrapper.appendChild(box);
    box.appendChild(chips);
    box.appendChild(input);
    wrapper.appendChild(dropdown);
    wrapper.appendChild(statusSelectEl);

    statusSelectEl.style.display = "none";

    function normalizeText(value) {
        return String(value || "").trim().toLowerCase();
    }

    function dedupeNativeSelectOptions() {
        const seen = new Set();
        const selectedValues = new Set(
            Array.from(statusSelectEl.options)
                .filter(opt => opt.selected)
                .map(opt => String(opt.value))
        );

        const uniqueOptions = [];

        Array.from(statusSelectEl.options).forEach(opt => {
            const value = String(opt.value);
            const label = String(opt.textContent || "").trim();
            const key = `${value}||${normalizeText(label)}`;

            if (seen.has(key)) return;
            seen.add(key);

            uniqueOptions.push({
                value,
                label,
                selected: selectedValues.has(value),
            });
        });

        statusSelectEl.innerHTML = "";

        uniqueOptions.forEach(item => {
            const option = document.createElement("option");
            option.value = item.value;
            option.textContent = item.label;
            option.selected = item.selected;
            statusSelectEl.appendChild(option);
        });
    }

    function getOptions() {
        const added = new Set();

        return Array.from(statusSelectEl.options)
            .map(opt => ({
                value: String(opt.value),
                label: String(opt.textContent || "").trim(),
                selected: opt.selected
            }))
            .filter(item => {
                const key = `${item.value}||${normalizeText(item.label)}`;
                if (added.has(key)) return false;
                added.add(key);
                return true;
            });
    }

    function getSelected() {
        return getOptions().filter(item => item.selected);
    }

    function renderChips() {
        chips.innerHTML = "";

        getSelected().forEach(item => {
            const chip = document.createElement("span");
            chip.className = "multi-chip";
            chip.innerHTML = `
                <span>${item.label}</span>
                <button type="button" class="multi-chip-remove" data-value="${item.value}">&times;</button>
            `;
            chips.appendChild(chip);
        });
    }

    function renderDropdown(search = "") {
        const term = normalizeText(search);
        const options = getOptions().filter(item => {
            if (item.selected) return false;
            if (!term) return true;
            return normalizeText(item.label).includes(term);
        });

        dropdown.innerHTML = "";

        if (!options.length) {
            const empty = document.createElement("div");
            empty.className = "multi-search-empty";
            empty.textContent = "Nenhum status encontrado";
            dropdown.appendChild(empty);
            dropdown.style.display = "block";
            return;
        }

        options.forEach(item => {
            const row = document.createElement("div");
            row.className = "multi-search-item";
            row.textContent = item.label;

            row.addEventListener("click", function () {
                const option = Array.from(statusSelectEl.options).find(opt => String(opt.value) === item.value);
                if (!option) return;

                option.selected = true;
                input.value = "";
                dedupeNativeSelectOptions();
                renderChips();
                renderDropdown("");
                statusSelectEl.dispatchEvent(new Event("change", { bubbles: true }));
            });

            dropdown.appendChild(row);
        });

        dropdown.style.display = "block";
    }

    function closeDropdown() {
        dropdown.style.display = "none";
    }

    function refreshComponent() {
        dedupeNativeSelectOptions();
        renderChips();
        closeDropdown();
    }

    box.addEventListener("click", function () {
        input.focus();
        renderDropdown(input.value);
    });

    input.addEventListener("focus", function () {
        renderDropdown(input.value);
    });

    input.addEventListener("input", function () {
        renderDropdown(this.value);
    });

    input.addEventListener("keydown", function (e) {
        if (e.key === "Backspace" && !input.value.trim()) {
            const selected = getSelected();
            const last = selected[selected.length - 1];
            if (!last) return;

            const option = Array.from(statusSelectEl.options).find(opt => String(opt.value) === last.value);
            if (!option) return;

            option.selected = false;
            dedupeNativeSelectOptions();
            renderChips();
            renderDropdown(input.value);
            statusSelectEl.dispatchEvent(new Event("change", { bubbles: true }));
        }
    });

    chips.addEventListener("click", function (e) {
        const btn = e.target.closest(".multi-chip-remove");
        if (!btn) return;

        const value = btn.getAttribute("data-value");
        const option = Array.from(statusSelectEl.options).find(opt => String(opt.value) === String(value));
        if (!option) return;

        option.selected = false;
        dedupeNativeSelectOptions();
        renderChips();
        renderDropdown(input.value);
        statusSelectEl.dispatchEvent(new Event("change", { bubbles: true }));
    });

    statusSelectEl.addEventListener("status:updated", refreshComponent);

    document.addEventListener("click", function (e) {
        if (!wrapper.contains(e.target)) {
            closeDropdown();
        }
    });

    refreshComponent();

    }


const table = document.getElementById("travelsSortableTable");
    const tableClearBtn = document.getElementById("clearTableSort");

    if (table) {

    const tbody = table.querySelector("tbody");
    const sortButtons = Array.from(table.querySelectorAll(".sort-btn"));

    let originalRows = Array.from(tbody.querySelectorAll("tr"));
    let sortStack = [];

    function normalizeText(value) {
        return String(value || "")
            .trim()
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    function parseNumber(value) {
        const clean = String(value || "")
            .replace(/[^\d,.-]/g, "")
            .replace(",", ".");

        const number = Number(clean);

        return Number.isNaN(number) ? 0 : number;
    }

    function parseDate(value) {
        if (!value) return 0;

        const direct = Date.parse(value);
        if (!Number.isNaN(direct)) return direct;

        const match = String(value).match(/^(\d{2})\/(\d{2})\/(\d{4})(?:\s+(\d{2}):(\d{2}))?/);

        if (!match) return 0;

        const day = Number(match[1]);
        const month = Number(match[2]) - 1;
        const year = Number(match[3]);
        const hour = Number(match[4] || 0);
        const minute = Number(match[5] || 0);

        return new Date(year, month, day, hour, minute).getTime();
    }

    function getRowValue(row, key, type) {
        const value = row.dataset[`sort${key.charAt(0).toUpperCase()}${key.slice(1)}`];

        if (type === "number") {
            return parseNumber(value);
        }

        if (type === "date") {
            return parseDate(value);
        }

        return normalizeText(value);
    }

    function compareValues(a, b, type) {
        if (type === "text") {
            return a.localeCompare(b, "pt-BR");
        }

        return a - b;
    }

    function applySort() {
        let rows = Array.from(tbody.querySelectorAll("tr"));

        if (!sortStack.length) {
            tbody.innerHTML = "";
            originalRows.forEach(row => tbody.appendChild(row));
            updateHeaderState();
            return;
        }

        rows.sort(function (rowA, rowB) {
            for (const sort of sortStack) {
                const valueA = getRowValue(rowA, sort.key, sort.type);
                const valueB = getRowValue(rowB, sort.key, sort.type);

                let result = compareValues(valueA, valueB, sort.type);

                if (sort.direction === "desc") {
                    result = result * -1;
                }

                if (result !== 0) {
                    return result;
                }
            }

            return 0;
        });

        tbody.innerHTML = "";
        rows.forEach(row => tbody.appendChild(row));

        updateHeaderState();
    }

    function updateHeaderState() {
        sortButtons.forEach(button => {
            const key = button.dataset.sortKey;
            const icon = button.querySelector(".sort-icon");
            const priority = button.querySelector(".sort-priority");

            const index = sortStack.findIndex(item => item.key === key);

            button.classList.remove("is-active");

            if (icon) {
                icon.textContent = "↕";
            }

            if (priority) {
                priority.textContent = "";
            }

            if (index >= 0) {
                const sort = sortStack[index];

                button.classList.add("is-active");

                if (icon) {
                    icon.textContent = sort.direction === "asc" ? "↑" : "↓";
                }

                if (priority) {
                    priority.textContent = index + 1;
                }
            }
        });
    }

    function addOrToggleSort(button) {
        const key = button.dataset.sortKey;
        const type = button.dataset.sortType || "text";

        const existing = sortStack.find(item => item.key === key);

        if (existing) {
            existing.direction = existing.direction === "asc" ? "desc" : "asc";
        } else {
            sortStack.push({
                key: key,
                type: type,
                direction: "asc",
            });
        }

        applySort();
    }

    sortButtons.forEach(button => {
        button.addEventListener("click", function () {
            addOrToggleSort(this);
        });
    });

    if (tableClearBtn) {
        tableClearBtn.addEventListener("click", function () {
            sortStack = [];
            applySort();
        });
    }

    updateHeaderState();

    }
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initListaViagens);
    } else {
        initListaViagens();
    }
})();
