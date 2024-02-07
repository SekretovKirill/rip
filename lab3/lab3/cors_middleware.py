class CorsMiddleware:
    def init(self, get_response):
        self.get_response = get_response

    def call(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "DELETE, GET, OPTIONS, PATCH, POST, PUT"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response