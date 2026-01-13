"""
Custom middleware for error handling and logging.
This ensures all 500 errors are properly logged and users see a friendly error page.
"""
import logging
import traceback
from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger('team')


class ErrorHandlerMiddleware:
    """
    Middleware to catch unhandled exceptions and:
    1. Log them with full traceback
    2. Return a friendly error page
    3. For API requests, return JSON error response
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        """Handle exceptions that occur during request processing."""
        # Log the full error with traceback
        logger.error(
            f"🔥 UNHANDLED EXCEPTION in {request.path}\n"
            f"User: {request.user}\n"
            f"Method: {request.method}\n"
            f"Error: {str(exception)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        
        # Check if this is an API request (expects JSON)
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'error': 'Internal server error',
                'detail': str(exception) if hasattr(request, 'user') and request.user.is_staff else 'An error occurred',
            }, status=500)
        
        # Return None to let Django's default error handling take over
        # (which will use our custom 500.html template)
        return None


class TemplateErrorMiddleware:
    """
    Middleware to catch template rendering errors specifically.
    These are common causes of 500 errors.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Log template errors with context
            logger.error(
                f"🎨 TEMPLATE ERROR in {request.path}\n"
                f"Error: {str(e)}\n"
                f"Type: {type(e).__name__}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise
