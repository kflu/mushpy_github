from greenlet import greenlet, getcurrent
from trigger import *
from common import *
from types import MethodType

# TODO need to have _func2pattern per each class rather than instance.
# _func2pattern needs to be setup upon class creation

def _get_main_greenlet():
    current = getcurrent()
    while current.parent != None:
        current = current.parent
    return current
main = _get_main_greenlet()

class Task(greenlet):
    """Collection of triggers and a greenlet.

    triggers are registered at instantiation. To define a trigger handler:

        >>> @Task.trigger("pattern_regex")
        >>> def onPattern(self, wildcards):
        >>>     # wildcards is a length 10 array holding the wildcards
        >>>     # The 10-th one is the whole line
        >>>     pass

    The coroutine should be defined in method "run" (refer to greenlet doc):

        >>> def run(self, *args):
        >>>     pass

    To run it, run

        >>> instance.switch(args)

    """

    @classmethod
    def trigger(cls, pattern):
        def wrapper(func):
            # Note that here "func" is a function rather than method In order
            # to reference it later when class instantiates, we have to
            # identify it by the name.
            def newfunc(self, trig_name, line, wc):
                # Bound the function object to class instance "self" and then
                # invoke
                MethodType(func, self, type(self))(wc)
            newfunc.pattern = pattern
            return newfunc
        return wrapper

    def __init__(self):
        super(Task, self).__init__()
        self._func2pattern = {} # func_name : trig_pattern
        self._trig_state = {} # func_name : on/off
        self._register_trigs() 

    def __getitem__(self, key):
        '''Get bound method by its name'''
        return getattr(self, key)

    def _register_trigs(self):
        for func in dir(self):
            print func
            try:
                if callable(getattr(self, func)) and "pattern" in dir(getattr(self, func)):
                    self._func2pattern[func] = getattr(self, func).pattern
                    class_name = self.__class__.__name__
                    global_name = "g__{0}__{1}__{2}".format(class_name, func, id(self))
                    expose(self[func], global_name)
                    add_trigger(name=global_name, pattern=self._func2pattern[func],
                            script=global_name)
            except AttributeError: # greelet.run doesn't like dir() on it
                pass

    def enable_all(self, store_state=True):
        if store_state:
            self._store_trig_state()
        for func in self._func2pattern:
            enable_trigger(name=self[func].global_name)

    def disable_all(self, store_state=True):
        if store_state:
            self._store_trig_state()
        for func in self._func2pattern:
            disable_trigger(name=self[func].global_name)

    def delete_all(self):
        self.disable_all(store_state=False)
        for func in self._func2pattern:
            del_trigger(name=self[func].global_name)

    def _store_trig_state(self):
        self._trig_state = {}
        for func in self._func2pattern:
            self._trig_state[func] = get_trig_onoff(name=self[func].global_name)

    def _resume_trig_state(self):
        for func in self._trig_state:
            set_trig_onoff(self[func].global_name, self._trig_state[func])
    resume = _resume_trig_state

    def _turn_onoff(self, func_or_list, on):
        if not isinstance(func_or_list, list):
            func_or_list = [func_or_list]
        for func in func_or_list:
            if on:
                enable_trigger(name=func.global_name)
            else:
                disable_trigger(name=func.global_name)

    def enable(self, func_or_list):
        self._turn_onoff(func_or_list, on=True)

    def disable(self, func_or_list):
        self._turn_onoff(func_or_list, on=False)

    def sw(self, task, *args, **kw):
        self.disable_all()
        result = task.switch(*args, **kw)
        self.resume()
        return result

    def switch_to_main(self):
        """Switch to the main greenlet"""
        return main.switch()

maketrigger = Task.trigger
