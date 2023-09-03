import fastapi
import pickle
import numpy as np
import pandas as pd
import umap
import io
import matplotlib.pyplot as plt
import base64


from sklearn.manifold import TSNE
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from database import DataBase

from request_data_structures import NoteAddRequest
from request_data_structures import DeleteNoteByIdRequest
from request_data_structures import SearchNoteRequest
from request_data_structures import GetNoteByIdRequest
from request_data_structures import GetKNearestNotesRequest
from request_data_structures import GetSegmentOfNotes
from request_data_structures import GetNotesListReq

from return_data_structures import GetKNearestNotesReturn
from request_data_structures import CreateLinkRequest
from return_data_structures import GetNotesListReturn

from fastapi.responses import JSONResponse



# pathes
import ml_server_settings

from sentence_transformers import SentenceTransformer



ml_api = fastapi.FastAPI()

# some preprocessing actions
db_obj = DataBase()

@ml_api.get("/")
async def get_req():
    return {"message" : "Do some important queries, stupid lil shit."}


@ml_api.get("/about")
async def about():
    return {"message" : "This is ML server for my Telegram Bot. You are welcome! \
            But don't destroy anything. Because, I'll destroy YOU."}


@ml_api.post("/ml_api/add_note")
async def add_note(note_add_req: NoteAddRequest):
    global db_obj
    # computing embeddings
    try:
        note_id = db_obj.add_note(note_add_req.name, note_add_req.text)
        print('Note id is ', type(note_id))
        return {
            'message' : 'Success',
            'note_id' : int(note_id)
            }
    except:
        return {
            'message' : 'Success',
            'note_id' : -1
        }
    
    


@ml_api.get("/ml_api/get_picture")
async def get_picture():
    global db_obj

    embedding_array = db_obj.get_embedding_array()

    if embedding_array.shape[0] < ml_server_settings.TSNE_PERPLEXITY:
        return {'message' : 'There is no enough notes to represent'}

    db_obj.compute_low_dim_repr()
    dots = db_obj.low_dim_repr
    
    fig = Figure()

    ax = fig.subplots()
    ax.plot(dots[:, 0], dots[:, 1])
    
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)


    image_string = base64.b64encode(buffer.getvalue()).decode('utf-8')


    return {
        'plot': image_string,
        'file_extension': '.png'
    }

@ml_api.get("/ml_api/sync_vault")
async def sync_vault():
    global db_obj

    db_obj.sync_vault()

    return {
        'message' : 'Data dumped successfully'
    }


@ml_api.post("/ml_api/delete_note")
async def delete_note(del_node_id_req: DeleteNoteByIdRequest):
    global db_obj
    db_obj.delete_note(del_node_id_req.note_id)


@ml_api.get('/ml_api/search_note_by_name')
async def search_note_by_name(search_note_req: SearchNoteRequest):
    global db_obj
    note_id = db_obj.search_note_by_name(search_note_req.request_text)
    return {
        'note_id' : str(note_id)
    }

@ml_api.get('/ml_api/get_notes_list', response_model=GetNotesListReturn)
async def get_notes_list(req: GetNotesListReq):
    global db_obj
    page_num = req.page_num
    notes_per_page = req.notes_per_page
    notes_data_dict, pages_count = db_obj.get_notes_list(page_num=page_num, notes_per_page=notes_per_page)
    ret_struct = GetNotesListReturn(
        note_id = notes_data_dict['note_id'],
        note_name = notes_data_dict['note_name'],
        note_text=notes_data_dict['note_text'],
        note_date=notes_data_dict['note_date'],
        pages_count=pages_count
    )
    return ret_struct

@ml_api.get('/ml_api/search_note_by_text')
async def search_note_by_name(search_note_req: SearchNoteRequest):
    global db_obj
    note_id = db_obj.search_note_by_text(search_note_req.request_text)
    return {
        'note_id' : str(note_id)
    }

@ml_api.get('/ml_api/get_note_by_id')
async def get_note_by_id(search_note_req: GetNoteByIdRequest):
    global db_obj
    note_name, note_text, date_create = db_obj.get_note_by_id(search_note_req.note_id)
    resp_json = {'note_name': note_name, 'note_text': note_text, 'date_create': date_create}

    # resp = JSONResponse(content=resp_json)
    return resp_json

@ml_api.get('/ml_api/get_k_nearest_notes', response_model=GetKNearestNotesReturn)
async def get_k_nearest_notes(get_req: GetKNearestNotesRequest):
    global db_obj

    res_list = db_obj.get_k_nearest_notes(get_req.note_id, get_req.k)
    print("Res list is ", res_list)

    return GetKNearestNotesReturn(numbers=res_list)


@ml_api.post('/ml_api/create_link')
async def create_link(req: CreateLinkRequest):
    global db_obj

    first_id = req.first_id
    second_id = req.second_id

    try:
        db_obj.create_link(first_id, second_id)
        return {
            'status': 'success'
        }
    except:
        return {
            'status': 'error'
        }

@ml_api.get('/ml_api/get_segment_notes', response_model=GetKNearestNotesReturn)
async def get_segment_notes(req: GetSegmentOfNotes):
    global db_obj

    list_of_notes = db_obj.get_segment_notes(note_id=req.note_id, k=req.k, seg_num=req.seg_num)
    return GetKNearestNotesReturn(numbers=list_of_notes)

@ml_api.get('ml_api/get_status')
async def get_status():
    global db_obj
    res = {}
    return res

@ml_api.get('ml_api/erase_db')
async def erase_db():
    global db_obj





