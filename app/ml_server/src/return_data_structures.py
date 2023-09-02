import pydantic

class GetKNearestNotesReturn(pydantic.BaseModel):
    numbers: list[int]
