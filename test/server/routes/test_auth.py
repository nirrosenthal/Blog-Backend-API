import requests
from typing import List

def print_response_status(response:requests.Response):
    if response.status_code in [200,204]:
        print(f"Response success status code {response.status_code}")
    else:
        print(f"Response fail status code {response.status_code}")
        print("Response text:", response.text)


def create_user(user_id:str, password:str, roles:List[str] = [])->requests.Response:
    url = "http://127.0.0.1:5000/api/v0/auth/register"
    user_credentials = {
        "user_id": user_id,
        "password": password,
        "roles": roles
    }

    response:requests.Response = requests.post(url, json=user_credentials)
    print_response_status(response)
    return response

def login(user_id:str, password:str)->requests.Response:
    url = "http://127.0.0.1:5000/api/v0/auth/login"
    user_credentials = {
        "user_id": user_id,
        "password": password,
    }
    response:requests.Response = requests.post(url, json=user_credentials)
    print_response_status(response)
    return response


def delete_user(user_id:str)->requests.Response:
    url = "http://127.0.0.1:5000/api/v0/auth/account/delete"
    user_details = {"user_id": user_id}
    response:requests.Response = requests.delete(url, json=user_details)
    print_response_status(response)
    return response



if __name__=="__main__":
    delete_user("user3")
    # can create posts
    user1,password1,roles1 = "user3","password3",["post_user"]
    response = create_user(user1,password1,roles1)
    # jwt_token after login
    user1_jwt_token = login(user1,password1).json().get("token")
    print(user1_jwt_token)
    # cannot create posts only comments
    user2,password2,role2 = "user2","password2",[]
    create_user(user2,password2,role2)




