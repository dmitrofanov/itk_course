import json
import requests


# WSGI-совместимое приложение для использования с Gunicorn и другими WSGI-серверами
def wsgi_app(environ, start_response):
    """
    WSGI-приложение для проксирования курсов валют.
    
    Использование:
    gunicorn currency_proxy:wsgi_app
    waitress-serve --listen=*:8000 currency_proxy:application
    """
    my_headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')
    ]

    # Определяем метод запроса
    method = environ.get('REQUEST_METHOD', 'GET')
    if method != 'GET':
        start_response('405 Method Not Allowed', my_headers)
        return [json.dumps({
            "error": True,
            "status_code": 405,
            "message": "Method Not Allowed"
        }).encode('utf-8')]
    
    # Извлекаем путь
    path = environ.get('PATH_INFO', '').strip('/')
    if not path:
        start_response('400 Bad Request', my_headers)
        return [json.dumps({
            "error": True,
            "status_code": 400,
            "message": "Currency code is required. Example: /USD"
        }).encode('utf-8')]
    
    # Извлекаем код валюты
    currency_code = path.split('/')[0].upper()
    if len(currency_code) != 3 or not currency_code.isalpha():
        start_response('400 Bad Request', my_headers)
        return [json.dumps({
            "error": True,
            "status_code": 400,
            "message": f"Invalid currency code: {currency_code}"
        }).encode('utf-8')]
    
    try:
        # Запрос к внешнему API
        url = f"https://api.exchangerate-api.com/v4/latest/{currency_code}"
        headers = {'User-Agent': 'CurrencyProxy/1.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Проверяем статус ответа
        if response.status_code == 404:
            start_response('404 Not Found', my_headers)
            return [json.dumps({
                "error": True,
                "status_code": 404,
                "message": f"Currency not found: {currency_code}"
            }).encode('utf-8')]
        
        # Проверяем, не является ли ответ ошибкой
        try:
            result = response.json()
            if 'error' in result and result['error'] == 'Invalid base currency':
                start_response('404 Not Found', my_headers)
                return [json.dumps({
                    "error": True,
                    "status_code": 404,
                    "message": f"Currency not found: {currency_code}"
                }).encode('utf-8')]
        except json.JSONDecodeError:
            pass
        
        # Отправляем успешный ответ
        start_response(f'{response.status_code} OK', my_headers)
        return [response.content]
        
    except requests.exceptions.Timeout:
        start_response('504 Gateway Timeout', my_headers)
        return [json.dumps({
            "error": True,
            "status_code": 504,
            "message": "Request to exchange rate API timed out"
        }).encode('utf-8')]
    except requests.exceptions.ConnectionError:
        start_response('502 Bad Gateway', my_headers)
        return [json.dumps({
            "error": True,
            "status_code": 502,
            "message": "Cannot connect to exchange rate API"
        }).encode('utf-8')]
    except requests.exceptions.RequestException as e:
        start_response('502 Bad Gateway', my_headers)
        return [json.dumps({
            "error": True,
            "status_code": 502,
            "message": f"Error connecting to exchange rate API: {str(e)}"
        }).encode('utf-8')]
    except Exception as e:
        start_response('500 Internal Server Error', my_headers)
        return [json.dumps({
            "error": True,
            "status_code": 500,
            "message": f"Internal server error: {str(e)}"
        }).encode('utf-8')]


# Для совместимости с WSGI серверами
application = wsgi_app