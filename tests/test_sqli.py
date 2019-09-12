import requests


SLQ_Injection = "Chile" + "'" + "); DROP TABLE *"



def test_sqli():
    req = requests.post("http://localhost:8000/signup", json = {
        "username": "SQL Injection Test",
        "password": "password",
        "country": SLQ_Injection
    })

    print(req.content)
    assert False