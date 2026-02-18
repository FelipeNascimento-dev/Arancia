from django.shortcuts import render


def detalhe_os_transp(request):
    payload = {
        "service_order": {
            "id": 602,
            "order_number": "260000000602",
            "external_order_number": "teste123",
            "created_by": "Davi",
            "order_type": {
                "type": "TRANSPORTE",
                "description": "Transporte de Equipamentos",
                "status_initial_id": 5,
                "client_id": 28,
                "id": 1
            },
            "order_state": {
                "type": "CANCELADO",
                "description": "Equipamento Cancelado",
                "finished": True,
                "type_id": 1,
                "id": 4
            },
            "service_order_events": [
                {
                    "status_id": None,
                    "event_type_id": 15,
                    "description": "OS foi criada e aguarda cotação",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "Davi",
                    "extra_information": None,
                    "id": 250
                },
                {
                    "status_id": None,
                    "event_type_id": 18,
                    "description": "Foi adicionada uma cotação à OS.",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "davi",
                    "extra_information": None,
                    "id": 256
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "total_itens": 6,
                        "seriais": [
                            "41111",
                            "2113",
                            "3",
                            "111113",
                            "4111111",
                            "34"
                        ]
                    },
                    "id": 368
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "seriais": [
                            "2113",
                            "4111111",
                            "3",
                            "34",
                            "41111",
                            "111113"
                        ]
                    },
                    "id": 379
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 383
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 385
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 387
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 389
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 391
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 393
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 395
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 397
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 399
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 401
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 403
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 405
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 407
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 409
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 411
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 413
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 415
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 417
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 419
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 421
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 423
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 425
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 427
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 429
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 431
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 433
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 435
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 437
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 439
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 451
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 453
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 455
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Ordem de serviço finalizada",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": {
                        "itens": [
                            [
                                "2113",
                                "teste123"
                            ],
                            [
                                "34",
                                "teste123"
                            ],
                            [
                                "41111",
                                "teste123"
                            ],
                            [
                                "4111111",
                                "teste123"
                            ],
                            [
                                "3",
                                "teste123"
                            ],
                            [
                                "111113",
                                "teste123"
                            ]
                        ]
                    },
                    "id": 457
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "coletado c/ sucesso",
                    "location_lat": "string",
                    "location_long": "string",
                    "img_url": "string",
                    "created_by": "string",
                    "extra_information": {
                        "obs": "ajuda na rota",
                        "itens": [
                            "Iteem1",
                            "2113",
                            "3"
                        ]
                    },
                    "id": 722
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "coletado c/ sucesso",
                    "location_lat": "string",
                    "location_long": "string",
                    "img_url": "string",
                    "created_by": "string",
                    "extra_information": {
                        "obs": "ajuda na rota",
                        "itens": [
                            "Iteem1",
                            "2113",
                            "3"
                        ]
                    },
                    "id": 723
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "coletado c/ sucesso",
                    "location_lat": "string",
                    "location_long": "string",
                    "img_url": "string",
                    "created_by": "string",
                    "extra_information": {
                        "obs": "ajuda na rota",
                        "itens": [
                            "Iteem1",
                            "2113",
                            "3"
                        ]
                    },
                    "id": 724
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "coletado c/ sucesso",
                    "location_lat": "string",
                    "location_long": "string",
                    "img_url": "string",
                    "created_by": "string",
                    "extra_information": {
                        "obs": "ajuda na rota",
                        "itens": [
                            "Iteem1",
                            "2113",
                            "3"
                        ]
                    },
                    "id": 725
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "string",
                    "location_lat": "string",
                    "location_long": "string",
                    "img_url": "string",
                    "created_by": "string",
                    "extra_information": {},
                    "id": 726
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "string",
                    "location_lat": "string",
                    "location_long": "string",
                    "img_url": "string",
                    "created_by": "string",
                    "extra_information": {},
                    "id": 727
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "string",
                    "location_lat": "string",
                    "location_long": "string",
                    "img_url": "string",
                    "created_by": "string",
                    "extra_information": {},
                    "id": 728
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "string",
                    "location_lat": "string",
                    "location_long": "string",
                    "img_url": "string",
                    "created_by": "string",
                    "extra_information": {},
                    "id": 729
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "string",
                    "location_lat": "string",
                    "location_long": "string",
                    "img_url": "string",
                    "created_by": "string",
                    "extra_information": {},
                    "id": 730
                },
                {
                    "status_id": 4,
                    "event_type_id": 21,
                    "description": "OS FINALIZADA",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "davi",
                    "extra_information": {
                        "service_order_id": 602,
                        "total_itens": 9
                    },
                    "id": 922
                },
                {
                    "status_id": 4,
                    "event_type_id": 21,
                    "description": "OS FINALIZADA",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "davi",
                    "extra_information": {
                        "service_order_id": 602,
                        "total_itens": 9
                    },
                    "id": 932
                },
                {
                    "status_id": 4,
                    "event_type_id": 21,
                    "description": "OS FINALIZADA",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "davi",
                    "extra_information": {
                        "service_order_id": 602,
                        "total_itens": 9
                    },
                    "id": 942
                },
                {
                    "status_id": 4,
                    "event_type_id": 21,
                    "description": "OS FINALIZADA",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "davi",
                    "extra_information": {
                        "service_order_id": 602,
                        "total_itens": 9
                    },
                    "id": 952
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Status tualizado",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "davi",
                    "extra_information": None,
                    "id": 968
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Status tualizado",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "davi",
                    "extra_information": None,
                    "id": 969
                },
                {
                    "status_id": None,
                    "event_type_id": 21,
                    "description": "Status tualizado",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "davi",
                    "extra_information": None,
                    "id": 970
                },
                {
                    "status_id": None,
                    "event_type_id": 18,
                    "description": "Foi adicionada uma cotação à OS.",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "extra_information": None,
                    "id": 1024
                },
                {
                    "status_id": 4,
                    "event_type_id": 21,
                    "description": "teste1",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "ssabio",
                    "extra_information": {},
                    "id": 1031
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
            "cnpj": None,
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
            "cnpj": "34.616.682/0001-83",
            "telefone1": "(11) 97233-9756",
            "telefone2": "(11) 95101-8967",
            "email": "ti@c-trends.com.br",
            "responsavel": "Igor Rocha",
            "id": 11
        },
        "destination": {
            "nome": "Tatuapé",
            "cod_iata": "SPO",
            "sales_channel": "SFC-Ctrends Tatuape",
            "deposito": "989A",
            "logradouro": "Rua Bonfim",
            "numero": "81",
            "complemento": "Portão azul",
            "bairro": "Maranhão",
            "cidade": "São Paulo",
            "UF": None,
            "estado": "SP",
            "CEP": "03073-010",
            "cnpj": "",
            "telefone1": "",
            "telefone2": "",
            "email": "suportecd@c-trends.com.br",
            "responsavel": "Bruno",
            "id": 27
        },
        "quotes": [
            {
                "service_order_id": 602,
                "carrier_id": 26,
                "origin_id": 11,
                "destination_id": 27,
                "total_weight": 10,
                "total_volume": 10,
                "estimated_price": 10,
                "estimated_deadline": 10,
                "created_by": "davi",
                "id": 36
            },
            {
                "service_order_id": 602,
                "carrier_id": 11,
                "origin_id": 11,
                "destination_id": 26,
                "total_weight": 1,
                "total_volume": 10,
                "estimated_price": 10,
                "estimated_deadline": 10,
                "created_by": "string",
                "id": 43
            }
        ],
        "travels": [
            {
                "order_id": 602,
                "driver_id": 1090,
                "carrier_id": 26,
                "start_date": "2026-01-12T13:08:32.268000-03:00",
                "end_date": "2026-01-22T17:31:41.832599-03:00",
                "status_id": 2,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 36,
                "price_charged": 9,
                "id": 65,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1340, 1341",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": None,
                        "id": 257
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_items": 3
                        },
                        "id": 311
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 2,
                            "seriais": [
                                "111113",
                                "2113"
                            ]
                        },
                        "id": 316
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 4,
                            "seriais": [
                                "3",
                                "41111",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 317
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "4111111",
                                "3",
                                "2113",
                                "111113",
                                "41111"
                            ]
                        },
                        "id": 358
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 6,
                            "seriais": [
                                "41111",
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 367
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "111113"
                            ]
                        },
                        "id": 369
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 370
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 371
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 372
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 373
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 374
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 375
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 376
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 377
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "seriais_destacados": [
                                "41111"
                            ],
                            "seriais_desvinculados": [
                                "2113",
                                "4111111",
                                "3",
                                "34",
                                "111113"
                            ]
                        },
                        "id": 378
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "seriais_destacados": [
                                "41111"
                            ],
                            "seriais_desvinculados": []
                        },
                        "id": 380
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "seriais_destacados": [
                                "41111"
                            ],
                            "seriais_desvinculados": []
                        },
                        "id": 381
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 382
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 384
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 386
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 388
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 390
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 392
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 394
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 396
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 398
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 400
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 402
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 404
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 406
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 408
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 410
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 412
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 414
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 416
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 418
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 420
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 422
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 424
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 426
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 428
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 430
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 432
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 434
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 436
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "destacados": [],
                            "desvinculados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 438
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 454
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [],
                            "desvinculados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "41111",
                                    "teste123"
                                ],
                                [
                                    "111113",
                                    "teste123"
                                ],
                                [
                                    "4111111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 456
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 458
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 459
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 460
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 461
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": []
                        },
                        "id": 462
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": []
                        },
                        "id": 463
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 464
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 465
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 466
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 467
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 468
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": []
                        },
                        "id": 469
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 470
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 471
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "STRING",
                                    "sss"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 472
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "STRING",
                                    "sss"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": []
                        },
                        "id": 473
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "STRING",
                                    "sss"
                                ]
                            ],
                            "desvinculados": []
                        },
                        "id": 474
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "STRING",
                                    "sss"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 475
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 476
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Atualização da viagem",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "destacados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "retirados": []
                        },
                        "id": 477
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Atualização da viagem",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "destacados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ]
                            ],
                            "retirados": []
                        },
                        "id": 478
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "Item atribuido",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Davi",
                        "extra_information": None,
                        "id": 21
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "teste",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 582
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "teste eee",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 583
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "teste eee",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 584
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 585
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 586
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 588
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 590
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 592
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 594
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 596
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 598
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 600
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 602
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 604
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 606
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "Item2"
                            ]
                        },
                        "id": 608
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "111113"
                            ]
                        },
                        "id": 610
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "111113"
                            ]
                        },
                        "id": 612
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113"
                            ]
                        },
                        "id": 614
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113"
                            ]
                        },
                        "id": 616
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 618
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 620
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 622
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 624
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 626
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 628
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 630
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 632
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 634
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 637
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 640
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 643
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 646
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 649
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "dadawdwaddadadwa",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 652
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 656
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 660
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota"
                        },
                        "id": 664
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota"
                        },
                        "id": 670
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota"
                        },
                        "id": 676
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 682
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 686
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 689
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 690
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 693
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 698
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 703
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 707
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 710
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 713
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "coletado c/ sucesso",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "obs": "ajuda na rota",
                            "itens": [
                                "Iteem1",
                                "2113",
                                "3"
                            ]
                        },
                        "id": 719
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 1",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona"
                            ]
                        },
                        "id": 735
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 741
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 746
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 749
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 756
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 757
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 758
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 759
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 760
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 761
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 762
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 763
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 764
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 765
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 766
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 773
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona1"
                            ]
                        },
                        "id": 774
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 781
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 788
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 795
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona11",
                                "te1stesefunciona11"
                            ]
                        },
                        "id": 802
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 810
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 819
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 828
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 837
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 846
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 855
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "3"
                            ]
                        },
                        "id": 864
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "3"
                            ]
                        },
                        "id": 874
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "3"
                            ]
                        },
                        "id": 884
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona11",
                                "testesefunciona11"
                            ]
                        },
                        "id": 894
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "ITEM2",
                                "4111111",
                                "testesefunciona11",
                                "testesefunciona11"
                            ]
                        },
                        "id": 904
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "itens": [
                                "3"
                            ]
                        },
                        "id": 913
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 923
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 933
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "testando validacao 2",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 943
                    },
                    {
                        "status_id": 2,
                        "event_type_id": 21,
                        "description": "Status Atualizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "C-trends",
                        "extra_information": None,
                        "id": 1029
                    },
                    {
                        "status_id": 2,
                        "event_type_id": 21,
                        "description": "Status Atualizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1030
                    }
                ]
            },
            {
                "order_id": 602,
                "driver_id": 1090,
                "carrier_id": 26,
                "start_date": "2026-01-13T15:38:56.698000-03:00",
                "end_date": None,
                "status_id": 2,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 2,
                "price_charged": 9,
                "id": 66,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1342",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davu",
                        "extra_information": None,
                        "id": 259
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 274
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 275
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 276
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 277
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 278
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 279
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 280
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 281
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 282
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 285
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 286
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 287
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 288
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 289
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {},
                        "id": 290
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "string",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {},
                        "id": 291
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "string",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {},
                        "id": 292
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "string",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {},
                        "id": 293
                    },
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "string",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {},
                        "id": 294
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "string",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {},
                        "id": 295
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "string",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {},
                        "id": 296
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Foi retirado após finalizada o viagem por falta do item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {},
                        "id": 297
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66
                        },
                        "id": 300
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66
                        },
                        "id": 301
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item": 1342,
                            "travel_id": 66
                        },
                        "id": 302
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66
                        },
                        "id": 303
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item_id": 1342,
                            "travel_id": 66
                        },
                        "id": 304
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item_id": 1342,
                            "travel_id": 66
                        },
                        "id": 305
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item_id": 1345,
                            "travel_id": 66
                        },
                        "id": 306
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item_id": 1344,
                            "travel_id": 66
                        },
                        "id": 307
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_items": 3
                        },
                        "id": 308
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_items": 3
                        },
                        "id": 309
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_items": 3
                        },
                        "id": 310
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "34",
                                "4111111",
                                "3",
                                "41111"
                            ]
                        },
                        "id": 314
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "4111111",
                                "41111",
                                "34",
                                "3"
                            ]
                        },
                        "id": 315
                    },
                    {
                        "status_id": 2,
                        "event_type_id": 21,
                        "description": "Status Atualizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1000
                    }
                ]
            }
        ],
        "items": [
            {
                "order_number": "teste123",
                "serial_number": "111113",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "davi",
                "status_id": 4,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": 66,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1340,
                "created_at": "2026-01-12T16:31:58.612092Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": None,
                        "id": 251
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": None,
                        "id": 258
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 2,
                            "seriais": [
                                "111113",
                                "2113"
                            ]
                        },
                        "id": 316
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 4,
                            "seriais": [
                                "3",
                                "41111",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 317
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "4111111",
                                "3",
                                "2113",
                                "111113",
                                "41111"
                            ]
                        },
                        "id": 358
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 6,
                            "seriais": [
                                "41111",
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 367
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "111113"
                            ]
                        },
                        "id": 369
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 370
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "2113",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "davi",
                "status_id": 4,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": 65,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1341,
                "created_at": "2026-01-12T16:31:58.612092Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": None,
                        "id": 252
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": None,
                        "id": 258
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 2,
                            "seriais": [
                                "111113",
                                "2113"
                            ]
                        },
                        "id": 316
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "4111111",
                                "3",
                                "2113",
                                "111113",
                                "41111"
                            ]
                        },
                        "id": 358
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 6,
                            "seriais": [
                                "41111",
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 367
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 370
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 4
                        },
                        "id": 520
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste1231",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 521
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 522
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 523
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 525
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 527
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 529
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 530
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 531
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 533
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 535
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 537
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 540
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 542
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 545
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 548
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 550
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 552
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 555
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 558
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 561
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "3",
                                "2113"
                            ],
                            "total_itens": 3
                        },
                        "id": 625
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "3",
                                "2113"
                            ],
                            "total_itens": 3
                        },
                        "id": 627
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "3",
                                "2113"
                            ],
                            "total_itens": 3
                        },
                        "id": 629
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "2113",
                                "3"
                            ],
                            "total_itens": 3
                        },
                        "id": 631
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "2113",
                                "3"
                            ],
                            "total_itens": 3
                        },
                        "id": 633
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 635
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 638
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 641
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 644
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 647
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "2113",
                                "3"
                            ],
                            "total_itens": 3
                        },
                        "id": 650
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 653
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 657
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 661
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 683
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 687
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 691
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113"
                            ],
                            "total_itens": 2
                        },
                        "id": 694
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113"
                            ],
                            "total_itens": 2
                        },
                        "id": 699
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 704
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 708
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 711
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113"
                            ],
                            "total_itens": 2
                        },
                        "id": 714
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 720
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "4111111",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "davi",
                "status_id": 4,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": 66,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1342,
                "created_at": "2026-01-12T16:31:58.612092Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": None,
                        "id": 253
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davu",
                        "extra_information": None,
                        "id": 260
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item": 1342,
                            "travel_id": 66
                        },
                        "id": 302
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66
                        },
                        "id": 303
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item_id": 1342,
                            "travel_id": 66
                        },
                        "id": 304
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item_id": 1342,
                            "travel_id": 66
                        },
                        "id": 305
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_items": 3
                        },
                        "id": 308
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_items": 3
                        },
                        "id": 311
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "34",
                                "4111111",
                                "3",
                                "41111"
                            ]
                        },
                        "id": 314
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "4111111",
                                "41111",
                                "34",
                                "3"
                            ]
                        },
                        "id": 315
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 4,
                            "seriais": [
                                "3",
                                "41111",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 317
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "4111111",
                                "3",
                                "2113",
                                "111113",
                                "41111"
                            ]
                        },
                        "id": 358
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 6,
                            "seriais": [
                                "41111",
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 367
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 370
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                "4111111"
                            ],
                            "total_itens": 1
                        },
                        "id": 737
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                "4111111"
                            ],
                            "total_itens": 1
                        },
                        "id": 743
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                "4111111"
                            ],
                            "total_itens": 1
                        },
                        "id": 748
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                "4111111"
                            ],
                            "total_itens": 1
                        },
                        "id": 751
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                "4111111"
                            ],
                            "total_itens": 1
                        },
                        "id": 768
                    },
                    {
                        "status_id": 1,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                "4111111"
                            ],
                            "total_itens": 1
                        },
                        "id": 776
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                "4111111"
                            ],
                            "total_itens": 1
                        },
                        "id": 804
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                "4111111"
                            ],
                            "total_itens": 1
                        },
                        "id": 896
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                "4111111"
                            ],
                            "total_itens": 1
                        },
                        "id": 906
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "34",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "davi",
                "status_id": 4,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": 65,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1343,
                "created_at": "2026-01-12T16:31:58.612092Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": None,
                        "id": 254
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "34",
                                "4111111",
                                "3",
                                "41111"
                            ]
                        },
                        "id": 314
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "4111111",
                                "41111",
                                "34",
                                "3"
                            ]
                        },
                        "id": 315
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 6,
                            "seriais": [
                                "41111",
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 367
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 370
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 4
                        },
                        "id": 520
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste1231",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 521
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 522
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 523
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 525
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 527
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 528
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 530
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 531
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 533
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 535
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 538
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 540
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 542
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 545
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 548
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 550
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 552
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 555
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 558
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 561
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "3",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "davi",
                "status_id": 4,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": 65,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1344,
                "created_at": "2026-01-12T16:31:58.612092Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": None,
                        "id": 255
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item_id": 1344,
                            "travel_id": 66
                        },
                        "id": 307
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_items": 3
                        },
                        "id": 308
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_items": 3
                        },
                        "id": 311
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "34",
                                "4111111",
                                "3",
                                "41111"
                            ]
                        },
                        "id": 314
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "4111111",
                                "41111",
                                "34",
                                "3"
                            ]
                        },
                        "id": 315
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 4,
                            "seriais": [
                                "3",
                                "41111",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 317
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "4111111",
                                "3",
                                "2113",
                                "111113",
                                "41111"
                            ]
                        },
                        "id": 358
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 6,
                            "seriais": [
                                "41111",
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 367
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 370
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "STRING",
                                    "sss"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 475
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 476
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 4
                        },
                        "id": 520
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste1231",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 521
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 523
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 525
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 527
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 528
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 530
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 531
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 533
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 535
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 537
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 540
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 542
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 545
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 548
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 550
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 552
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 555
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 558
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 561
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "3",
                                "2113"
                            ],
                            "total_itens": 3
                        },
                        "id": 625
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "3",
                                "2113"
                            ],
                            "total_itens": 3
                        },
                        "id": 627
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "3",
                                "2113"
                            ],
                            "total_itens": 3
                        },
                        "id": 629
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "2113",
                                "3"
                            ],
                            "total_itens": 3
                        },
                        "id": 631
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "2113",
                                "3"
                            ],
                            "total_itens": 3
                        },
                        "id": 633
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 635
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 638
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 641
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 644
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 647
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "ITEEM1",
                                "2113",
                                "3"
                            ],
                            "total_itens": 3
                        },
                        "id": 650
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 653
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 657
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 661
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 683
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113",
                                "ITEEM1"
                            ],
                            "total_itens": 3
                        },
                        "id": 687
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 691
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113"
                            ],
                            "total_itens": 2
                        },
                        "id": 694
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113"
                            ],
                            "total_itens": 2
                        },
                        "id": 699
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 704
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 708
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 711
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3",
                                "2113"
                            ],
                            "total_itens": 2
                        },
                        "id": 714
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "2113",
                                "3"
                            ],
                            "total_itens": 2
                        },
                        "id": 720
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3"
                            ],
                            "total_itens": 1
                        },
                        "id": 865
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3"
                            ],
                            "total_itens": 1
                        },
                        "id": 875
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3"
                            ],
                            "total_itens": 1
                        },
                        "id": 885
                    },
                    {
                        "status_id": 4,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "davi",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                "3"
                            ],
                            "total_itens": 1
                        },
                        "id": 914
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "41111",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "davi",
                "status_id": 4,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": 66,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1345,
                "created_at": "2026-01-12T16:31:58.612092Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "item_id": 1345,
                            "travel_id": 66
                        },
                        "id": 306
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_items": 3
                        },
                        "id": 308
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_items": 3
                        },
                        "id": 311
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "34",
                                "4111111",
                                "3",
                                "41111"
                            ]
                        },
                        "id": 314
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 66,
                            "total_itens": 4,
                            "seriais": [
                                "4111111",
                                "41111",
                                "34",
                                "3"
                            ]
                        },
                        "id": 315
                    },
                    {
                        "status_id": None,
                        "event_type_id": 32,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 4,
                            "seriais": [
                                "3",
                                "41111",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 317
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 5,
                            "seriais": [
                                "4111111",
                                "3",
                                "2113",
                                "111113",
                                "41111"
                            ]
                        },
                        "id": 358
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 6,
                            "seriais": [
                                "41111",
                                "34",
                                "2113",
                                "3",
                                "111113",
                                "4111111"
                            ]
                        },
                        "id": 367
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 371
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 372
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_id": 65,
                            "total_itens": 1,
                            "seriais": [
                                "41111"
                            ]
                        },
                        "id": 377
                    }
                ]
            },
            {
                "order_number": "sss",
                "serial_number": "STRING",
                "product_model": None,
                "product_type": None,
                "created_by": "Sistema",
                "status_id": 4,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": 66,
                "item_control": None,
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1346,
                "created_at": "2026-01-20T12:06:52.660652Z",
                "extra_information": None,
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "34",
                                    "teste123"
                                ],
                                [
                                    "3",
                                    "teste123"
                                ],
                                [
                                    "2113",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 471
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FOI RETIRADO DA TRAVEL:",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "coletados": [
                                [
                                    "2113",
                                    "teste123"
                                ],
                                [
                                    "34",
                                    "teste123"
                                ]
                            ],
                            "desvinculados": [
                                [
                                    "41111",
                                    "teste123"
                                ]
                            ]
                        },
                        "id": 476
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 4
                        },
                        "id": 520
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste1231",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 521
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 522
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 523
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 525
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 527
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 528
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 530
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 531
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 533
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 535
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 537
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 540
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 543
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 546
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 549
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 551
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 553
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 556
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 559
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "ITEM FINALIZADO EM OUTRA VIAGEM",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 66,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 1
                        },
                        "id": 562
                    }
                ]
            },
            {
                "order_number": "teste1231",
                "serial_number": "34",
                "product_model": None,
                "product_type": None,
                "created_by": "Sistema",
                "status_id": 4,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": 66,
                "item_control": None,
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1347,
                "created_at": "2026-01-20T16:12:01.488454Z",
                "extra_information": None,
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste1231",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 521
                    }
                ]
            },
            {
                "order_number": "teste12321",
                "serial_number": "34",
                "product_model": None,
                "product_type": None,
                "created_by": "Sistema",
                "status_id": 4,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": 65,
                "item_control": None,
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1348,
                "created_at": "2026-01-20T16:19:27.033370Z",
                "extra_information": None,
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": None,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 523
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss",
                                    "travel_origem": 65,
                                    "travel_finalizada": 65
                                }
                            ],
                            "travel_finalizada": 65,
                            "total_itens": 5
                        },
                        "id": 525
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 527
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 528
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 530
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 531
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 533
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 535
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 537
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "STRING",
                                    "order": "sss"
                                }
                            ],
                            "total_itens": 5
                        },
                        "id": 540
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 542
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 545
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 548
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 550
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 552
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 555
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 558
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": " Item Finalizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": {
                            "travel_origem": 65,
                            "travel_finalizada": 65,
                            "itens": [
                                {
                                    "serial": "2113",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "3",
                                    "order": "teste123"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste12321"
                                },
                                {
                                    "serial": "34",
                                    "order": "teste123"
                                }
                            ],
                            "total_itens": 4
                        },
                        "id": 561
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "111113",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "1212",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": None,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1361,
                "created_at": "2026-01-29T19:04:02.335724Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "1212",
                        "extra_information": None,
                        "id": 1016
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "2113",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "1212",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": None,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1362,
                "created_at": "2026-01-29T19:04:02.335724Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "1212",
                        "extra_information": None,
                        "id": 1017
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "4111111",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "1212",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": None,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1363,
                "created_at": "2026-01-29T19:04:02.335724Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "1212",
                        "extra_information": None,
                        "id": 1018
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "34",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "1212",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": None,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1364,
                "created_at": "2026-01-29T19:04:02.335724Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "1212",
                        "extra_information": None,
                        "id": 1019
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "3",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "1212",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 602,
                "travel_order_id": None,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1365,
                "created_at": "2026-01-29T19:04:02.335724Z",
                "extra_information": {
                    "nr_mac": "Campo Extra,q Pode ser criada mais Colunas",
                    "teste": "oio",
                    "test": "iii"
                },
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "1212",
                        "extra_information": None,
                        "id": 1020
                    }
                ]
            }
        ]
    }
    return render(request, 'transportes/transportes/detalhe_os.html', {
        "payload": payload,

    })
