from livesync.fswatcher.handlers import BaseEventHandler
from livesync.asyncserver import dispatcher


class LiveReloadRequestHandler(BaseEventHandler):
    @property
    def extensions(self):
        return ['*.js', '*.css', '*.htm', '*.html',]

    def handle(self, event):
        dispatcher.dispatch('refresh')
