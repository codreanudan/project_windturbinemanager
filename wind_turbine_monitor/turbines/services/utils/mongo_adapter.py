# utils/mongo_adapter.py
from bson import ObjectId
from datetime import date, datetime

def drf_to_mongo(data: dict) -> dict:
    data_copy = data.copy()
    for key, value in data_copy.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            # Convertim date la string ISO
            data_copy[key] = value.isoformat()
    return data_copy

def mongo_to_drf(data: dict) -> dict:
    data_copy = data.copy()

    # Convertim _id din ObjectId în string pentru JSON serialization
    if '_id' in data_copy and isinstance(data_copy['_id'], ObjectId):
        data_copy['_id'] = str(data_copy['_id'])

    # Convertim installation_date din string ISO în date object
    if 'installation_date' in data_copy:
        val = data_copy['installation_date']
        if isinstance(val, str):
            try:
                data_copy['installation_date'] = datetime.fromisoformat(val).date()
            except ValueError:
                pass

    return data_copy
