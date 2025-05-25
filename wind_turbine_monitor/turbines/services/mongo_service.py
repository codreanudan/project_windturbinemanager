# services/mongo_service.py
from pymongo import MongoClient
from bson import ObjectId
from .utils.mongo_adapter import mongo_to_drf, drf_to_mongo


class MongoService:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://dbUser:dbUserPassword@cluster0.wtnbkwh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsAllowInvalidCertificates=true")
        self.db = self.client["wind_turbine_db"]
        self.collection = self.db["wind_turbines"]

    def insert_wind_turbine(self, data: dict) -> str:
        result = self.collection.insert_one(drf_to_mongo(data))
        return str(result.inserted_id)

    def get_wind_turbine(self, turbine_id: str) -> dict:
        result = self.collection.find_one({"_id": ObjectId(turbine_id)})
        return mongo_to_drf(result) if result else None

    def list_wind_turbines(self) -> list:
        return [mongo_to_drf(doc) for doc in self.collection.find()]
    
    def update_wind_turbine(self, turbine_id: str, data: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(turbine_id)},
            {"$set": drf_to_mongo(data)}
        )
        return result.modified_count > 0

    def delete_wind_turbine(self, turbine_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(turbine_id)})
        return result.deleted_count > 0
