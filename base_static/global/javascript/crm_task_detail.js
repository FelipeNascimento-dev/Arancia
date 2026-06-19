document.addEventListener("DOMContentLoaded", function () {
    const config = document.getElementById("crm-task-detail-sections");
    if (!config) return;

    const tabUrl = config.dataset.tabUrl || "";
    const activeSection = config.dataset.activeSection || "";
    const loadedSections = new Set();
    const loadingSections = new Set();

    document.querySelectorAll(".crm-task-section[data-loaded='1']").forEach((section) => {
        const name = section.dataset.section;
        if (name) loadedSections.add(name);
    });

    function loadSection(sectionName, panel) {
        if (!panel || !tabUrl || loadedSections.has(sectionName) || loadingSections.has(sectionName)) {
            return;
        }

        loadingSections.add(sectionName);
        panel.innerHTML = '<div class="tab-loading">Carregando...</div>';

        fetch(tabUrl + "?tab=" + encodeURIComponent(sectionName), {
            headers: { Accept: "application/json" },
            credentials: "same-origin",
        })
            .then((response) => response.json().then((payload) => ({ ok: response.ok, payload })))
            .then(({ ok, payload }) => {
                if (!ok || !payload.ok) {
                    panel.innerHTML = '<div class="tab-loading">Não foi possível carregar esta seção.</div>';
                    return;
                }
                panel.innerHTML = payload.html || "";
                loadedSections.add(sectionName);
                const section = panel.closest(".crm-task-section");
                if (section) section.dataset.loaded = "1";
            })
            .catch(() => {
                panel.innerHTML = '<div class="tab-loading">Erro ao carregar esta seção.</div>';
            })
            .finally(() => {
                loadingSections.delete(sectionName);
            });
    }

    function loadSectionByName(sectionName) {
        const section = document.querySelector('.crm-task-section[data-section="' + sectionName + '"]');
        if (!section || section.dataset.loaded === "1") return;
        const panel = section.querySelector(".section-panel");
        loadSection(sectionName, panel);
    }

    function initLazySections() {
        const pending = document.querySelectorAll('.crm-task-section[data-loaded="0"]');
        if (!pending.length) return;

        const hash = window.location.hash.replace("#", "");
        const priority = activeSection || hash;
        if (priority) {
            loadSectionByName(priority);
        }

        if (!("IntersectionObserver" in window)) {
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    const section = entry.target;
                    const name = section.dataset.section;
                    const panel = section.querySelector(".section-panel");
                    if (name && panel) {
                        loadSection(name, panel);
                    }
                    observer.unobserve(section);
                });
            },
            { rootMargin: "240px 0px", threshold: 0 }
        );

        pending.forEach((section) => observer.observe(section));
    }

    if (activeSection) {
        const target = document.getElementById(activeSection);
        if (target) {
            setTimeout(() => target.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
        }
    }

    initLazySections();

    const hash = window.location.hash.replace("#", "");
    if (hash && hash !== activeSection) {
        const el = document.getElementById(hash);
        if (el) {
            setTimeout(() => {
                el.scrollIntoView({ behavior: "smooth", block: "start" });
                loadSectionByName(hash);
            }, 200);
        }
    }
});
