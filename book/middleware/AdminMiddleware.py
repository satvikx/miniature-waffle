# middleware.py
import os
from django.http import HttpResponseForbidden
from django.conf import settings

class AdminAPIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_api_key = os.getenv(
            'ADMIN_API_KEY',
            'CUSTOM_API_KEY'
        )

    def __call__(self, request):
        # Check if admin endpoint
        if request.path.startswith('/api/admin/'):
            # Get API key from headers
            api_key = request.headers.get('X-Admin-API-Key')
            
            if api_key != self.admin_api_key:
                return HttpResponseForbidden(f"Invalid Admin API Key{api_key, self.admin_api_key}")
        
        return self.get_response(request)

# Helper function
# def generate_admin_api_key():
#     import secrets
#     return secrets.token_urlsafe(32)