from watchdog.observers import Observer


class FileWatcher(object):
    def __init__(self):
        self.handlers = set()
        self.observer = Observer()

    def _schedule_all(self):
        for handler in self.handlers:
            for path in handler.watched_paths:
                self.observer.schedule(handler, path, recursive=True)

    def add_handler(self, handler):
        self.handlers.add(handler)

    def start(self):
        self._schedule_all()
        self.observer.start()

    def stop(self):
        self.observer.stop()
