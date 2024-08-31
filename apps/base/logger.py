import logging
from copy import deepcopy

logger = logging.getLogger('external_request')


class RequestResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Collect request information
        request_info = {
            'Method': request.method,
            'Path': request.path,
            'Headers': request.META,
            'Body':deepcopy(request.body)
        }

        # Collect response information
        response = self.get_response(request)
        response_info = {
            'Status Code': response.status_code,
            'Headers': response.items(),
            'Content': response.content,
        }

        # Log the combined request and response information
        logger.info("Request-Response Log: %s", {
            'Request': request_info,
            'Response': response_info,
        })
        return response
