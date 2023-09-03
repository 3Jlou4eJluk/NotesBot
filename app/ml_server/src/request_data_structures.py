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

class CreateLinkRequest(pydantic.BaseModel):
    first_id: int
    second_id: int

class GetSegmentOfNotes(pydantic.BaseModel):
    note_id: int
    k: int
    seg_num: int

class GetNotesListReq(pydantic.BaseModel):
    page_num: int
    notes_per_page: int
