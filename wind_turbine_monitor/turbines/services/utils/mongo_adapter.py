# utils/mongo_adapter.py
from bson import ObjectId
from datetime import date, datetime

def drf_to_mongo(data: dict) -> dict:
    """Convert DRF data format to MongoDB format with correct types"""
    data_copy = data.copy()

    # Remove 'id' field if present (MongoDB will auto-generate _id)
    if 'id' in data_copy:
        del data_copy['id']

    # Ensure correct types for numeric and date fields
    if 'capacity_kw' in data_copy:
        try:
            data_copy['capacity_kw'] = float(data_copy['capacity_kw'])
        except Exception:
            pass
    if 'latitude' in data_copy:
        try:
            data_copy['latitude'] = float(data_copy['latitude'])
        except Exception:
            pass
    if 'longitude' in data_copy:
        try:
            data_copy['longitude'] = float(data_copy['longitude'])
        except Exception:
            pass
    if 'installation_date' in data_copy:
        from datetime import datetime, date
        val = data_copy['installation_date']
        if isinstance(val, str):
            try:
                data_copy['installation_date'] = datetime.fromisoformat(val).date()
            except Exception:
                pass
    if 'last_maintenance_date' in data_copy:
        from datetime import datetime, date
        val = data_copy['last_maintenance_date']
        if isinstance(val, str) and val:
            try:
                data_copy['last_maintenance_date'] = datetime.fromisoformat(val).date()
            except Exception:
                pass
        elif not val:
            data_copy['last_maintenance_date'] = None
    if 'maintenance_done' in data_copy:
        # Accept "true"/"false" strings or booleans
        val = data_copy['maintenance_done']
        if isinstance(val, str):
            data_copy['maintenance_done'] = val.lower() == "true" or val == "on"

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
    from datetime import datetime
    for field in date_fields:
        if field in data_copy and data_copy[field]:
            val = data_copy[field]
            if isinstance(val, str):
                try:
                    # Accept both date and datetime ISO strings
                    if 'T' in val:
                        data_copy[field] = datetime.fromisoformat(val.replace('Z', '+00:00')).date()
                    else:
                        data_copy[field] = datetime.fromisoformat(val).date()
                except (ValueError, TypeError):
                    pass

    return data_copy