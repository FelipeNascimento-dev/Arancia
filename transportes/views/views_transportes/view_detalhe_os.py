from django.shortcuts import render
from datetime import datetime
from django.utils.dateparse import parse_datetime


def detalhe_os_transp(request):
    payload = {
        "service_order": {
            "id": 609,
            "order_number": "260000000609",
            "external_order_number": "teste123312321",
            "created_by": "Davi",
            "created_at": "2026-02-18T17:05:02.933897Z",
            "order_type": {
                "type": "TRANSPORTE",
                "description": "Transporte de Equipamentos",
                "status_initial_id": 5,
                "client_id": 28,
                "id": 1
            },
            "order_state": {
                "type": "PENDENTE",
                "description": "Equipamento Pendente",
                "finished": False,
                "type_id": 1,
                "id": 1
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
                    "created_at": "2026-02-18T17:05:02.933897Z",
                    "extra_information": None,
                    "id": 959
                },
                {
                    "status_id": None,
                    "event_type_id": 18,
                    "description": "Foi adicionada uma cotação à OS.",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "string",
                    "created_at": "2026-02-18T17:05:02.933897Z",
                    "extra_information": None,
                    "id": 977
                },
                {
                    "status_id": None,
                    "event_type_id": 18,
                    "description": "Foi adicionada uma cotação à OS.",
                    "location_lat": None,
                    "location_long": None,
                    "img_url": None,
                    "created_by": "davi",
                    "created_at": "2026-02-18T17:05:02.933897Z",
                    "extra_information": None,
                    "id": 1034
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
                "service_order_id": 609,
                "carrier_id": 26,
                "origin_id": 11,
                "destination_id": 28,
                "total_weight": 121,
                "total_volume": 20,
                "estimated_price": 211,
                "estimated_deadline": 60,
                "created_by": "davi",
                "id": 9,
                "created_at": "2026-02-18T17:05:02.933897Z"
            },
            {
                "service_order_id": 609,
                "carrier_id": 21,
                "origin_id": 11,
                "destination_id": 11,
                "total_weight": 10,
                "total_volume": 10,
                "estimated_price": 10,
                "estimated_deadline": 10,
                "created_by": "string",
                "id": 42,
                "created_at": "2026-02-18T17:05:02.933897Z"
            },
            {
                "service_order_id": 609,
                "carrier_id": 43,
                "origin_id": 11,
                "destination_id": 26,
                "total_weight": 10,
                "total_volume": 10,
                "estimated_price": 1000,
                "estimated_deadline": 10,
                "created_by": "davi",
                "id": 44,
                "created_at": "2026-02-18T17:05:02.933897Z"
            }
        ],
        "travels": [
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 26,
                "start_date": "2026-01-23T16:37:27.658000-03:00",
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 42,
                "price_charged": 12,
                "id": 67,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1360, 1359, 1358",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 978
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 26,
                "start_date": "2026-01-29T17:45:39.644000-03:00",
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 68,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1360",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1025
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 11,
                "start_date": "2026-01-29T18:03:19.912000-03:00",
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 2,
                "price_charged": 11,
                "id": 69,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1360",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1027
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 43,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 44,
                "price_charged": 0,
                "id": 70,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1366",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1035
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 43,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 44,
                "price_charged": 0,
                "id": 71,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1366",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1037
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 43,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 44,
                "price_charged": 0,
                "id": 72,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1366",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1039
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 43,
                "start_date": None,
                "end_date": None,
                "status_id": 2,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 44,
                "price_charged": 0,
                "id": 73,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1366",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1041
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 43,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 44,
                "price_charged": 0,
                "id": 74,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1366",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1043
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 43,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 44,
                "price_charged": 0,
                "id": 75,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1366",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1045
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 43,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 44,
                "price_charged": 0,
                "id": 76,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1366",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1047
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 43,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 44,
                "price_charged": 41,
                "id": 83,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1366",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1049
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 43,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-10T20:15:30.816000Z",
                "quote_id": 1,
                "price_charged": 41,
                "id": 86,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1366",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1051
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 107,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1376, 1377",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1107
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 108,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1376, 1377",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1109
                    }
                ]
            },
            {
                "order_id": 609,
                "driver_id": 1090,
                "carrier_id": 28,
                "start_date": None,
                "end_date": None,
                "status_id": 1,
                "vehicle_id": 1,
                "created_at": "2026-02-11T15:11:20.772000Z",
                "quote_id": 2,
                "price_charged": 10,
                "id": 109,
                "travel_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Uma nova viagem foi criada para os itens: 1376, 1377",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1111
                    }
                ]
            }
        ],
        "items": [
            {
                "order_number": "teste123",
                "serial_number": "string",
                "product_model": "string",
                "product_type": "string",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "string",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1355,
                "created_at": "2026-01-23T19:18:31.846348Z",
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
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 971
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "111113",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "dav",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1356,
                "created_at": "2026-01-23T19:20:08.391482Z",
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
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 972
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "2113",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "dav",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1357,
                "created_at": "2026-01-23T19:20:08.391482Z",
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
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 973
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "3",
                "product_model": "qweqwe",
                "product_type": "qwe",
                "created_by": "dav",
                "status_id": 2,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "131321",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1360,
                "created_at": "2026-01-23T19:20:08.391482Z",
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
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 976
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 979
                    },
                    {
                        "status_id": 2,
                        "event_type_id": 21,
                        "description": "Status Atualizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 991
                    },
                    {
                        "status_id": 2,
                        "event_type_id": 21,
                        "description": "Status Atualizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 992
                    },
                    {
                        "status_id": 2,
                        "event_type_id": 21,
                        "description": "Status Atualizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 993
                    },
                    {
                        "status_id": 2,
                        "event_type_id": 21,
                        "description": "Status Atualizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 994
                    },
                    {
                        "status_id": 2,
                        "event_type_id": 21,
                        "description": "Status Atualizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 995
                    },
                    {
                        "status_id": 2,
                        "event_type_id": 21,
                        "description": "Status Atualizado",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 996
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 67",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1002
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 67",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1003
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 67",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1004
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 67",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1005
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 67",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1006
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 67",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1007
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 67",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1008
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 67",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1009
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 65",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1010
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para None",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1011
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para 65",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1012
                    },
                    {
                        "status_id": None,
                        "event_type_id": 21,
                        "description": "Foi atualizado o Travel do Item para None",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1013
                    },
                    {
                        "status_id": None,
                        "event_type_id": 14,
                        "description": "Foi atualizado o Travel do Item para None",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1014
                    },
                    {
                        "status_id": None,
                        "event_type_id": 14,
                        "description": "Foi atualizado o Travel do Item para None",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1022
                    },
                    {
                        "status_id": None,
                        "event_type_id": 14,
                        "description": "Foi atualizado o Travel do Item para 65",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "dav",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1023
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1026
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1028
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "st123131ring",
                "product_model": "string",
                "product_type": "string",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "string",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1366,
                "created_at": "2026-01-29T19:32:58.849175Z",
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
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1021
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1036
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1038
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1040
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1042
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1044
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1046
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1048
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1050
                    },
                    {
                        "status_id": None,
                        "event_type_id": 4,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1052
                    }
                ]
            },
            {
                "order_number": None,
                "serial_number": "string",
                "product_model": "string",
                "product_type": "string",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "string",
                "weight": None,
                "height": None,
                "length": None,
                "width": None,
                "id": 1367,
                "created_at": "2026-02-02T18:58:23.350829Z",
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
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1032
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "strin232323232g",
                "product_model": "string",
                "product_type": "UNIQUE",
                "created_by": "Sistema",
                "status_id": 2,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1374,
                "created_at": "2026-02-11T13:02:13.898420Z",
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
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1079
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "pZi",
                "product_model": "string",
                "product_type": None,
                "created_by": "Sistema",
                "status_id": 2,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1375,
                "created_at": "2026-02-11T13:08:03.302701Z",
                "extra_information": {},
                "sub_itens": [],
                "item_events": []
            },
            {
                "order_number": "teste123",
                "serial_number": "pZi",
                "product_model": "string",
                "product_type": None,
                "created_by": "Sistema",
                "status_id": 2,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": 109,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1376,
                "created_at": "2026-02-11T13:10:12.463395Z",
                "extra_information": {},
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1108
                    },
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1110
                    },
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1112
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "pZi",
                "product_model": "string",
                "product_type": None,
                "created_by": "Sistema",
                "status_id": 2,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": 109,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1377,
                "created_at": "2026-02-11T13:15:18.547493Z",
                "extra_information": {},
                "sub_itens": [],
                "item_events": [
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1108
                    },
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1110
                    },
                    {
                        "status_id": None,
                        "event_type_id": 3,
                        "description": "Adicionada viagem à os e atribuída ao item",
                        "location_lat": None,
                        "location_long": None,
                        "img_url": None,
                        "created_by": "string",
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1112
                    }
                ]
            },
            {
                "order_number": "teste123",
                "serial_number": "pZi",
                "product_model": "string",
                "product_type": "VOLUMN",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1378,
                "created_at": "2026-02-11T13:18:57.842629Z",
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
                        "id": 1
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
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1080
                    }
                ]
            },
            {
                "order_number": "teste123312321",
                "serial_number": "str234234234ing",
                "product_model": "string",
                "product_type": "UNIQUE",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": None,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1390,
                "created_at": "2026-02-13T13:39:44.991820Z",
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
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1133
                    }
                ]
            },
            {
                "order_number": "teste123312321",
                "serial_number": "st22ring",
                "product_model": "string",
                "product_type": "UNIQUE",
                "created_by": "Sistema",
                "status_id": 1,
                "client_id": 28,
                "service_order_id": 609,
                "travel_order_id": None,
                "item_control": "string",
                "weight": 0,
                "height": 0,
                "length": 0,
                "width": 0,
                "id": 1392,
                "created_at": "2026-02-13T13:59:03.316050Z",
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
                        "created_at": "2026-02-18T17:05:02.933897Z",
                        "extra_information": None,
                        "id": 1135
                    }
                ]
            }
        ]
    }

    payload["service_order"]["created_at"] = parse_datetime(
        payload["service_order"]["created_at"]
    )

    for quote in payload["quotes"]:
        quote["created_at"] = parse_datetime(quote["created_at"])

    for travel in payload["travels"]:
        travel["created_at"] = parse_datetime(travel["created_at"])

        for ev in travel["travel_events"]:
            ev["created_at"] = parse_datetime(ev["created_at"])

    for item in payload["items"]:
        item["created_at"] = parse_datetime(item["created_at"])

        for ev in item["item_events"]:
            ev["created_at"] = parse_datetime(ev["created_at"])

    for ev in payload["service_order"]["service_order_events"]:
        ev["created_at"] = parse_datetime(ev["created_at"])

    return render(request, 'transportes/transportes/detalhe_os.html', {
        "payload": payload,

    })
