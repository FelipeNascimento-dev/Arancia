(function () {
    function getCfg() {
        var el = document.getElementById("consulta-os-config");
        return el ? JSON.parse(el.textContent) : {};
    }

    var cfg = getCfg();

    function bindTravelModalButtons() {
        document.querySelectorAll(".open-travel-modal, .btn-show-travels").forEach(function (btn) {
            if (btn.dataset.travelModalBound === "1") return;
            btn.dataset.travelModalBound = "1";

            btn.addEventListener("click", function () {
                var orderNumber = btn.getAttribute("data-order-number") || "-";
                var modal = document.getElementById("travelModal");
                var modalTitle = document.getElementById("travelModalTitle");
                var modalList = document.getElementById("travelModalList");
                if (!modal || !modalList) return;

                modalTitle.textContent = "Viagens da OS " + orderNumber;
                modalList.innerHTML =
                    '<div class="results-loading"><div class="spinner"></div><span>Carregando viagens...</span></div>';
                modal.classList.add("is-open");

                var base = cfg.urls && cfg.urls.order_travels ? cfg.urls.order_travels : "";
                fetch(base + "?order_number=" + encodeURIComponent(orderNumber), {
                    headers: { Accept: "application/json" },
                    credentials: "same-origin",
                })
                    .then(function (r) {
                        return r.json();
                    })
                    .then(function (data) {
                        var travels = data.travels || [];
                        modalList.innerHTML = "";
                        if (!travels.length) {
                            modalList.innerHTML =
                                '<div class="travel-empty">Nenhuma viagem encontrada para esta OS.</div>';
                            return;
                        }
                        travels.forEach(function (travel) {
                            var row = document.createElement("div");
                            row.className = "travel-row";
                            row.innerHTML =
                                '<span class="travel-id">ID: ' +
                                (travel.id || "-") +
                                '</span><span class="travel-status">' +
                                (travel.status || "-") +
                                "</span>";
                            modalList.appendChild(row);
                        });
                    })
                    .catch(function () {
                        modalList.innerHTML =
                            '<div class="travel-empty">Erro ao carregar viagens.</div>';
                    });
            });
        });
    }

    function hideResultsOverlay() {
        var overlay = document.getElementById("resultsLoadingOverlay");
        if (overlay) overlay.classList.remove("is-active");
    }

    function showResultsError(message) {
        var content = document.getElementById("resultsContent");
        hideResultsOverlay();
        if (content) {
            content.innerHTML =
                '<div class="empty-state">' + (message || "Erro ao carregar resultados.") + "</div>";
        }
    }

    function loadResultsAsync() {
        if (!cfg.async_list_load) return;

        var content = document.getElementById("resultsContent");
        var listUrl = cfg.urls && cfg.urls.list_results;
        if (!content || !listUrl) return;

        var params = new URLSearchParams(window.location.search);
        if (params.get("enviar_evento") !== "1") return;

        fetch(listUrl + "?" + params.toString(), {
            headers: {
                Accept: "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
            credentials: "same-origin",
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    if (!response.ok) {
                        throw new Error((data && data.detail) || "Falha ao consultar OS.");
                    }
                    return data;
                });
            })
            .then(function (data) {
                content.innerHTML = data.html || "";
                hideResultsOverlay();
                bindTravelModalButtons();
            })
            .catch(function (error) {
                showResultsError(error && error.message ? error.message : null);
            });
    }

    function initConsultaOsExtras() {
        bindTravelModalButtons();

        var closeBtn = document.getElementById("closeTravelModal");
        var travelModal = document.getElementById("travelModal");
        if (closeBtn && travelModal) {
            closeBtn.addEventListener("click", function () {
                travelModal.classList.remove("is-open");
            });
            travelModal.addEventListener("click", function (event) {
                if (event.target === travelModal) {
                    travelModal.classList.remove("is-open");
                }
            });
        }

        loadResultsAsync();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initConsultaOsExtras);
    } else {
        initConsultaOsExtras();
    }
})();
