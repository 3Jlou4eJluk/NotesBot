import os
# переехало в переменную окружения NOTES_BOT_ML_API_LINK
# ml_api_link = 'http://ml_server:8000/ml_api'

ml_api_link = os.getenv('NOTES_BOT_ML_API_LINK')

# notes to be shown on one inline keyboard page
note_page_count = 4
