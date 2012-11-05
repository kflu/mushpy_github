from datetime import datetime
class Terminal:
    '''Terminal.

    Options:
        time_stamp: prefix a time stamp to each line, default to False
        prompt_to_save: prompt to save on exit, default to False
        read_only: if the notepad is readonly. default to True
    '''

    def __init__(self, title="stdout", **options):
        self.title = title

        self.options = options
        self.options['time_stamp'] = options.get('time_stamp', False)
        self.options['prompt_to_save'] = options.get('prompt_to_save', False)
        self.options['read_only'] = options.get('read_only', True)

        # Have to write to a notepad first, then the NotepadSaveMethod() call can take effect.
        self.write("Initializing...\r\n")

        if self.options['prompt_to_save']:
            world.NotepadSaveMethod(self.title, 1)
        else:
            world.NotepadSaveMethod(self.title, 2)

        world.NotepadReadOnly(self.title, self.options['read_only'])

    def write(self, what):
        if self.options['time_stamp']:
            if what.strip():
                what = datetime.now().strftime("%c")+": "+what
        what = what.replace('\n', '\r\n')
        world.appendtonotepad(self.title, what)

    def flush(self):
        pass

    def __getattr__(self, name):
        return self.__call_any

    def __call_any(self, *args, **kwargs):
        pass

