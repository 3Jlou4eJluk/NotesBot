import pydantic

class GetKNearestNotesReturn(pydantic.BaseModel):
    numbers: list[int]

class GetNotesListReturn(pydantic.BaseModel):
    note_id: list[int]
    note_name: list[str]
    note_text: list[str]
    note_date: list[str]
    pages_count: int