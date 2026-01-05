from django.shortcuts import render


def transp_view(request):
    payload = {
        "service_order": {
            "id": 571,
            "order_number": "260000000571",
            "external_order_number": "TESTE",
            "price_charged": 10,
            "created_by": "ARC0000",
            "order_type": {
                "type": "TRANSPORTE",
                "description": "Transporte de Equipamentos",
                "id": 1
            },
            "order_state": {
                "type": "AGUARDANDO COTAÇÃO",
                "description": "Esperando Cotação",
                "finished": None
            },
            "service_order_events": [
                {
                    "event_type_id": 15,
                    "status_id": None,
                    "description": "OS foi criada e aguarda cotação",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "ARC0000",
                    "id": 127
                }
            ]
        },

        "client": {
            "nome": "teste",
            "cod_iata": None,
            "sales_channel": "all",
            "deposito": "989S",
            "logradouro": "Rua Bonfim",
            "numero": "81",
            "complemento": "Portao Azul",
            "bairro": "Maranhão",
            "cidade": "São Paulo",
            "UF": "SP",
            "estado": "SP",
            "CEP": "03073-010",
            "telefone1": None,
            "telefone2": None,
            "email": "ti@c-trends.com.br",
            "responsavel": None,
            "id": 26
        },

        "origin": {
            "nome": "TI",
            "cod_iata": "SPO",
            "sales_channel": "all",
            "deposito": "989A",
            "logradouro": "Rua Bonfim",
            "numero": "81",
            "complemento": None,
            "bairro": "Maranhão",
            "cidade": "São Paulo",
            "UF": "SP",
            "estado": "SP",
            "CEP": "03073-010",
            "telefone1": "(11) 97233-9756",
            "telefone2": "(11) 95101-8967",
            "email": "ti@c-trends.com.br",
            "responsavel": "Igor Rocha",
            "id": 11
        },

        "destination": {
            "nome": "BKO",
            "cod_iata": "SPO",
            "sales_channel": "all",
            "deposito": "3131",
            "logradouro": "Rua Bonfim",
            "numero": "81",
            "complemento": None,
            "bairro": "Maranhão",
            "cidade": "São Paulo",
            "UF": None,
            "estado": "SP",
            "CEP": "03073-010",
            "telefone1": "11999999999",
            "telefone2": "(11) 95101-8967",
            "email": "felipe.nascimento@c-trends.com.br",
            "responsavel": "Felipe",
            "id": 21
        },

        "quotes": [
            {
                "service_order_id": 571,
                "carrier_id": 26,
                "origin_cep": "C-TRENDS",
                "destination_cep": "CIELO",
                "total_weight": 11.1,
                "total_volume": 1,
                "estimated_price": 49,
                "estimated_deadline": 15,
                "created_by": "DAVI",
                "id": 1
            }
        ],

        "travels": [
            {
                "order_id": 571,
                "driver_id": 2,
                "carrier_id": 11,
                "start_date": "2025-12-30T22:12:00Z",
                "end_date": "2025-12-30T22:12:00Z",
                "status_id": 1,
                "vehicle_id": 1,
                "id": 28,
                "travel_events": [
                    {
                        "event_type_id": 3,
                        "status_id": None,
                        "description": "Viagem criada",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "id": 34
                    }
                ]
            }
        ],

        "items": [
            {
                "order_number": "CLR21312313",
                "order_origin": "SGA",
                "serial_number": "string213",
                "product_model": "string",
                "product_type": "string",
                "service_type": "string",
                "created_by": "Sistema",
                "status_id": 1,
                "service_deadline": "2026-01-10T10:07:24.005081Z",
                "id": 1244,
                "created_at": "2025-12-26T10:39:39.092987Z",
                "extra_information": {},
                "item_events": [
                    {
                        "event_type_id": 2,
                        "status_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "ARC0000",
                        "id": 128
                    }
                ]
            }
        ]
    }

    service_order = payload.get("service_order", {})
    client = payload.get("client", {})
    origin = payload.get("origin", {})
    destination = payload.get("destination", {})
    quotes = payload.get("quotes", [])
    travels = payload.get("travels", [])
    items = payload.get("items", [])

    historico = []

    for ev in service_order.get("service_order_events", []):
        historico.append({
            "tipo": "OS",
            "descricao": ev.get("description"),
            "created_by": ev.get("created_by"),
        })

    for travel in travels:
        for ev in travel.get("travel_events", []):
            historico.append({
                "tipo": "VIAGEM",
                "descricao": ev.get("description"),
                "created_by": ev.get("created_by"),
            })

    for item in items:
        for ev in item.get("item_events", []):
            historico.append({
                "tipo": "ITEM",
                "descricao": ev.get("description"),
                "created_by": ev.get("created_by"),
            })

    context = {
        "service_order": service_order,
        "client": client,
        "origin": origin,
        "destination": destination,
        "quotes": quotes,
        "travels": travels,
        "items": items,
        "historico": historico,
        "total_eventos": len(historico),
        "quote": quotes[0] if quotes else None
    }

    return render(request, "logistica/transp.html", context)
