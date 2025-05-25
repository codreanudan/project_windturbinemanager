# services/mongo_service.py
from pymongo import MongoClient, errors
from bson import ObjectId
from datetime import datetime, date
import logging
from typing import Optional, List, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class MongoService:
    """MongoDB service for wind turbine management"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Initialize MongoDB connection"""
        try:
            connection_string = getattr(settings, 'MONGODB_CONNECTION_STRING', 
                "mongodb+srv://dbUser:dbUserPassword@cluster0.wtnbkwh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsAllowInvalidCertificates=true")
            
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            db_name = getattr(settings, 'MONGODB_DATABASE', 'WIND_TURBINE_MONITOR')
            collection_name = getattr(settings, 'MONGODB_COLLECTION', 'wind_turbines')
            
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info("✅ Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Index on name for faster lookups
            self.collection.create_index("name")
            # Compound index for location-based queries
            self.collection.create_index([("latitude", 1), ("longitude", 1)])
            # Index on installation_date for time-based queries
            self.collection.create_index("installation_date")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
    
    def _serialize_for_mongo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python data types to MongoDB-compatible format"""
        serialized = {}
        
        for key, value in data.items():
            if key == 'id':
                # Skip 'id' field - MongoDB uses '_id'
                continue
            elif isinstance(value, date) and not isinstance(value, datetime):
                # Convert date to datetime for MongoDB
                serialized[key] = datetime.combine(value, datetime.min.time())
            elif isinstance(value, datetime):
                serialized[key] = value
            elif value is None:
                serialized[key] = None
            else:
                serialized[key] = value
        
        # Add metadata
        serialized['updated_at'] = datetime.utcnow()
        if 'created_at' not in serialized:
            serialized['created_at'] = datetime.utcnow()
            
        return serialized
    
    def _deserialize_from_mongo(self, doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert MongoDB document to DRF-compatible format"""
        if not doc:
            return None
        
        result = {}
        
        for key, value in doc.items():
            if key == '_id':
                # Convert ObjectId to string for DRF
                result['id'] = str(value)
            elif key in ['installation_date', 'last_maintenance_date'] and isinstance(value, datetime):
                # Convert datetime back to date
                result[key] = value.date() if value else None
            elif key in ['created_at', 'updated_at']:
                # Keep metadata as datetime but make it optional for DRF
                continue
            else:
                result[key] = value
        
        return result
    
    def create_turbine(self, data: Dict[str, Any]) -> Optional[str]:
        """Create a new wind turbine"""
        try:
            # Validate required fields
            required_fields = ['name', 'latitude', 'longitude', 'installation_date', 'capacity_kw']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValueError(f"Required field '{field}' is missing")
            
            # Check if turbine with same name already exists
            existing = self.collection.find_one({"name": data['name']})
            if existing:
                raise ValueError(f"Turbine with name '{data['name']}' already exists")
            
            mongo_data = self._serialize_for_mongo(data)
            result = self.collection.insert_one(mongo_data)
            
            logger.info(f"Created turbine: {data.get('name')} with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating turbine: {e}")
            raise
    
    def get_turbine(self, turbine_id: str) -> Optional[Dict[str, Any]]:
        """Get a single wind turbine by ID"""
        try:
            if not ObjectId.is_valid(turbine_id):
                logger.warning(f"Invalid ObjectId: {turbine_id}")
                return None
            
            doc = self.collection.find_one({"_id": ObjectId(turbine_id)})
            return self._deserialize_from_mongo(doc)
            
        except Exception as e:
            logger.error(f"Error getting turbine {turbine_id}: {e}")
            return None
    
    def list_turbines(self, limit: int = None, offset: int = 0, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List wind turbines with optional pagination and filtering"""
        try:
            query = filters or {}
            
            cursor = self.collection.find(query).skip(offset).sort("created_at", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            return [self._deserialize_from_mongo(doc) for doc in cursor]
            
        except Exception as e:
            logger.error(f"Error listing turbines: {e}")
            return []
    
    def update_turbine(self, turbine_id: str, data: Dict[str, Any]) -> bool:
        """Update a wind turbine by ID"""
        try:
            if not ObjectId.is_valid(turbine_id):
                logger.warning(f"Invalid ObjectId: {turbine_id}")
                return False
            
            # Don't allow updating the name if it would create a duplicate
            if 'name' in data:
                existing = self.collection.find_one({
                    "name": data['name'],
                    "_id": {"$ne": ObjectId(turbine_id)}
                })
                if existing:
                    raise ValueError(f"Turbine with name '{data['name']}' already exists")
            
            mongo_data = self._serialize_for_mongo(data)
            # Don't update created_at
            if 'created_at' in mongo_data:
                del mongo_data['created_at']
            
            result = self.collection.update_one(
                {"_id": ObjectId(turbine_id)},
                {"$set": mongo_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated turbine: {turbine_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating turbine {turbine_id}: {e}")
            raise
    
    def delete_turbine(self, turbine_id: str) -> bool:
        """Delete a wind turbine by ID"""
        try:
            if not ObjectId.is_valid(turbine_id):
                logger.warning(f"Invalid ObjectId: {turbine_id}")
                return False
            
            result = self.collection.delete_one({"_id": ObjectId(turbine_id)})
            success = result.deleted_count > 0
            
            if success:
                logger.info(f"Deleted turbine: {turbine_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting turbine {turbine_id}: {e}")
            return False
    
    def count_turbines(self, filters: Dict[str, Any] = None) -> int:
        """Count wind turbines with optional filtering"""
        try:
            query = filters or {}
            return self.collection.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting turbines: {e}")
            return 0
    
    def get_turbines_by_location(self, lat: float, lon: float, radius_km: float = 10) -> List[Dict[str, Any]]:
        """Get turbines within a radius of a location"""
        try:
            # Simple bounding box query (for more precise results, use MongoDB's geospatial queries)
            lat_delta = radius_km / 111  # Rough conversion: 1 degree ≈ 111km
            lon_delta = radius_km / (111 * abs(lat))  # Adjust for latitude
            
            query = {
                "latitude": {"$gte": lat - lat_delta, "$lte": lat + lat_delta},
                "longitude": {"$gte": lon - lon_delta, "$lte": lon + lon_delta}
            }
            
            cursor = self.collection.find(query)
            return [self._deserialize_from_mongo(doc) for doc in cursor]
            
        except Exception as e:
            logger.error(f"Error getting turbines by location: {e}")
            return []
    
    def get_maintenance_overdue(self) -> List[Dict[str, Any]]:
        """Get turbines that need maintenance"""
        try:
            # Get turbines where maintenance is not done or last maintenance is old
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            query = {
                "$or": [
                    {"maintenance_done": False},
                    {"last_maintenance_date": {"$lt": seven_days_ago}},
                    {"last_maintenance_date": None}
                ]
            }
            
            cursor = self.collection.find(query)
            return [self._deserialize_from_mongo(doc) for doc in cursor]
            
        except Exception as e:
            logger.error(f"Error getting overdue maintenance turbines: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Check MongoDB connection health"""
        try:
            # Ping the database
            self.client.admin.command('ping')
            
            # Get collection stats
            stats = self.db.command("collStats", self.collection.name)
            
            return {
                "status": "healthy",
                "database": self.db.name,
                "collection": self.collection.name,
                "document_count": stats.get("count", 0),
                "data_size": stats.get("size", 0),
                "connected": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connected": False
            }
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Singleton instance
_mongo_service = None

def get_mongo_service() -> MongoService:
    """Get or create MongoDB service instance"""
    global _mongo_service
    if _mongo_service is None:
        _mongo_service = MongoService()
    return _mongo_service