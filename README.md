## Запуск тестов (инструкция для ОС Windows) :

&nbsp;

### Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:an-nastasiia/scan_testing.git
cd scan_testing
```

### Cоздать и активировать виртуальное окружение:

```
py -m venv venv | python -m venv venv | python3 -m venv venv
source venv/scripts/activate
```

### Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

### Установить браузеры для тестирования:

```
playwright install
```

### Запустить тестирование:

```
#  в Chromium
pytest --alluredir=./allure_results

#  в Webkit (Safari)
pytest --alluredir=./allure_results --browser webkit

#  в Firefox
pytest --alluredir=./allure_results --browser firefox

#  во всех трех браузерах
pytest --alluredir=./allure_results --browser chromium --browser webkit --browser firefox
```
### Просмотреть результаты тестирования в Allure:

```
allure serve ./allure_results
```
