/**
 * Oculta UUIDs e IDs longos na UI do CRM / Projetos.
 * IDs permanecem em data-attributes e campos hidden para AJAX.
 */
(function (global) {
    const UUID_RE =
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    const OPAQUE_MIN_LEN = 12;

    function isOpaqueId(value) {
        if (value === null || value === undefined || value === "") return false;
        const s = String(value).trim();
        if (UUID_RE.test(s)) return true;
        if (/^\d+$/.test(s) && s.length >= OPAQUE_MIN_LEN) return true;
        return s.length >= 24 && s.includes("-");
    }

    function shortRef(value, length) {
        const len = length || 8;
        if (value === null || value === undefined || value === "") return "";
        const s = String(value).trim();
        if (!isOpaqueId(s)) return s;
        return s.slice(0, len);
    }

    function displayLabel(value, fallback) {
        const fb = fallback === undefined ? "-" : fallback;
        if (value === null || value === undefined || value === "") return fb;
        if (isOpaqueId(value)) return fb;
        return String(value);
    }

    global.CrmIdDisplay = {
        isOpaqueId,
        shortRef,
        displayLabel,
    };
})(typeof window !== "undefined" ? window : globalThis);
