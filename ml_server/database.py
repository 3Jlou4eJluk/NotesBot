import numpy as np
import pandas as pd
import ml_server_settings

from sentence_transformers import SentenceTransformer, util
from sklearn.manifold import TSNE


class DataBase:
    def __init__(self):
        try:
            self.embeddings_df = pd.read_json(ml_server_settings.EMBEDDING_DB_PATH)
        except:
            print('Error: embeddings database not found')
            self.embeddings_df = pd.DataFrame(data=None, columns=['note_name', 
                                                                  'note_text',
                                                                  'note_id',
                                                                  'note_embedding'])
        self.model = SentenceTransformer(ml_server_settings.SENTENCE_TRANSFORMERS_MODEL)
        self.last_id = 0

        self.reducer = TSNE(n_components=2, metric='cosine')
        self.reduced_repr = None
    
    def add_note(self, name: str, text: str) -> int:
        note_emb = self.model.encode(text)
        self.embeddings_df = self.embeddings_df._append({'note_name': name, 'note_text': text, 
                                                         'note_id': self.last_id, 'note_embedding': note_emb}, ignore_index=True)
        self.last_id += 1
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

    def get_embedding_array(self) -> np.ndarray:
        if self.embeddings_df.shape[0] == 0:
            return None
        ret_array = np.zeros((self.embeddings_df.shape[0], self.embeddings_df[0].shape[0]))
        for i in range(self.embeddings_df.shape[0]):
            ret_array[i] = self.embeddings_df.iloc[i]['note_embedding']
        return ret_array
    
    def sync_vault(self) -> None:
        self.embeddings_df.to_json(ml_server_settings.EMBEDDING_DB_PATH)

    def get_note_by_id(self, note_id) -> tuple[str, str]:
        needed_slice = self.embeddings_df[self.embeddings_df['note_id'] == note_id]
        if needed_slice.shape[0] == 0:
            return None, None
        else:
            return needed_slice.iloc[0]['note_name'], needed_slice.iloc[0]['note_text']
    
    def get_k_nearest_notes(self, note_id, k) -> list[tuple[str, str]]:
        search_in_reduced_space_flag = ml_server_settings.TSNE_PERPLEXITY < self.embeddings_df.shape[0]

        res_list = []
        if search_in_reduced_space_flag:
            # recomputing tsne representation
            pass
        else:
            note_id_mask = self.embeddings_df['note_id'] == note_id
            request_note_embedding = self.embeddings_df[note_id_mask]['note_embedding'][0]
            search_data = self.embeddings_df[~note_id_mask]
            search_data['cos_sim'] = search_data['note_embedding'].apply(lambda x: util.cos_sim(x, request_note_embedding))
            sorted_data = search_data.sort_values(by='cos_sim', ascending=False)
            for i in range(min(k, sorted_data.shape[0])):
                res_list.append(sorted_data['note_id'])
        
        return res_list