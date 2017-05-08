import re
import json
from django.conf import settings


class DjangoLiveSyncMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    @staticmethod
    def process_response(request, response):
        if settings.DEBUG and 'text/html' in response['Content-Type']:
            script_settings = """
                <script type='text/javascript'>
                    window.DJANGO_LIVESYNC = {settings}
                </script>
            """.format(settings=json.dumps(settings.DJANGO_LIVESYNC)).encode('UTF-8')

            script_tag = b"""
                <script src='/static/livesync.js'></script></body>
            """

            pattern = re.compile(b'</body>', re.IGNORECASE)
            response.content = pattern.sub(script_settings + script_tag, response.content)

        return response
