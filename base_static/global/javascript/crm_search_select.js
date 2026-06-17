/**
 * Transforma <select class="js-crm-search-select"> em campo pesquisável.
 */
(function (window) {
    "use strict";

    function normalizeText(value) {
        return String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }

    function enhanceSelect(select) {
        if (!select || select.dataset.crmSearchEnhanced === "1") {
            return;
        }
        const realOptions = Array.from(select.options).filter((option) => option.value !== "");
        if (!realOptions.length) {
            return;
        }
        select.dataset.crmSearchEnhanced = "1";

        const wrapper = document.createElement("div");
        wrapper.className = "crm-search-select";
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);

        const input = document.createElement("input");
        input.type = "text";
        input.className = "crm-search-select-input form-control";
        input.placeholder = select.dataset.searchPlaceholder || "Digite para pesquisar...";
        input.autocomplete = "off";
        wrapper.insertBefore(input, select);

        const list = document.createElement("div");
        list.className = "crm-search-select-list";
        wrapper.appendChild(list);

        select.classList.add("crm-search-select-native");
        select.tabIndex = -1;
        select.setAttribute("aria-hidden", "true");

        function optionsData() {
            return Array.from(select.options).map((option) => ({
                value: option.value,
                label: option.textContent.trim(),
            }));
        }

        function selectedLabel() {
            const selected = select.options[select.selectedIndex];
            return selected ? selected.textContent.trim() : "";
        }

        function renderList(filterText) {
            const search = normalizeText(filterText);
            list.innerHTML = "";
            const matches = optionsData().filter((item) => {
                if (!search) {
                    return true;
                }
                return normalizeText(item.label).includes(search);
            });

            if (!matches.length) {
                const empty = document.createElement("div");
                empty.className = "crm-search-select-empty";
                empty.textContent = "Nenhum resultado encontrado.";
                list.appendChild(empty);
                return;
            }

            matches.forEach((item) => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "crm-search-select-option";
                if (item.value === select.value) {
                    btn.classList.add("active");
                }
                btn.dataset.value = item.value;
                btn.textContent = item.label;
                btn.addEventListener("click", () => {
                    select.value = item.value;
                    input.value = item.label;
                    list.classList.remove("open");
                    select.dispatchEvent(new Event("change", { bubbles: true }));
                    renderList("");
                });
                list.appendChild(btn);
            });
        }

        function syncInputFromSelect() {
            input.value = selectedLabel();
        }

        input.addEventListener("focus", () => {
            list.classList.add("open");
            renderList(input.value);
        });

        input.addEventListener("input", () => {
            list.classList.add("open");
            if (input.value !== selectedLabel()) {
                select.value = "";
            }
            renderList(input.value);
        });

        input.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                list.classList.remove("open");
                syncInputFromSelect();
            }
        });

        document.addEventListener("click", (event) => {
            if (!wrapper.contains(event.target)) {
                list.classList.remove("open");
                syncInputFromSelect();
            }
        });

        select.addEventListener("change", syncInputFromSelect);
        syncInputFromSelect();
    }

    function initAll(root) {
        const scope = root || document;
        scope.querySelectorAll("select.js-crm-search-select").forEach(enhanceSelect);
    }

    window.CrmSearchSelect = {
        initAll,
        enhanceSelect,
    };

    document.addEventListener("DOMContentLoaded", () => initAll(document));
})(window);
