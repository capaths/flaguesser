import requests


SLQ_Injection = "Chile" + "'" + "); DROP TABLE *;"



def test_sqli():
    req = requests.post("http://localhost:8000/signup", json = {
        "username": "SQL_Injection_Test",
        "password": "password",
        "country": SLQ_Injection
    })

    req = requests.get("http://localhost:8000/player/SQL_Injection_Test")
    assert req.status == 200
