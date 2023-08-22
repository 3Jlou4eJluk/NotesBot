import pydantic

# data structures
class NoteAddRequest(pydantic.BaseModel):
    name: str
    text: str

class DeleteNoteByIdRequest(pydantic.BaseModel):
    note_id: int

class SearchNoteRequest(pydantic.BaseModel):
    request_text: str


class GetNoteByIdRequest(pydantic.BaseModel):
    note_id: int

class GetKNearestNotesRequest(pydantic.BaseModel):
    note_id: int
    k: int