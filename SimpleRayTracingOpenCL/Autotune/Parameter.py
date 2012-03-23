class Parameter(object):
    """Parameter class"""
    def __init__(self, name, start, stop=None, stride=None):
        self.name = name
        self.start = start
        if stop != None:
            self.stop = stop
            self.stride = stride