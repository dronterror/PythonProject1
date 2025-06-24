from pydantic import BaseModel

class APIError(BaseModel):
    errorCode: str
    detail: str 