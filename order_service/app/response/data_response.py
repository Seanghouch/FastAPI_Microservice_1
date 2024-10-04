from pydantic import BaseModel


class ResponseData(BaseModel):
    code: int
    message: str
    data: object = None


class ResponseDataList(BaseModel):
    code: int
    message: str
    total_record: int
    data: object = None