import requests

# Base URL of your API
base_url = "http://192.168.1.41:8000/api/admin_view/users"

# Auth Token
auth_token = ("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
              ".eyJzdWIiOiJkaGFuYUBleGFtcGxlLmNvbSIsImlhdCI6MTcxNTIzNDY1OSwibmJmIjoxNzE"
              "1MjM0NjU5LCJqdGkiOiIzMzU3ZmY1Ni0yMGI5LTRmNGEtYjcwNy0yZTc0MDVjZDdiZGIiLCJleHAiO"
              "jE3MTUyNDE4NTksInR5cGUiOiJhY2Nlc3MiLCJmcmVzaCI6ZmFsc2V9.oTJi9IiLqe07MTLdrcTADBtS"
              "6hBb1MxIAFiqBd-oAm0")


def get_request():
    headers = {"Authorization": auth_token}
    response = requests.get(base_url, headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    print("json response body: ", json_data)


get_request()
