import datetime
import threading
import time

try:
    from loops.version import __version__
except ImportError:
    __version__ = None

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
    on_exception -- What to do when an exception occurs in process_value. If given, must be an iterable of actions, which will be done in order. Possible actions are 'log_stdout' (write traceback to sys.stdout), 'log_stderr' (write traceback to sys.stderr), or 'raise' (the default; lets the exception through to threading's default handling). Set to an empty iterable to ignore exceptions and continue the loop.
    process_value -- A function which will be called with each yielded value as argument. Defaults to self.process_value.
    sleep_length -- A datetime.timedelta representing how long to sleep between each check for the next value or the stop signal. Defaults to half a second.
    """
    def __init__(self, *, iterable=None, on_exception=('raise',), process_value=None, sleep_length=datetime.timedelta(seconds=0.5)):
        super().__init__()
        if iterable is None:
            self.iterable = self.iterable()
        else:
            self.iterable = iterable
        self.on_exception = tuple(on_exception)
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
                    try:
                        self.process_value(iter_thread.value)
                    except:
                        for exception_action in self.on_exception:
                            if exception_action == 'log_stdout':
                                traceback.print_exc(file=sys.stdout)
                            elif exception_action == 'log_stderr':
                                traceback.print_exc(file=sys.stderr)
                            elif exception_action == 'raise':
                                raise
                            else:
                                raise ValueError('Unrecognized exception action: {!r}'.format(exception_action))
                    iter_thread = IterThread(iterator)
                    iter_thread.start() # get the next value
                    continue
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

def timeout_single(iterable, timeout, sleep_length=datetime.timedelta(seconds=0.5)):
    """This function creates an iterator that yields from the given iterable, but aborts when the iterable takes too long to yield a value.

    Required arguments:
    iterable -- The iterable to yield from.
    timeout -- A datetime.timedelta representing the maximum time the iterable may take to produce a single value. If any iteration step takes longer than this, the iteration is aborted.

    Optional arguments:
    sleep_length -- A datetime.timedelta representing how long to sleep between each check for the next value. Will be truncated to the remainder of the timeout. Defaults to half a second.

    Yields:
    The values from `iterable', until it is exhausted or `timeout' is reached.
    """
    iterator = iter(iterable)
    current_timeout = timeout
    iter_thread = IterThread(iterator)
    iter_thread.start() # get the first value
    while current_timeout > datetime.timedelta():
        current_sleep_length = min(sleep_length, current_timeout)
        time.sleep(current_sleep_length.total_seconds())
        current_timeout -= current_sleep_length
        if not iter_thread.is_alive():
            if iter_thread.stopped: # iterator exhausted
                return
            else: # iterator has yielded a value
                yield iter_thread.value
                current_timeout = timeout
                iter_thread = IterThread(iterator)
                iter_thread.start() # get the next value

def timeout_total(iterable, timeout, sleep_length=datetime.timedelta(seconds=0.5)):
    """This function creates an iterator that yields from the given iterable, but aborts after a timeout.

    Required arguments:
    iterable -- The iterable to yield from.
    timeout -- A datetime.timedelta representing how long after iteration is started it should be aborted.

    Optional arguments:
    sleep_length -- A datetime.timedelta representing how long to sleep between each check for the next value. Will be truncated to the remainder of the timeout. Defaults to half a second.

    Yields:
    The values from `iterable', until it is exhausted or `timeout' is reached.
    """
    iterator = iter(iterable)
    current_timeout = timeout
    iter_thread = IterThread(iterator)
    iter_thread.start() # get the first value
    while current_timeout > datetime.timedelta():
        current_sleep_length = min(sleep_length, current_timeout)
        time.sleep(current_sleep_length.total_seconds())
        current_timeout -= current_sleep_length
        if not iter_thread.is_alive():
            if iter_thread.stopped: # iterator exhausted
                return
            else: # iterator has yielded a value
                yield iter_thread.value
                iter_thread = IterThread(iterator)
                iter_thread.start() # get the next value
