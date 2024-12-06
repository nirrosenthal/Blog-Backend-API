import requests
from typing import List

def print_response_status(response:requests.Response):
    if response.status_code in [200,204]:
        print(f"Response success status code {response.status_code}")
    else:
        print(f"Response fail status code {response.status_code}")
        print("Response text:", response.text)


def create_user_request(user_id:str, password:str, roles:List[str] = [])->requests.Response:
    url = "http://127.0.0.1:5000/api/v0/auth/register"
    user_credentials = {
        "user_id": user_id,
        "password": password,
        "roles": roles
    }

    response:requests.Response = requests.post(url, json=user_credentials)
    print_response_status(response)
    return response

def login_request(user_id:str, password:str)->requests.Response:
    url = "http://127.0.0.1:5000/api/v0/auth/login"
    user_credentials = {
        "user_id": user_id,
        "password": password,
    }
    response:requests.Response = requests.post(url, json=user_credentials)
    print_response_status(response)
    return response


if __name__=="__main__":
    user3 = "user3"
    password3 = "password3"
    roles3 = ["user_post"]
    response = create_user_request(user3,password3,roles3)
    user1_jwt_token = login_request(user3,password3).json().get("token")
    print(user1_jwt_token)
    # user2 = "user2"
    # password2 = "password2"
    # create_user_request(user2,password2)



