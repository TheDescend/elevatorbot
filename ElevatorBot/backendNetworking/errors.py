class BackendException(Exception):
    """This gets raised when a backend connection raised a CustomException (409) and we responded to it"""

    def __init__(
        self,
        error: str,
    ):
        self.error = error
