import mush
mush.init(ax) # it must be initialized before using

from mush.task import Task, maketrigger

class TestTask(Task):
    def __init__(self):
        # constructor is no necessary if it doesn't take additional arguments
        super(TestTask, self).__init__()

    @maketrigger("blah")
    def onBlah(self, wc):
        print "wc:", wc

t = TestTask()
t.enable_all()
