import datetime
import threading
import time

def parse_version_string():
    import os
    import os.path
    import subprocess
    
    path = os.path.abspath(__file__)
    while os.path.islink(path):
        path = os.path.join(os.path.dirname(path), os.readlink(path))
    path = os.path.dirname(path) # go up one level, from repo/loops.py to repo, where README.md is located
    while os.path.islink(path):
        path = os.path.join(os.path.dirname(path), os.readlink(path))
    try:
        version = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=path).decode('utf-8').strip('\n')
        if version == 'master':
            try:
                with open(os.path.join(path, 'README.md')) as readme:
                    for line in readme.read().splitlines():
                        if line.startswith('This is `python-xdg-basedir` version'):
                            return line.split(' ')[4]
            except:
                pass
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=path).decode('utf-8').strip('\n')
    except:
        pass

__version__ = parse_version_string()

class IterThread(threading.Thread):
    """Helper class used in loops."""
    def __init__(self, iterator):
        super().__init__()
        self.daemon = True
        self.iterator = iterator
        self.stopped = False
    
    def run(self):
        try:
            self.value = next(self.iterator)
        except StopIteration:
            self.stopped = True

class Loop(threading.Thread):
    """Generic loop thread that periodically checks if it should stop while waiting for the iterable to yield.
    
    Keyword-only arguments:
    iterable -- The iterable to be looped over. By default, self.get_iterable is called.
    process_value -- A function which will be called with each yielded value as argument. Defaults to self.process_value.
    sleep_length -- A datetime.timedelta representing how long to sleep between each check for the next value or the stop signal. Defaults to half a second.
    """
    def __init__(self, *, iterable=None, process_value=None, sleep_length=datetime.timedelta(seconds=0.5)):
        super().__init__()
        if iterable is not None:
            self.iterable = iterable
        if process_value is not None:
            self.process_value = process_value
        self.stopped = False
        self.sleep_length = sleep_length
    
    @staticmethod
    def iterable():
        """The iterable to be looped over. Must be overridden in a subclass, or by passing the `iterable' keyword argument to the constructor."""
        raise NotImplementedError('iterable must be overwritten in subclasses, or set explicitly')
    
    def run(self):
        iterator = iter(self.iterable)
        iter_thread = IterThread(iterator)
        iter_thread.start() # get the first value
        while not self.stopped:
            if not iter_thread.is_alive():
                if iter_thread.stopped: # iterator exhausted
                    return
                else: # iterator has yielded a value
                    self.process_value(iter_thread.value)
                    iter_thread = IterThread(iterator)
                    iter_thread.start() # get the next value
            time.sleep(self.sleep_length.total_seconds())
    
    @staticmethod
    def process_value(value):
        """Will be called with each yielded value as argument. Must be overridden in a subclass, or by passing the `process_value' keyword argument to the constructor."""
        raise NotImplementedError('process_value must be overwritten in subclasses, or set explicitly')
    
    def start(self):
        self.stopped = False
        super().start()
    
    def stop(self):
        self.stopped = True
