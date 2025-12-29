import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request

class CurrencyProxyHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP запросов для проксирования курсов валют."""
    
    def do_GET(self):
        # Извлекаем код валюты из пути
        path = self.path.strip('/')
        if not path:
            self.send_error_response(400, "Currency code is required. Example: /USD")
            return
        
        currency_code = path.split('/')[0].upper()
        if len(currency_code) != 3 or not currency_code.isalpha():
            self.send_error_response(400, f"Invalid currency code: {currency_code}")
            return
        
        try:
            # Запрос к внешнему API
            url = f"https://api.exchangerate-api.com/v4/latest/{currency_code}"
            req = urllib.request.Request(url, headers={'User-Agent': 'CurrencyProxy/1.0'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read()
                
                # Проверяем, не является ли ответ ошибкой
                result = json.loads(data)
                if 'error' in result and result['error'] == 'Invalid base currency':
                    self.send_error_response(404, f"Currency not found: {currency_code}")
                    return
                
                # Отправляем успешный ответ
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.send_error_response(404, f"Currency not found: {currency_code}")
            else:
                self.send_error_response(502, f"External API error: {e.code}")
        except urllib.error.URLError as e:
            self.send_error_response(502, f"Cannot connect to exchange rate API: {str(e)}")
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    def send_error_response(self, status_code, message):
        """Отправляет JSON ответ с ошибкой."""
        error_data = {
            "error": True,
            "status_code": status_code,
            "message": message
        }
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(error_data).encode('utf-8'))


def run_server(port=8000):
    """Запускает HTTP сервер."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CurrencyProxyHandler)
    print(f"Starting server on port {port}")
    print(f"Test with: http://localhost:{port}/USD")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()