class _NoLastID:
    def __init__(self):
        pass

    def __eq__(self, rhs):
        return self is rhs

    def __repr__(self):
        return "(NoLastID)"


NoLastID = _NoLastID()
