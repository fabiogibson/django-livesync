from watchdog.events import PatternMatchingEventHandler
from .utils import get_md5


class BaseEventHandler(PatternMatchingEventHandler):
    @property
    def extensions(self):
        pass

    def handle(self, event): # pragma: no cover
        pass

    def __init__(self):
        super(BaseEventHandler, self).__init__(ignore_directories=True, patterns=self.extensions)
        self.history = dict()

    def _remove_from_history(self, path):
        if path in self.history:
            del self.history[path]

    def _update_history(self, path):
        md5hash = get_md5(path)

        if self.history.get(path) == md5hash:
            return False

        self.history[path] = md5hash
        return True

    def on_deleted(self, event):
        self._remove_from_history(event.src_path)
        self.handle(event)

    def on_moved(self, event):
        self._remove_from_history(event.src_path)
        self._update_history(event.dest_path)
        self.handle(event)

    def on_modified(self, event):
        if self._update_history(event.src_path):
            self.handle(event)
