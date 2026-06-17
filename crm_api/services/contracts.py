from crm_api.client import CrmApiClient, parse_list_response


def list_contracts(client: CrmApiClient, *, skip=0, limit=10, q=None, client_gai_id=None):
    params = {"skip": skip, "limit": limit}
    if q:
        params["q"] = q
    if client_gai_id:
        params["client_gai_id"] = client_gai_id
    data = client.get("/contracts/", params=params)
    return parse_list_response(data)


def get_contract(client: CrmApiClient, contract_id):
    return client.get(f"/contracts/{contract_id}")


def create_contract(client: CrmApiClient, payload):
    return client.post("/contracts/", json=payload)


def update_contract(client: CrmApiClient, contract_id, payload):
    return client.patch(f"/contracts/{contract_id}", json=payload)


def list_contract_files(client: CrmApiClient, contract_id):
    data = client.get(f"/contracts/{contract_id}/files")
    items, _ = parse_list_response(data)
    return items if items else (data if isinstance(data, list) else data.get("files", []))


def upload_contract_file(client: CrmApiClient, contract_id, uploaded_file):
    uploaded_file.seek(0)
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file,
            getattr(uploaded_file, "content_type", "application/octet-stream"),
        )
    }
    return client.upload(f"/contracts/{contract_id}/files", files=files)


def delete_contract_file(client: CrmApiClient, contract_id, file_id):
    return client.delete(f"/contracts/{contract_id}/files/{file_id}")
