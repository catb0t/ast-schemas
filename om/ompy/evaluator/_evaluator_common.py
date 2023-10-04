
class _SkipEnd:
    def __init__(self):
        pass

    def __eq__(self, rhs):
        return self is rhs

SkipEnd = _SkipEnd()
