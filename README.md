# Лабораторная работа №4: Автотесты для Web UI с использованием Selenium

Автоматизированные UI-тесты для проверки функционала веб-интерфейса OpenBMC с помощью Python, Selenium WebDriver и pytest.

## Покрытие тестами
* `test_successful_login` — Успешная авторизация в веб-интерфейсе.
* `test_invalid_credentials` — Обработка ошибки при вводе неверных учетных данных.
* `test_account_lockout` — Проверка поведения формы при серии неудачных входов.
* `test_power_control_host` — Переход на страницу управления питанием сервера.
* `test_inventory_display` — Отображение аппаратного инвентаря оборудования.

## Запуск тестов
```bash
python3 -m venv venv
source venv/bin/activate
pip install pytest selenium
pytest openbmc_auth_tests.py -v