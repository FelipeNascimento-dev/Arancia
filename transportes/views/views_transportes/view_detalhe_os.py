from django.shortcuts import render


def detalhe_os(request):
    payload = {
        "service_order": {
            "id": 610,
            "order_number": "260000000610",
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
                "type": "AGUARDANDO COTAÇÃO",
                "description": "Esperando Cotação",
                "finished": False,
                "type_id": 1,
                "id": 5
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
                    "id": 960
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
                "service_order_id": 610,
                "carrier_id": 26,
                "origin_id": 11,
                "destination_id": 26,
                "total_weight": 10,
                "total_volume": 10,
                "estimated_price": 10,
                "estimated_deadline": 10,
                "created_by": "davi",
                "id": 11
            },
            {
                "service_order_id": 610,
                "carrier_id": 26,
                "origin_id": 11,
                "destination_id": 26,
                "total_weight": 10,
                "total_volume": 10,
                "estimated_price": 10,
                "estimated_deadline": 10,
                "created_by": "davi",
                "id": 12
            }
        ],
        "travels": [
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 90,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1088
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 91,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1089
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 92,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1090
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 93,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1091
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 94,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1092
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 95,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1093
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 96,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1094
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 97,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1095
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 98,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1096
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 99,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1097
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 100,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1098
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 101,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1099
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 102,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1100
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 103,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1101
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 104,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1102
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 105,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1103
                    }
                ]
            },
            {
                "order_id": 610,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 106,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1385, 1384",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1105
                    }
                ]
            }
        ],
        "items": [
            {
                "order_number": "teste123",
                "serial_number": "pZi",
                "product_model": "string",
                "product_type": "VOLUMN",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 610,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1379,
                "created_at": "2026-02-11T13:19:19.346574Z",
                "extra_information": {},
                "sub_itens": [
                    {
                        "serial_number": "string",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 2
                    }
                ],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Sistema",
                        "extra_information": None,
                        "id": 1081
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "2p3Zi",
                "product_model": "string",
                "product_type": "VOLUMN",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 610,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1381,
                "created_at": "2026-02-11T13:37:45.164757Z",
                "extra_information": {},
                "sub_itens": [
                    {
                        "serial_number": "string",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 4
                    }
                ],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Sistema",
                        "extra_information": None,
                        "id": 1083
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "2p3eqeqZi",
                "product_model": "string",
                "product_type": "VOLUMN",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 610,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1382,
                "created_at": "2026-02-11T13:42:23.742499Z",
                "extra_information": {},
                "sub_itens": [
                    {
                        "serial_number": "string",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 5
                    }
                ],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Sistema",
                        "extra_information": None,
                        "id": 1084
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "3eqeqZi",
                "product_model": "ing",
                "product_type": "VOLUMN",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 610,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1383,
                "created_at": "2026-02-11T13:43:06.107415Z",
                "extra_information": {},
                "sub_itens": [
                    {
                        "serial_number": "string",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 6
                    }
                ],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Sistema",
                        "extra_information": None,
                        "id": 1085
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "Pai",
                "product_model": "ing",
                "product_type": "VOLUMN",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 610,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1384,
                "created_at": "2026-02-11T13:44:13.607541Z",
                "extra_information": {},
                "sub_itens": [
                    {
                        "serial_number": "string",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 7
                    },
                    {
                        "serial_number": "string",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 8
                    },
                    {
                        "serial_number": "string",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 9
                    },
                    {
                        "serial_number": "st213123ring",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 10
                    },
                    {
                        "serial_number": "string",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 11
                    },
                    {
                        "serial_number": "string",
                        "product_model": "string",
                        "product_type": "string",
                        "item_control": "string",
                        "weight": 0,
                        "height": 0,
                        "length": 0,
                        "width": 0,
                        "extra_information": {},
                        "id": 12
                    }
                ],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Sistema",
                        "extra_information": None,
                        "id": 1086
                    },
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1104
                    },
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1106
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "Pa3i",
                "product_model": "ing",
                "product_type": "UNIQUE",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 610,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1385,
                "created_at": "2026-02-11T13:49:07.373392Z",
                "extra_information": {},
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 2,
                        "description": "item foi atribuído à ordem de serviço",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "Sistema",
                        "extra_information": None,
                        "id": 1087
                    },
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1104
                    },
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "extra_information": None,
                        "id": 1106
                    }
                ]
            }
        ]
    }
    return render(request, 'transportes/transportes/detalhe_os.html', {
        "payload": payload,

    })
