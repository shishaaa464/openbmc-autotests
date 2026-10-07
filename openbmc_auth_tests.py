import time
import pytest
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OPENBMC_HOST = "127.0.0.1:2443"
BASE_URL = f"https://{OPENBMC_HOST}"

VALID_USER = "root"
VALID_PASSWORD = "0penBmc"
INVALID_PASSWORD = "WrongPassword123"


def get_authenticated_session(username, password):
    """Вспомогательная функция для получения Redfish Session Token"""
    session = requests.Session()
    session.verify = False
    payload = {"UserName": username, "Password": password}
    response = session.post(
        f"{BASE_URL}/redfish/v1/SessionService/Sessions",
        json=payload,
        timeout=5
    )
    return response, session


def test_successful_login():
    """Успешное создание сессии через Redfish API"""
    response, session = get_authenticated_session(VALID_USER, VALID_PASSWORD)
    assert response.status_code == 201, f"Ожидался статус 201 Created, получен {response.status_code}"
    assert "X-Auth-Token" in response.headers, "Сервер должен вернуть X-Auth-Token"

    session_url = response.headers.get("Location")
    if session_url:
        token = response.headers.get("X-Auth-Token")
        requests.delete(
            f"{BASE_URL}{session_url}",
            headers={"X-Auth-Token": token},
            verify=False
        )


def test_invalid_credentials():
    """Отказ в доступе при неверных учетных данных на защищенном эндпоинте"""
    session = requests.Session()
    session.verify = False
    
    response = session.get(
        f"{BASE_URL}/redfish/v1/AccountService/Accounts",
        auth=(VALID_USER, INVALID_PASSWORD),
        timeout=5
    )
    assert response.status_code == 401, f"Ожидался 401 Unauthorized, получен {response.status_code}"


def test_account_lockout():
    """Проверка серии неудачных попыток входа"""
    session = requests.Session()
    session.verify = False

    for _ in range(5):
        resp = session.post(
            f"{BASE_URL}/redfish/v1/SessionService/Sessions",
            json={"UserName": VALID_USER, "Password": INVALID_PASSWORD},
            timeout=5
        )
        assert resp.status_code == 401


def test_power_control_host():
    """Проверка доступа к ресурсам управления питанием (Systems)"""
    resp_login, _ = get_authenticated_session(VALID_USER, VALID_PASSWORD)
    assert resp_login.status_code == 201
    token = resp_login.headers.get("X-Auth-Token")

    session = requests.Session()
    session.verify = False
    session.headers.update({"X-Auth-Token": token})

    resp = session.get(f"{BASE_URL}/redfish/v1/Systems", timeout=5)
    assert resp.status_code == 200
    assert "Members" in resp.json()


def test_inventory_display():
    """Проверка получения инвентарных данных (Chassis/Board)"""
    resp_login, _ = get_authenticated_session(VALID_USER, VALID_PASSWORD)
    assert resp_login.status_code == 201
    token = resp_login.headers.get("X-Auth-Token")

    session = requests.Session()
    session.verify = False
    session.headers.update({"X-Auth-Token": token})

    resp = session.get(f"{BASE_URL}/redfish/v1/Chassis", timeout=5)
    assert resp.status_code == 200
    assert "Members" in resp.json()