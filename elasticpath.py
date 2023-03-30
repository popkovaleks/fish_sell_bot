import requests
import json
import time


def is_access_token_expired():
    try:
        with open("access_data.json", "r") as access_file:
            access_data = json.loads(access_file.read())
            return access_data["expires"] < time.time()
    except FileNotFoundError:
        return True


def get_access_token():
    if is_access_token_expired():
        url = "https://api.moltin.com/oauth/access_token"

        payload='client_id=GzfRZv0lswGiw2D56fyxQ8Abw8i2m9s9HJU1xHTgQU&client_secret=MTo6d1YMLqkqLH3CrJWYsz42DpndKJwkCyJP3dWBQT&grant_type=client_credentials'
        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'content-type': 'text/plain'
        }

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        
        with open("access_data.json", "w") as access_file:
            access_file.write(response.text)
        return response.json()["access_token"]

    with open("access_data.json", "r") as access_file:
        access_data = json.loads(access_file.read())
        return access_data["access_token"]


def get_products(access_token):
    url = "https://api.moltin.com/pcm/products"

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response_data = response.json()["data"]

    products = [{
        'id': product["id"],
        'name': product["attributes"]["name"]
    } for product in response_data]
    return products


def get_product(access_token, product_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(f'https://api.moltin.com/pcm/products/{product_id}', headers=headers)
    response.raise_for_status()
    product_data = response.json()["data"]
    product = {
        "name": product_data["attributes"]["name"],
        "description": product_data["attributes"]["description"],
        "image": product_data["relationships"]["main_image"]["data"]["id"],
        "id": product_data["id"]
    }
    return product


def get_file(access_token, file_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/files/{file_id}', headers=headers)
    response.raise_for_status()
    return response.json()["data"]["link"]["href"]


def get_items_in_cart(access_token, chat_id):
    url = f"https://api.moltin.com/v2/carts/{chat_id}/items"

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response_data = response.json()["data"]
    items_in_cart = [{
        "id": product["id"],
        "product_id": product["product_id"],
        "name": product["name"],
        "description": product["description"],
        "quantity": product["quantity"],
        "price_per_kg": product["meta"]["display_price"]["with_tax"]["unit"]["formatted"],
        "value": product["meta"]["display_price"]["with_tax"]["value"]["formatted"]
    } for product in response_data]
  
    return items_in_cart


def get_total_amount_for_cart(access_token, chat_id):
    url = f"https://api.moltin.com/v2/carts/{chat_id}"

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response_data = response.json()["data"]
    return response_data["meta"]["display_price"]["with_tax"]["formatted"]


def add_product_to_cart(access_token, chat_id, product_id, quantity):
    url = f"https://api.moltin.com/v2/carts/{chat_id}/items"

    payload = json.dumps({
        "data": {
            "id": f"{product_id}",
            "type": "cart_item",
            "quantity": quantity
        }
        })
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()


def delete_cart_item(access_token, chat_id, id):
    url = f"https://api.moltin.com/v2/carts/{chat_id}/items/{id}"

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def create_customer(access_token, chat_id, email):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    json_data = {
        'data': {
            'type': 'customer',
            'name': str(chat_id),
            'email': email,
        }
    }

    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=json_data)
    response.raise_for_status()
