import re
import json
from django.conf import settings


class DjangoLiveSyncMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request, response):
        if settings.DEBUG and response['Content-Type'] == 'text/html':
            script_settings = """
                <script type='text/javascript'>
                    window.DJANGO_LIVESYNC = {settings}
                </script>
            """.format(settings=json.dumps(settings.DJANGO_LIVESYNC))

            script_tag = """
                <script src='/static/livesync.js'></script></body>
            """

            pattern = re.compile(b'</body>', re.IGNORECASE)
            response.content = pattern.sub(script_settings + script_tag, response.content)

        return response
