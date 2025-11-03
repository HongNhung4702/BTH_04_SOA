import requests
from django.http import JsonResponse
from django.conf import settings

class ProductJWTAuthMiddleware:
    """
    Middleware kiểm tra JWT trong header Authorization
    để xác thực các request đến product_service.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'error': 'Authorization header missing'}, status=401)

        try:
            token = auth_header.split(' ')[1]
        except Exception:
            return JsonResponse({'error': 'Invalid Authorization header'}, status=401)

        try:
            # Verify token via Auth service (TH2)
            verify_url = getattr(settings, 'AUTH_VERIFY_URL', 'http://127.0.0.1:8000/auth/')
            resp = requests.post(verify_url, json={'token': token}, timeout=5)
            if resp.status_code != 200:
                return JsonResponse({'error': 'Unauthorized'}, status=401)
            data = resp.json() or {}
            request.user_id = data.get('user_id')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=401)

        response = self.get_response(request)
        return response
