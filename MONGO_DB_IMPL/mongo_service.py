# services/mongo_service.py
from pymongo import MongoClient
from bson import ObjectId
from .utils.mongo_adapter import mongo_to_drf, drf_to_mongo
import logging

logger = logging.getLogger(__name__)

class MongoService:
    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://dbUser:dbUserPassword@cluster0.wtnbkwh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsAllowInvalidCertificates=true"
        )
        self.db = 'WIND_TURBINE_MONITOR'
        self.collection = 'WIND_TURBINE_MONITOR'

    def init_mongo_connection(self) -> None:
        client = MongoClient("mongodb+srv://dbUser:dbUserPassword@cluster0.wtnbkwh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsAllowInvalidCertificates=true")
        try:
            client.admin.command("ping")
            print("[MONGO_DB][INFO][✅] Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print("[MONGO_DB][ERROR][❌] Could not connect to MongoDB:", e)
            raise
        return client

    def insert_wind_turbine(self, data: dict) -> str:
        """Insert a new wind turbine and return its ID"""
        try:
            mongo_data = drf_to_mongo(data)
            result = self.collection.insert_one(mongo_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting wind turbine: {e}")
            raise

    def get_wind_turbine(self, turbine_id: str) -> dict:
        """Get a single wind turbine by ID"""
        try:
            if not ObjectId.is_valid(turbine_id):
                return None
            
            result = self.collection.find_one({"_id": ObjectId(turbine_id)})
            return mongo_to_drf(result) if result else None
        except Exception as e:
            logger.error(f"Error getting wind turbine {turbine_id}: {e}")
            return None

    def list_wind_turbines(self, limit: int = None, offset: int = 0) -> list:
        """List all wind turbines with optional pagination"""
        try:
            cursor = self.collection.find().skip(offset)
            if limit:
                cursor = cursor.limit(limit)
            
            return [mongo_to_drf(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Error listing wind turbines: {e}")
            return []
    
    def update_wind_turbine(self, turbine_id: str, data: dict) -> bool:
        """Update a wind turbine by ID"""
        try:
            if not ObjectId.is_valid(turbine_id):
                return False
                
            mongo_data = drf_to_mongo(data)
            result = self.collection.update_one(
                {"_id": ObjectId(turbine_id)},
                {"$set": mongo_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating wind turbine {turbine_id}: {e}")
            return False

    def delete_wind_turbine(self, turbine_id: str) -> bool:
        """Delete a wind turbine by ID"""
        try:
            if not ObjectId.is_valid(turbine_id):
                return False
                
            result = self.collection.delete_one({"_id": ObjectId(turbine_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting wind turbine {turbine_id}: {e}")
            return False

    def count_wind_turbines(self) -> int:
        """Count total number of wind turbines"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Error counting wind turbines: {e}")
            return 0

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
         
# Initialize the MongoDB service   
mongo_service = MongoService()
mongo_service.init_mongo_connection()