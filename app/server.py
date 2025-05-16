from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
from datetime import datetime
from decimal import Decimal
from urllib.parse import urlparse, parse_qs
from app.resources import (
    appointments, medspas, services,
    service_categories, service_types,
    service_products, service_product_suppliers
)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# Routing table with patterns
ROUTES = {
    'GET': {
        r'^/appointments$': appointments.get_all,
        r'^/appointments/(\d+)$': appointments.get_by_id,
        r'^/medspas$': medspas.get_all,
        r'^/medspas/(\d+)$': medspas.get_by_id,
        r'^/medspas/(\d+)/services$': services.get_all_by_medspa,
        r'^/services/(\d+)$': services.get_by_id,
        r'^/service-categories$': service_categories.get_all,
        r'^/service-types$': service_types.get_all,
        r'^/service-products$': service_products.get_all,
        r'^/service-product-suppliers$': service_product_suppliers.get_all
    },
    'POST': {
        r'^/appointments$': appointments.create,
        r'^/medspas$': medspas.create,
        r'^/services$': services.create,
        r'^/service-categories$': service_categories.create,
        r'^/service-types$': service_types.create,
        r'^/service-products$': service_products.create,
        r'^/service-product-suppliers$': service_product_suppliers.create
    },
    'PUT': {
        r'^/appointments/(\d+)$': appointments.update,
        r'^/services/(\d+)$': services.update
    },
    'DELETE': {
        r'^/medspas/(\d+)$': medspas.delete
    }
}

class RequestHandler(BaseHTTPRequestHandler):
    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, cls=CustomJSONEncoder).encode())

    def parse_query_params(self):
        """Parse query parameters from the URL"""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        # Convert lists to single values where appropriate
        return {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

    def find_handler(self, method):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        routes = ROUTES.get(method, {})
        for pattern, handler in routes.items():
            match = re.match(pattern, path)
            if match:
                return handler, match.groups()
        return None, None

    def do_GET(self):
        handler, params = self.find_handler('GET')
        if handler:
            query_params = self.parse_query_params()
            if params:
                status_code, data = handler(*params)
            else:
                status_code, data = handler(query_params) if query_params else handler()
            self.send_json_response(status_code, data)
        else:
            self.send_json_response(404, {"error": "Not found"})

    def do_POST(self):
        handler, params = self.find_handler('POST')
        if handler:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            status_code, response_data = handler(data, *params) if params else handler(data)
            self.send_json_response(status_code, response_data)
        else:
            self.send_json_response(404, {"error": "Not found"})

    def do_PUT(self):
        handler, params = self.find_handler('PUT')
        if handler:
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data.decode())
            
            status_code, response_data = handler(data, *params)
            self.send_json_response(status_code, response_data)
        else:
            self.send_json_response(404, {"error": "Not found"})

    def do_DELETE(self):
        handler, params = self.find_handler('DELETE')
        if handler:
            status_code, response_data = handler(*params)
            self.send_json_response(status_code, response_data)
        else:
            self.send_json_response(404, {"error": "Not found"})

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), RequestHandler)
    print('Server running on port 8000...')
    server.serve_forever() 