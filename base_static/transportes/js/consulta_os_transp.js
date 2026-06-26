(function () {
    function getCfg() {
        var el = document.getElementById("consulta-os-config");
        return el ? JSON.parse(el.textContent) : {};
    }
    var cfg = getCfg();
    function initConsultaOsExtras() {
        document.querySelectorAll(".btn-show-travels").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var orderNumber = btn.getAttribute("data-order-number") || "-";
                var modal = document.getElementById("travelModal");
                var modalTitle = document.getElementById("travelModalTitle");
                var modalList = document.getElementById("travelModalList");
                if (!modal || !modalList) return;
                modalTitle.textContent = "Viagens da OS " + orderNumber;
                modalList.innerHTML = '<div class="results-loading"><div class="spinner"></div><span>Carregando viagens...</span></div>';
                modal.classList.add("show");
                var base = cfg.urls && cfg.urls.order_travels ? cfg.urls.order_travels : "";
                fetch(base + "?order_number=" + encodeURIComponent(orderNumber), {
                    headers: { Accept: "application/json" },
                })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        var travels = data.travels || [];
                        modalList.innerHTML = "";
                        if (!travels.length) {
                            modalList.innerHTML = '<div class="travel-empty">Nenhuma viagem encontrada para esta OS.</div>';
                            return;
                        }
                        travels.forEach(function (travel) {
                            var row = document.createElement("div");
                            row.className = "travel-row";
                            row.innerHTML =
                                '<span class="travel-id">ID: ' + (travel.id || "-") +
                                '</span><span class="travel-status">' + (travel.status || "-") + "</span>";
                            modalList.appendChild(row);
                        });
                    })
                    .catch(function () {
                        modalList.innerHTML = '<div class="travel-empty">Erro ao carregar viagens.</div>';
                    });
            });
        });
        var closeBtn = document.getElementById("closeTravelModal");
        var travelModal = document.getElementById("travelModal");
        if (closeBtn && travelModal) {
            closeBtn.addEventListener("click", function () { travelModal.classList.remove("show"); });
        }
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initConsultaOsExtras);
    } else {
        initConsultaOsExtras();
    }
})();
