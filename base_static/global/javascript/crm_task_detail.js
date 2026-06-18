document.addEventListener("DOMContentLoaded", function () {
    const root = document.getElementById("crm-task-detail-tabs");
    if (!root) return;

    const tabUrl = root.dataset.tabUrl || "";
    const loadedTabs = new Set();

    root.querySelectorAll(".tab-panel[data-loaded='1']").forEach((panel) => {
        if (panel.dataset.tabName) {
            loadedTabs.add(panel.dataset.tabName);
        }
    });

    function activateTab(btn) {
        const panelId = btn.dataset.panel;
        const tabName = btn.dataset.tab;
        root.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
        root.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        const panel = document.getElementById(panelId);
        if (panel) {
            panel.classList.add("active");
        }
        if (tabName && !loadedTabs.has(tabName)) {
            loadTab(tabName, panel);
        }
        if (tabName && window.history && window.history.replaceState) {
            const url = new URL(window.location.href);
            url.searchParams.set("tab", tabName);
            window.history.replaceState({}, "", url.toString());
        }
    }

    function loadTab(tabName, panel) {
        if (!panel || !tabUrl) return;
        panel.innerHTML = '<div class="tab-loading">Carregando...</div>';

        fetch(tabUrl + "?tab=" + encodeURIComponent(tabName), {
            headers: { Accept: "application/json" },
            credentials: "same-origin",
        })
            .then((response) => response.json().then((payload) => ({ ok: response.ok, payload })))
            .then(({ ok, payload }) => {
                if (!ok || !payload.ok) {
                    panel.innerHTML = '<div class="tab-loading">Não foi possível carregar esta aba.</div>';
                    return;
                }
                panel.innerHTML = payload.html || "";
                panel.dataset.loaded = "1";
                loadedTabs.add(tabName);
            })
            .catch(() => {
                panel.innerHTML = '<div class="tab-loading">Erro ao carregar esta aba.</div>';
            });
    }

    root.querySelectorAll(".tab").forEach((btn) => {
        btn.addEventListener("click", () => activateTab(btn));
    });
});
