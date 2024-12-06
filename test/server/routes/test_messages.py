import requests
from test_auth import login
def print_response_status(response:requests.Response):
    if response.status_code in [200,204]:
        print(f"Response success status code {response.status_code}")
    else:
        print(f"Response fail status code {response.status_code}")
        print("Response text:", response.text)



def get_posts(jwt_token, start_index:int=0, limit:int=10 ):
    url = "http://127.0.0.1:5000/api/v0/messages/posts"
    headers = { "Authorization": f"Bearer {jwt_token}"}
    data_params = {
        "start_index": start_index,
        "limit": limit,
    }
    response: requests.Response = requests.get(url, headers=headers, json=data_params)
    print_response_status(response)
    return response


def create_message(jwt_token,content, reply_to_message_id='')->requests.Response:
    url = "http://127.0.0.1:5000/api/v0/messages/create"
    headers = { "Authorization": f"Bearer {jwt_token}"}
    data_params = {
        "content": content,
        "reply_to_message_id": reply_to_message_id
    }
    response: requests.Response = requests.post(url, headers=headers, json=data_params)
    print_response_status(response)
    return response

def edit_message(jwt_token, message_id, content)->requests.Response:
    url = "http://127.0.0.1:5000/api/v0/messages/edit"
    headers = { "Authorization": f"Bearer {jwt_token}"}
    data_params = {
        "message_id": message_id,
        "content": content
    }
    response: requests.Response = requests.put(url, headers=headers, json=data_params)
    print_response_status(response)
    return response


def delete_message(jwt_token,message_id)->requests.Response:
    url = "http://127.0.0.1:5000/api/v0/messages/delete"
    headers = { "Authorization": f"Bearer {jwt_token}"}
    data_params = {
        "message_id": message_id
    }
    response: requests.Response = requests.post(url, headers=headers, json=data_params)
    print_response_status(response)
    return response


def add_like(jwt_token, message_id):
    url = "http://127.0.0.1:5000/api/v0/messages/like/add"
    headers = { "Authorization": f"Bearer {jwt_token}"}
    data_params = {
        "message_id": message_id
    }
    response: requests.Response = requests.put(url, headers=headers, json=data_params)
    print_response_status(response)
    return response

def remove_like(jwt_token, message_id):
    url = "http://127.0.0.1:5000/api/v0/messages/like/delete"
    headers = { "Authorization": f"Bearer {jwt_token}"}
    data_params = {
        "message_id": message_id
    }
    response: requests.Response = requests.put(url, headers=headers, json=data_params)
    print_response_status(response)
    return response


def get_message(jwt_token, message_id):
    url = "http://127.0.0.1:5000/api/v0/messages/get"
    headers = { "Authorization": f"Bearer {jwt_token}"}
    data_params = {
        "message_id": message_id
    }
    response: requests.Response = requests.get(url, headers=headers, json=data_params)
    print_response_status(response)
    return response


if __name__=="__main__":
    response = login("user3","password3")
    jwt_token = response.json().get("token")
    print(get_posts(jwt_token,0,5))
    post_response = create_message(jwt_token,"post example from user3")
    post = get_message(jwt_token,post_response.json().get("message_id")).json()


