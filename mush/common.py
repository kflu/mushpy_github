def expose(*args):
    '''Expose the functino to global namespace.

    After exposing, the global name is set to an attribute in the callable
    object as "global_name"

    Can be used as decorator as well as a function:

    @expose("global_name")
    def func: ...
    
    or

    expose(func, "global name")
    '''
    if len(args) == 2:
        # called as a function
        func, name = args[0:2]
        if not callable(func):
            raise TypeError(func, 'Not callable')   #FIXME
        print "exposing func: %s with name: %s" % (str(func), name)
        #setattr(ax._scriptEngine_.globalNameSpaceModule, name, func.__call__)
        setattr(ax._scriptEngine_.globalNameSpaceModule, name, func)
        # setattr doesn't work on instancemethod for python2.7
        # setattr(func, 'global_name', name)
        func.__func__.global_name = name
        return

    if len(args) == 1:
        # called as a decorator
        name = args[0]
        def CalledOnFunc(func):
            expose(func, name)
            return func
        return CalledOnFunc

