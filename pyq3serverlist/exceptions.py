class PyQ3SLError(Exception):
    pass


class PyQ3SLTimeoutError(PyQ3SLError):
    def __init__(self, message: str):
        super().__init__(message)
