from greenlet import greenlet
from trigger import *
from common import *

class Task(greenlet):
    _func2pattern = {}

    def __init__(self):
        self._trig_state = {} # func : on/off
        self._register_trigs()

    def _register_trigs(self):
        for func in self._func2pattern:
            class_name = func.im_class.__name__
            func_name = func.im_func.__name__
            global_name = "g__{0}__{1}__{2}".format(class_name, func_name, id(func))
            expose(func, func.global_name)
            add_trigger(name=func.global_name, pattern=self._func2pattern[func],
                    script=func.global_name)

    def enable_all(self, store_state=True):
        if store_state:
            self._store_trig_state()
        for func in self._func2pattern:
            enable_trigger(name=func.global_name)

    def disable_all(self, store_state=True):
        if store_state:
            self._store_trig_state()
        for func in self._func2pattern:
            disable_trigger(name=func.global_name)

    def delete_all(self):
        self.disable_all(store_state=False)
        for func in self._func2pattern:
            del_trigger(name=func.global_name)

    def _store_trig_state(self):
        self._trig_state = {}
        for func in self._func2pattern:
            self._trig_state[func] = get_trig_onoff(name=func.global_name)

    def _resume_trig_state(self):
        for func in self._trig_state:
            set_trig_onoff(func.global_name, self._trig_state[func])
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

    @staticmethod
    def trigger(pattern):
        def wrapper(func):
            Task._func2pattern[func] = pattern
            return func
        return wrapper

