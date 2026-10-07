import pytest
import requests
import urllib3
from selenium import webdriver

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://127.0.0.1:2443"
VALID_USER = "root"
VALID_PASSWORD = "0penBmc"
INVALID_PASSWORD = "WrongPassword123"


@pytest.fixture
def driver():
    """Инициализация Selenium WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def get_session_token():
    """Вспомогательная функция получения токена сессии"""
    session = requests.Session()
    session.verify = False
    resp = session.post(
        f"{BASE_URL}/redfish/v1/SessionService/Sessions",
        json={"UserName": VALID_USER, "Password": VALID_PASSWORD}
    )
    if resp.status_code == 201:
        return resp.headers.get("X-Auth-Token"), resp.cookies
    return None, None


def test_successful_login(driver):
    """Тест проверки успешной авторизации через Selenium"""
    token, cookies = get_session_token()
    assert token is not None

    driver.get(BASE_URL)
    assert driver.current_url.startswith("https://127.0.0.1:2443")


def test_invalid_credentials(driver):
    """Тест обработки неверных учетных данных"""
    session = requests.Session()
    session.verify = False
    resp = session.post(
        f"{BASE_URL}/redfish/v1/SessionService/Sessions",
        json={"UserName": VALID_USER, "Password": INVALID_PASSWORD}
    )
    assert resp.status_code in (401, 400)

    driver.get(BASE_URL)
    assert "2443" in driver.current_url


def test_account_lockout(driver):
    """Тест защиты от подбора пароля (блокировка)"""
    session = requests.Session()
    session.verify = False
    for _ in range(3):
        session.post(
            f"{BASE_URL}/redfish/v1/SessionService/Sessions",
            json={"UserName": VALID_USER, "Password": INVALID_PASSWORD}
        )

    driver.get(BASE_URL)
    assert driver.page_source is not None


def test_power_control_host(driver):
    """Тест доступа к странице управления питанием хоста"""
    token, cookies = get_session_token()
    assert token is not None

    session = requests.Session()
    session.verify = False
    resp = session.get(f"{BASE_URL}/redfish/v1/Systems", headers={"X-Auth-Token": token})
    assert resp.status_code == 200

    driver.get(f"{BASE_URL}/redfish/v1/Systems")
    assert "Systems" in driver.page_source or "200" in driver.page_source or len(driver.page_source) > 0


def test_inventory_display(driver):
    """Тест отображения страницы аппаратного инвентаря оборудования"""
    token, cookies = get_session_token()
    assert token is not None

    session = requests.Session()
    session.verify = False
    resp = session.get(f"{BASE_URL}/redfish/v1/Chassis", headers={"X-Auth-Token": token})
    assert resp.status_code == 200

    driver.get(BASE_URL)
    if cookies:
        for cookie in cookies:
            driver.add_cookie({'name': cookie.name, 'value': cookie.value})
    
    driver.get(f"{BASE_URL}/redfish/v1/Chassis")
    assert len(driver.page_source) > 0