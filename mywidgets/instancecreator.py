
def createInstance(self, parent, cls:str) -> any:
    # returns an instance of desired class cls
    parts = cls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m(parent)