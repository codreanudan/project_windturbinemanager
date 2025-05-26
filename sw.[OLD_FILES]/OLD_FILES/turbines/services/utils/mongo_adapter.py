# utils/mongo_adapter.py
from bson import ObjectId
from datetime import date, datetime

def drf_to_mongo(data: dict) -> dict:
    """Convert DRF data format to MongoDB format"""
    data_copy = data.copy()
    
    # Remove 'id' field if present (MongoDB will auto-generate _id)
    if 'id' in data_copy:
        del data_copy['id']
    
    # Convert date objects to ISO strings for MongoDB storage
    for key, value in data_copy.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            data_copy[key] = value.isoformat()
        elif isinstance(value, datetime):
            data_copy[key] = value.isoformat()
    
    return data_copy

def mongo_to_drf(data: dict) -> dict:
    """Convert MongoDB data format to DRF format"""
    if not data:
        return None
        
    data_copy = data.copy()

    # Convert MongoDB _id to DRF id
    if '_id' in data_copy:
        if isinstance(data_copy['_id'], ObjectId):
            data_copy['id'] = str(data_copy['_id'])
        else:
            data_copy['id'] = data_copy['_id']
        del data_copy['_id']

    # Convert date strings back to date objects
    date_fields = ['installation_date', 'last_maintenance_date']
    for field in date_fields:
        if field in data_copy and data_copy[field]:
            val = data_copy[field]
            if isinstance(val, str):
                try:
                    # Handle both date and datetime ISO strings
                    if 'T' in val:
                        data_copy[field] = datetime.fromisoformat(val.replace('Z', '+00:00')).date()
                    else:
                        data_copy[field] = datetime.fromisoformat(val).date()
                except (ValueError, TypeError):
                    pass

    return data_copy