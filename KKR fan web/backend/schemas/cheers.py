from pydantic import BaseModel, Field, field_validator

class CheerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    msg: str = Field(..., min_length=1)

    @field_validator('name', 'msg')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Must not be empty or whitespace only')
        return v.strip()

class CheerResponse(BaseModel):
    name: str
    msg: str
    time: str
