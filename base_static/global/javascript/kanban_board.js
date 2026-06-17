/**
 * Kanban drag-and-drop — namespace isolado (Arancia CRM BFF).
 * Chama apenas rotas Django /crm/ajax/tasks/.../move/
 */
(function (window) {
    'use strict';

    const cfg = window.CrmKanbanConfig || {};
    if (!cfg.canMove) return;

    const board = document.getElementById('crm-kanban-root');
    if (!board) return;

    const csrfToken = cfg.csrfToken || '';
    let draggedCard = null;

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

    board.querySelectorAll('.kanban-card[draggable="true"]').forEach(card => {
        card.addEventListener('dragstart', e => {
            draggedCard = card;
            card.classList.add('kanban-card-dragging');
            e.dataTransfer.effectAllowed = 'move';
        });
        card.addEventListener('dragend', () => {
            card.classList.remove('kanban-card-dragging');
            draggedCard = null;
        });
    });

    board.querySelectorAll('.kanban-column-body').forEach(zone => {
        zone.addEventListener('dragover', e => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            zone.classList.add('kanban-drop-hover');
        });
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('kanban-drop-hover');
        });
        zone.addEventListener('drop', e => {
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
})(window);
