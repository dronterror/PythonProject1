class BusinessLogicError(Exception):
    def __init__(self, errorCode: str, detail: str):
        self.errorCode = errorCode
        self.detail = detail 