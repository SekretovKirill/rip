# middlewares.py
from django.middleware.common import CommonMiddleware

class Cors(CommonMiddleware):
    def process_response(self, request, response):
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return super().process_response(request, response)
