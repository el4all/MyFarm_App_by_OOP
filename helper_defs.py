import requests
import json
import os
import flet as ft

from pathlib import Path
from loguru import logger
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

from models.bunny_class import Farm, Bunny


URL =             'https://drive.google.com/uc?export=download&id=1YtUsFlRl2_kSrMqBFnHllE1bAyakREZW'
URL_for_testing = 'https://drive.google.com/uc?export=download&id=1hqo0hYlAyZD9BrHgiVhCfITjSMkAhdiG'
DATE_FORMAT = '%d.%m.%Y'
FILE_ID = '1YtUsFlRl2_kSrMqBFnHllE1bAyakREZW'
TEMP_FOR_CHECKBOX = 'temp_for_checkboxes.json'
TEMP_FOR_DICT = 'temp_for_dict_type_data.json'

def file_from_google():
    try:
        response = requests.get(URL_for_testing, timeout=(5,30))
        response.raise_for_status()
        data = response.json()
        return data

    except Exception as e:

        print(f'Error download: {e}')
        return {'rabbits': {}}

def file_upload_google(farm: Farm):
    try:
        BASE_DIR = Path(__file__).resolve().parent
        KEY_PATH = str(BASE_DIR / 'meatberry_farm_for_gspread.json')

        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
        creds.refresh(Request())
        access_token = creds.token

        json_string = json.dumps(farm.save_to_json_for_net(), ensure_ascii=False, indent=4)

        url = f'https://www.googleapis.com/upload/drive/v3/files/{FILE_ID}?uploadType=media'
        headers = {'Authorization': f'Bearer {access_token}', 'Content_Type': 'application/json'}

        response = requests.patch(url, headers=headers, data=json_string)

        if response.status_code == 200:
            logger.info('Синхронізовано')
            return True
        else:
            logger.error(f'Помилка {response.status_code} - {response.text}.')
            return False

    except Exception as e:
        print(e)
        return False

def save_value_for_checkboxes(process_key: str, completed_ids: list):
    data = {}
    if os.path.exists(TEMP_FOR_CHECKBOX):
        try:
            with open(TEMP_FOR_CHECKBOX, 'r',encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}
    data[process_key] = completed_ids
    with open(TEMP_FOR_CHECKBOX, 'w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_value_for_checkboxes(process_key: str):
    if not os.path.exists(TEMP_FOR_CHECKBOX):
        return []
    try:
        with open(TEMP_FOR_CHECKBOX, 'r', encoding='utf-8') as f:
            data = json.load(f).get(process_key,[])
            return data
    except Exception:
        return []

def get_temp_for_dict_type(process_key: str):
    if not os.path.exists(TEMP_FOR_CHECKBOX):
        return {}
    try:
        with open(TEMP_FOR_DICT, 'r', encoding='utf-8') as f:
            data = json.load(f).get(process_key, {})
            return data
    except Exception:
        return {}

def save_temp_for_dict_type(process_key: str, individual_process_data: dict):
    data = {}
    if os.path.exists(TEMP_FOR_CHECKBOX):
        try:
            with open(TEMP_FOR_CHECKBOX, 'r',encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}
    data[process_key] = individual_process_data
    with open(TEMP_FOR_CHECKBOX, 'w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
