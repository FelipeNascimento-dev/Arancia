"""Catálogo de ferramentas de infraestrutura para o grupo arancia_DEV."""

from __future__ import annotations


def get_dev_infra_apps() -> list[dict[str, str]]:
    return [
        {
            'name': 'Grafana',
            'category': 'Observabilidade',
            'tag': 'Painel',
            'url': 'http://192.168.0.213:3000',
            'purpose': 'Dashboards, Tempo, Loki e Prometheus',
            'notes': 'Principal tela de observabilidade.',
            'icon': 'fa-solid fa-chart-line',
            'accent': '#f46800',
        },
        {
            'name': 'Prometheus',
            'category': 'Observabilidade',
            'tag': 'Métricas',
            'url': 'http://192.168.0.213:9090',
            'purpose': 'Coleta de métricas',
            'notes': 'Usar /targets para conferir scrapes UP/DOWN.',
            'icon': 'fa-solid fa-gauge-high',
            'accent': '#e6522c',
        },
        {
            'name': 'Uptime Kuma',
            'category': 'Observabilidade',
            'tag': 'Disponibilidade',
            'url': 'http://kuma.wolf.local/dashboard',
            'purpose': 'Disponibilidade e checks',
            'notes': 'Acesso amigável interno sem porta quando DNS local resolve.',
            'icon': 'fa-solid fa-heart-pulse',
            'accent': '#22c55e',
        },
        {
            'name': 'Tempo',
            'category': 'Backends',
            'tag': 'Traces',
            'url': 'http://192.168.0.213:3200/api/echo',
            'purpose': 'Backend de traces',
            'notes': 'Não é painel de usuário. Grafana consulta em http://tempo:3200.',
            'icon': 'fa-solid fa-route',
            'accent': '#8b5cf6',
        },
        {
            'name': 'Loki',
            'category': 'Backends',
            'tag': 'Logs',
            'url': 'http://192.168.0.213:3100/ready',
            'purpose': 'Backend de logs',
            'notes': 'Consulta normalmente via Grafana Explore.',
            'icon': 'fa-solid fa-file-lines',
            'accent': '#f59e0b',
        },
        {
            'name': 'cAdvisor',
            'category': 'Backends',
            'tag': 'Métricas',
            'url': 'http://192.168.0.213:8081',
            'purpose': 'Métricas Docker',
            'notes': 'Usado pelo Prometheus para métricas de containers.',
            'icon': 'fa-solid fa-boxes-stacked',
            'accent': '#6366f1',
        },
        {
            'name': 'Node Exporter',
            'category': 'Backends',
            'tag': 'Host',
            'url': 'http://192.168.0.213:9100/metrics',
            'purpose': 'Métricas do host Linux',
            'notes': 'Endpoint técnico de métricas.',
            'icon': 'fa-solid fa-server',
            'accent': '#64748b',
        },
        {
            'name': 'HAProxy stats',
            'category': 'Backends',
            'tag': 'Load balancer',
            'url': 'http://192.168.0.213:8082',
            'purpose': 'Status / load balancing',
            'notes': 'Se habilitado no HAProxy.',
            'icon': 'fa-solid fa-scale-balanced',
            'accent': '#0ea5e9',
        },
        {
            'name': 'Portainer',
            'category': 'Infraestrutura',
            'tag': 'Docker',
            'url': 'https://192.168.0.213:9443',
            'purpose': 'Gestão Docker visual',
            'notes': 'Usar para containers, volumes, redes e stacks.',
            'icon': 'fa-brands fa-docker',
            'accent': '#13bef9',
        },
        {
            'name': 'Nginx Proxy Manager',
            'category': 'Infraestrutura',
            'tag': 'Proxy',
            'url': 'http://192.168.0.213:81',
            'purpose': 'Reverse proxy e certificados',
            'notes': 'Admin do NPM. Não alterar hosts sem registrar.',
            'icon': 'fa-solid fa-network-wired',
            'accent': '#43a047',
        },
        {
            'name': 'Vaultwarden',
            'category': 'Operações',
            'tag': 'Segurança',
            'url': 'https://mmm.centralretencao.com.br/vault',
            'purpose': 'Cofre de senhas',
            'notes': 'Confirmar se o host está como mm ou mmm no DNS/NPM.',
            'icon': 'fa-solid fa-shield-halved',
            'accent': '#175ddc',
        },
        {
            'name': 'GLPI',
            'category': 'Operações',
            'tag': 'Chamados',
            'url': 'http://192.168.0.213:8086',
            'purpose': 'Inventário e chamados',
            'notes': 'Container GLPI via porta 8086.',
            'icon': 'fa-solid fa-headset',
            'accent': '#ea580c',
        },
    ]


def get_dev_infra_categories(apps: list[dict[str, str]] | None = None) -> list[dict[str, object]]:
    items = apps if apps is not None else get_dev_infra_apps()
    order = ['Observabilidade', 'Backends', 'Infraestrutura', 'Operações']
    icons = {
        'Observabilidade': 'fa-solid fa-chart-pie',
        'Backends': 'fa-solid fa-database',
        'Infraestrutura': 'fa-solid fa-cubes',
        'Operações': 'fa-solid fa-screwdriver-wrench',
    }
    grouped: dict[str, list[dict[str, str]]] = {key: [] for key in order}
    for app in items:
        grouped.setdefault(app['category'], []).append(app)

    return [
        {
            'name': category,
            'icon': icons.get(category, 'fa-solid fa-folder'),
            'apps': grouped.get(category, []),
        }
        for category in order
        if grouped.get(category)
    ]
