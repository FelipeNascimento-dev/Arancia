/**
 * Kanban drag-and-drop — namespace isolado (Arancia CRM BFF).
 * Chama apenas rotas Django /crm/ajax/tasks/.../move/
 */
(function (window) {
    'use strict';

    const cfg = window.CrmKanbanConfig || {};
    const board = document.getElementById('crm-kanban-root');
    if (!board) return;

    const csrfToken = cfg.csrfToken || '';
    let draggedCard = null;
    let tasksLoaded = cfg.tasksLoaded || 0;
    let loadingMore = false;

    function moveUrl(taskId) {
        return (cfg.moveUrlTemplate || '').replace('__ID__', String(taskId));
    }

    function cardsInColumn(columnBody) {
        return columnBody.querySelectorAll('.kanban-card');
    }

    function postMove(taskId, statusId, position) {
        return fetch(moveUrl(taskId), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                status_id: statusId,
                kanban_position: position,
                board_id: cfg.boardId,
            }),
        }).then(r => r.json()).then(data => {
            if (!data.ok) {
                window.alert(data.detail || 'Não foi possível mover a task.');
                window.location.reload();
            }
        }).catch(() => {
            window.alert('Erro de comunicação ao mover a task.');
            window.location.reload();
        });
    }

    function bindCardDrag(card) {
        if (!cfg.canMove || card.getAttribute('draggable') !== 'true') return;
        card.addEventListener('dragstart', e => {
            draggedCard = card;
            card.classList.add('kanban-card-dragging');
            e.dataTransfer.effectAllowed = 'move';
        });
        card.addEventListener('dragend', () => {
            card.classList.remove('kanban-card-dragging');
            draggedCard = null;
        });
    }

    function createCardElement(task) {
        const card = document.createElement('div');
        card.className = 'kanban-card';
        card.setAttribute('draggable', cfg.canMove ? 'true' : 'false');
        card.dataset.taskId = String(task.id);

        const titleLink = document.createElement('a');
        titleLink.className = 'kanban-card-title';
        titleLink.href = task.detail_url || '#';
        titleLink.textContent = task.title || 'Task';
        card.appendChild(titleLink);

        if (task.priority_name) {
            const tag = document.createElement('span');
            tag.className = 'kanban-tag';
            tag.textContent = task.priority_name;
            card.appendChild(tag);
        }

        if (task.display_due && task.display_due !== '-') {
            const meta = document.createElement('div');
            meta.className = 'kanban-card-meta';
            meta.innerHTML = '<i class="fa-regular fa-clock"></i> ' + task.display_due;
            card.appendChild(meta);
        }

        bindCardDrag(card);
        return card;
    }

    function findColumnBody(columnKey) {
        const key = String(columnKey);
        const column = board.querySelector('.kanban-column[data-status-id="' + key + '"]');
        return column ? column.querySelector('.kanban-column-body') : null;
    }

    function updateColumnCount(columnKey) {
        const key = String(columnKey);
        const column = board.querySelector('.kanban-column[data-status-id="' + key + '"]');
        if (!column) return;
        const countEl = column.querySelector('.kanban-column-count');
        const body = column.querySelector('.kanban-column-body');
        if (countEl && body) {
            countEl.textContent = String(body.querySelectorAll('.kanban-card').length);
        }
    }

    function appendTasks(tasks) {
        (tasks || []).forEach(task => {
            const body = findColumnBody(task.column_key);
            if (!body) return;
            body.appendChild(createCardElement(task));
            updateColumnCount(task.column_key);
        });
    }

    function setLoadMoreVisible(visible) {
        const btn = document.getElementById('crm-kanban-load-more');
        if (!btn) return;
        btn.hidden = !visible;
        btn.disabled = !visible;
    }

    function loadMoreTasks() {
        if (!cfg.tasksUrl || loadingMore) return;
        loadingMore = true;
        const btn = document.getElementById('crm-kanban-load-more');
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Carregando...';
        }

        const url = cfg.tasksUrl + '?skip=' + encodeURIComponent(String(tasksLoaded)) +
            '&limit=' + encodeURIComponent(String(cfg.loadMoreLimit || 50));

        fetch(url, {
            headers: { Accept: 'application/json' },
            credentials: 'same-origin',
        })
            .then(r => r.json())
            .then(data => {
                if (!data.ok) {
                    window.alert(data.detail || 'Não foi possível carregar mais tasks.');
                    return;
                }
                appendTasks(data.tasks);
                tasksLoaded = data.loaded != null ? data.loaded : (tasksLoaded + (data.tasks || []).length);
                cfg.hasMoreTasks = Boolean(data.has_more);
                setLoadMoreVisible(cfg.hasMoreTasks);
            })
            .catch(() => {
                window.alert('Erro ao carregar mais tasks.');
            })
            .finally(() => {
                loadingMore = false;
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Carregar mais tasks';
                }
            });
    }

    board.querySelectorAll('.kanban-card[draggable="true"]').forEach(bindCardDrag);

    board.querySelectorAll('.kanban-column-body').forEach(zone => {
        zone.addEventListener('dragover', e => {
            if (!cfg.canMove) return;
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            zone.classList.add('kanban-drop-hover');
        });
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('kanban-drop-hover');
        });
        zone.addEventListener('drop', e => {
            if (!cfg.canMove) return;
            e.preventDefault();
            zone.classList.remove('kanban-drop-hover');
            if (!draggedCard) return;

            const column = zone.closest('.kanban-column');
            const statusId = column && column.dataset.statusId;
            if (!statusId) return;

            zone.appendChild(draggedCard);
            const cards = cardsInColumn(zone);
            let position = 0;
            cards.forEach((c, idx) => {
                if (c === draggedCard) position = idx;
            });

            const taskId = draggedCard.dataset.taskId;
            postMove(taskId, statusId, position);

            const countEl = column.querySelector('.kanban-column-count');
            if (countEl) countEl.textContent = String(cards.length);
        });
    });

    const loadMoreBtn = document.getElementById('crm-kanban-load-more');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreTasks);
        setLoadMoreVisible(Boolean(cfg.hasMoreTasks));
    }
})(window);
