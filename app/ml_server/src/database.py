import numpy as np
import pandas as pd
import ml_server_settings
import umap

from datetime import datetime as dt

from sentence_transformers import SentenceTransformer, util
from sklearn.manifold import TSNE

from database_settings import DATE_FORMAT



class DataBase:
    def __init__(self):
        try:
            self.embeddings_df = pd.read_json(ml_server_settings.EMBEDDING_DB_PATH)
        except:
            print('Error: embeddings database not found')
            self.embeddings_df = pd.DataFrame(data=None, columns=['note_name', 
                                                                  'note_text',
                                                                  'note_id',
                                                                  'date_create',
                                                                  'note_embedding'])
            
        try:
            self.link_df = pd.read_json(ml_server_settings.LINK_DB_PATH)
        except:
            print('Error: link database not found')
            self.link_df = pd.DataFrame(data=None, columns=['link_id', 'first_id', 'second_id'])

        self.model = SentenceTransformer(ml_server_settings.SENTENCE_TRANSFORMERS_MODEL)
        self.last_id = (self.embeddings_df['note_id'].max() + 1 if self.embeddings_df.shape[0] > 0 else 0)
        self.last_link_id = (self.link_df['link_id'].max() + 1 if self.link_df.shape[0] > 0 else 0)

        self.reducer = umap.UMAP(n_components=ml_server_settings.TSNE_PERPLEXITY, metric='cosine')
        self.reduced_repr = None
        self.auto_sync_flag = True
        self.low_dim_repr_df = None
    
    def add_note(self, name: str, text: str) -> int:
        note_emb = self.model.encode(text)
        self.embeddings_df = self.embeddings_df._append({'note_name': name, 'note_text': text, 'date_create': dt.strftime(dt.today(), DATE_FORMAT),
                                                         'note_id': self.last_id, 'note_embedding': note_emb}, ignore_index=True)

        if self.auto_sync_flag:
            self.sync_vault()

        self.last_id += 1
        
        # We need to rebuild low_dim repr
        self.low_dim_repr_df = None

        return self.last_id - 1
    
    def search_note_by_name(self, name: str) -> int:
        """
            Returns note_id
        """
        search_embedding = self.model.encode(name)
        max_cos_sim = -10
        max_note_id = None
        for pos in range(self.embeddings_df.shape[0]):
            row = self.embeddings_df.iloc[pos]
            row_embedding = self.model.encode(row['note_name'])
            cs = util.cos_sim(row_embedding, search_embedding)
            if cs > max_cos_sim:
                max_cos_sim = cs
                max_note_id = row.note_id
        return max_note_id

    def search_note_by_text(self, text: str) -> int:
        '''
            Returns note_id
        '''
        search_embedding = self.model.encode(text)
        max_cos_sim = -10
        max_note_id = None
        for pos in range(self.embeddings_df.shape[0]):
            row = self.embeddings_df.iloc[pos]
            cs = util.cos_sim(search_embedding, row['note_embedding'])
            if cs > max_cos_sim:
                max_cos_sim = cs
                max_note_id = row.note_id
        return max_note_id
    
    def delete_note(self, note_id: int) -> None:
        needed_row_index = self.embeddings_df[self.embeddings_df.note_id == note_id]
        if needed_row_index.shape[0] == 0:
            print('There is no notes to delete')
        self.embeddings_df.drop(labels=needed_row_index.index, inplace=True)

        if self.auto_sync_flag:
            self.sync_vault()

        # we will rebuid low dim representation in near future
        self.low_dim_repr_df = None

    def get_embedding_array(self) -> np.ndarray:
        if self.embeddings_df.shape[0] == 0:
            return None
        ret_array = np.zeros((self.embeddings_df.shape[0], self.embeddings_df[0].shape[0]))
        for i in range(self.embeddings_df.shape[0]):
            ret_array[i] = self.embeddings_df.iloc[i]['note_embedding']
        return ret_array
    
    def sync_vault(self) -> None:
        self.embeddings_df.to_json(ml_server_settings.EMBEDDING_DB_PATH)

    def sync_links(self) -> None:
        self.link_df.to_json(ml_server_settings.LINK_DB_PATH)

    def get_note_by_id(self, note_id) -> tuple[str, str]:
        needed_slice = self.embeddings_df[self.embeddings_df['note_id'] == note_id]
        if needed_slice.shape[0] == 0:
            return None, None, None
        else:
            return needed_slice.iloc[0]['note_name'], needed_slice.iloc[0]['note_text'], needed_slice.iloc[0]['date_create']
    
    def get_k_nearest_notes(self, note_id, k) -> list[tuple[str, str]]:
        search_in_reduced_space_flag = ml_server_settings.TSNE_PERPLEXITY < self.embeddings_df.shape[0]

        res_list = []
        if search_in_reduced_space_flag:
            # recomputing tsne representation
            self.compute_low_dim_repr()
            
            search_df = self.low_dim_repr_df
            note_mask = search_df['note_id'] == note_id
            search_without_note_df = search_df[~note_mask]
            note_row = search_df[note_mask][0]
            distance_arr = (search_without_note_df['representation'] - note_row) ** 2
            search_df['distance'] = distance_arr
            search_df.sort_values(by='distance', ascending=False)
            needed_slice = search_df.iloc[:min(k, search_df.shape[0])]
            res_list = list(needed_slice['note_id'])
        else:
            note_id_mask = self.embeddings_df['note_id'] == note_id

            request_note_embedding = self.embeddings_df[note_id_mask]['note_embedding'].iloc[0]
            search_data = self.embeddings_df[~note_id_mask]
            search_data['cos_sim'] = search_data['note_embedding'].apply(lambda x: util.cos_sim(x, request_note_embedding))
            sorted_data = search_data.sort_values(by='cos_sim', ascending=False)
            for i in range(min(k, sorted_data.shape[0])):
                res_list.append(sorted_data.iloc[i]['note_id'])
        
        return res_list
    
    def compute_low_dim_repr(self):
        if self.low_dim_repr_df is None:
            return None
        low_dim_repr = self.reducer.fit_transform(self.embeddings_df['note_embedding'])
        self.low_dim_repr_df = pd.DataFrame(data=low_dim_repr, columns=['representation'])
        self.low_dim_repr_df['note_id'] = self.embeddings_df['note_id']
    
    def create_link(self, first_id, second_id):
        self.link_df.append({'link_id': self.last_link_id, 'first_id': first_id, 'second_id': second_id})
        self.last_link_id += 1
        self.sync_links()

    def get_segment_notes(self, note_id, k, seg_num):
        search_in_reduced_space_flag = ml_server_settings.TSNE_PERPLEXITY < self.embeddings_df.shape[0]


        if seg_num * k > self.embeddings_df.shape[0]:
            return []

        res_list = []
        if search_in_reduced_space_flag:
            # recomputing tsne representation
            self.compute_low_dim_repr()
            
            search_df = self.low_dim_repr_df
            note_mask = search_df['note_id'] == note_id
            search_without_note_df = search_df[~note_mask]
            note_row = search_df[note_mask][0]
            distance_arr = (search_without_note_df['representation'] - note_row) ** 2
            search_df['distance'] = distance_arr
            search_df.sort_values(by='distance', ascending=False)
            needed_slice = search_df.iloc[seg_num * k:min(seg_num * k + k, search_df.shape[0])]
            res_list = list(needed_slice['note_id'])
        else:
            note_id_mask = self.embeddings_df['note_id'] == note_id

            request_note_embedding = self.embeddings_df[note_id_mask]['note_embedding'].iloc[0]
            search_data = self.embeddings_df[~note_id_mask]
            search_data['cos_sim'] = search_data['note_embedding'].apply(lambda x: util.cos_sim(x, request_note_embedding))
            sorted_data = search_data.sort_values(by='cos_sim', ascending=False)
            for i in range(seg_num * k, min(seg_num * k + k, sorted_data.shape[0])):
                res_list.append(sorted_data.iloc[i]['note_id'])
        
        return res_list
    
    def erase_db(self):
        self.embeddings_df = pd.DataFrame(data=None, columns=['note_name', 
                                                              'note_text',
                                                              'note_id',
                                                              'date_create',
                                                              'note_embedding'])
        self.link_df = pd.DataFrame(data=None, columns=['link_id', 'first_id', 'second_id'])
        self.model = SentenceTransformer(ml_server_settings.SENTENCE_TRANSFORMERS_MODEL)

        self.last_id = 0
        self.last_link_id = 0

        self.reducer = umap.UMAP(n_components=ml_server_settings.TSNE_PERPLEXITY, metric='cosine')
        self.reduced_repr = None
        self.auto_sync_flag = True
        self.low_dim_repr_df = None
    
    def get_notes_list(self, page_num, notes_per_page=5):
        sorted_notes = self.embeddings_df.sort_values(by='note_id')
        pages_count = (self.embeddings_df.shape[0] - 1) / notes_per_page + 1
        if page_num >= pages_count:
            return [], pages_count
        offset = page_num * notes_per_page
        needed_slice = sorted_notes[offset:min(offset + notes_per_page, self.embeddings_df.shape[0])]
        ret_struct = {
            'note_id': [],
            'note_name': [],
            'note_text': [],
            'note_date': []
        }
        for note_row in range(needed_slice.shape[0]):
            row = needed_slice.iloc[note_row]
            ret_struct['note_id'].append(row['note_id'])
            ret_struct['note_name'].append(row['note_name'])
            ret_struct['note_text'].append(row['note_text'])
            ret_struct['note_date'].append(row['note_date'])
        return ret_struct, pages_count
