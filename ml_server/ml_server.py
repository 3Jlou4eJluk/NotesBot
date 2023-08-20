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

from return_data_structures import GetKNearestNotesReturn



# pathes
import ml_server_settings

from sentence_transformers import SentenceTransformer



# some preprocessing actions
ml_api = fastapi.FastAPI()

# tSNE dimension reduction
reducer = TSNE(n_components=2, metric='cosine', perplexity=5)

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
    note_id = db_obj.add_note(note_add_req.name, note_add_req.text)
    
    return {
            'message' : 'Success',
            'note_id' : note_id
            }


@ml_api.get("/ml_api/get_picture")
async def get_picture():
    global db_obj

    embedding_array = db_obj.get_embedding_array()

    if embedding_array.shape[0] < ml_server_settings.TSNE_PERPLEXITY:
        return {'message' : 'There is no enough notes to represent'}

    dots = reducer.fit_transform(embedding_array)
    
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


@ml_api.post("/ml_api/delete_node")
async def delete_node(del_node_id_req: DeleteNoteByIdRequest):
    global db_obj
    db_obj.delete_note(del_node_id_req.note_id)


@ml_api.get('/ml_api/search_note_by_name')
async def search_note_by_name(search_note_req: SearchNoteRequest):
    global db_obj
    note_id = db_obj.search_note_by_name(search_note_req.request_text)
    return {
        'note_id' : str(note_id)
    }

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
    note_name, note_text = db_obj.get_note_by_id(search_note_req.note_id)

    return {
        'note_name': note_name,
        'note_text': note_text
    }

@ml_api.get('/ml_api/get_k_nearest_notes', response_model=GetKNearestNotesReturn)
async def get_k_nearest_notes(get_req: GetKNearestNotesRequest):
    global db_obj

    res_list = db_obj.get_k_nearest_notes(get_req.note_id, get_req.k)
    print("Res list is ", res_list)

    return GetKNearestNotesReturn(numbers=res_list)