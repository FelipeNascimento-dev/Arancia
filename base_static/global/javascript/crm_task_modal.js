/**
 * Modal de criação de task — editor rich text (CKEditor 5), igual ao mural.
 */
(function (window) {
    "use strict";

    const DESCRIPTION_ID = "taskCreateDescription";

    const EDITOR_TOOLBAR = [
        "heading",
        "|",
        "bold",
        "italic",
        "link",
        "bulletedList",
        "numberedList",
        "|",
        "blockQuote",
        "insertTable",
        "|",
        "undo",
        "redo",
    ];

    let descriptionEditor = null;
    let initPromise = null;

    function getDescriptionTextarea() {
        return document.getElementById(DESCRIPTION_ID);
    }

    function initDescriptionEditor() {
        if (initPromise) {
            return initPromise;
        }

        const textarea = getDescriptionTextarea();
        if (!textarea || typeof window.ClassicEditor === "undefined") {
            initPromise = Promise.resolve(null);
            return initPromise;
        }

        initPromise = window.ClassicEditor.create(textarea, {
            toolbar: EDITOR_TOOLBAR,
        })
            .then(function (editor) {
                descriptionEditor = editor;
                window.crmTaskDescriptionEditor = editor;
                return editor;
            })
            .catch(function (error) {
                console.error("Erro ao iniciar editor de descrição da task:", error);
                initPromise = null;
                return null;
            });

        return initPromise;
    }

    function syncEditorToTextarea() {
        const textarea = getDescriptionTextarea();
        if (descriptionEditor && textarea) {
            textarea.value = descriptionEditor.getData();
        }
    }

    function resetEditor() {
        if (descriptionEditor) {
            descriptionEditor.setData("");
            return;
        }
        const textarea = getDescriptionTextarea();
        if (textarea) {
            textarea.value = "";
        }
    }

    function setEditorData(html) {
        if (descriptionEditor) {
            descriptionEditor.setData(html || "");
            return;
        }
        const textarea = getDescriptionTextarea();
        if (textarea) {
            textarea.value = html || "";
        }
    }

    function bindForm(formId) {
        const form = document.getElementById(formId);
        if (!form) return;
        form.addEventListener("submit", function () {
            syncEditorToTextarea();
        });
    }

    function init(options) {
        options = options || {};
        const formId = options.formId || "formCreateTask";

        bindForm(formId);

        return initDescriptionEditor().then(function (editor) {
            if (editor && options.initialDescription) {
                editor.setData(options.initialDescription);
            }
            return editor;
        });
    }

    window.CrmTaskModal = {
        init: init,
        syncEditorToTextarea: syncEditorToTextarea,
        resetEditor: resetEditor,
        setEditorData: setEditorData,
    };
})(window);
