import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv

from utils.logger import logger
from utils.exceptions import DatabaseConnectionError

# Load env variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "kkr_fan_hub")

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        """Establish MongoDB connection, verify connectivity, log collections, and seed initial records."""
        if not MONGO_URI or "your_mongodb_connection_string" in MONGO_URI:
            logger.error("MONGO_URI environment variable is missing or placeholder.")
            raise DatabaseConnectionError("MONGO_URI variable is not set correctly in environment.")
        
        logger.info("Attempting to connect to MongoDB Atlas...")
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            
            # Ping admin database to force connection check
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]
            
            logger.info("Successfully connected to MongoDB Atlas!")
            logger.info(f"Connected Database Name: {DATABASE_NAME}")
            
            # Seed collections if empty
            self.seed_all_collections()
            
            # Retrieve and log active collections list
            collections = self.db.list_collection_names()
            logger.info(f"Active Collections in Database: {collections}")
            
            # Setup collection indexes
            self.create_indexes()
        except (ConnectionFailure, PyMongoError) as e:
            logger.critical(f"Failed to connect to MongoDB: {e}")
            raise DatabaseConnectionError(str(e))

    def disconnect(self):
        """Close the MongoDB connection client."""
        if self.client:
            logger.info("Closing MongoDB connection client...")
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed.")

    def seed_all_collections(self):
        """Seed MongoDB collections from local JSON fallback files if they are empty on startup."""
        if self.db is None:
            return
            
        from utils.helpers import read_json
        
        collections_to_seed = {
            "players": "players.json",
            "matches": "matches.json",
            "news": "news.json",
            "quiz": "quiz.json",
            "legends": "legends.json"
        }
        
        now = datetime.utcnow()
        
        for coll_name, json_file in collections_to_seed.items():
            try:
                # Count document check
                if self.db[coll_name].count_documents({}) == 0:
                    logger.info(f"MongoDB collection '{coll_name}' is empty. Seeding from local '{json_file}'...")
                    data = read_json(json_file)
                    if data:
                        # Append audit attributes for seeding compliance
                        for item in data:
                            if isinstance(item, dict):
                                item["createdAt"] = now
                                item["createdBy"] = "system_seed"
                        self.db[coll_name].insert_many(data)
                        logger.info(f"Successfully seeded {len(data)} records into MongoDB collection '{coll_name}'.")
                    else:
                        logger.warning(f"No seed records found in '{json_file}' file.")
            except Exception as e:
                logger.error(f"Error seeding database collection '{coll_name}': {e}")

    def create_indexes(self):
        """Setup proper indexes for optimized querying, uniqueness constraints, and search."""
        if self.db is not None:
            try:
                # cheers index
                self.db.cheers.create_index([("createdAt", -1)])
                
                # users indexes
                self.db.users.create_index("username", unique=True)
                self.db.users.create_index("email", unique=True)
                self.db.users.create_index([("createdAt", -1)])
                
                # news indexes (descending date search and text indices for headline/snippet searches)
                self.db.news.create_index([("createdAt", -1)])
                self.db.news.create_index([("headline", "text"), ("snippet", "text")])
                
                # players indexes (date search, player name query index)
                self.db.players.create_index([("createdAt", -1)])
                self.db.players.create_index("name")
                
                # matches indexes
                self.db.matches.create_index([("createdAt", -1)])
                
                # quiz indexes
                self.db.quiz.create_index([("createdAt", -1)])
                
                # legends indexes
                self.db.legends.create_index([("createdAt", -1)])
                
                logger.info("Successfully configured constraints and search indexes across collections.")
            except Exception as e:
                logger.warning(f"Failed to create indexes: {e}")

# Global instance of connection manager
db_manager = MongoDBManager()

def init_db():
    """Initializes the database connection."""
    db_manager.connect()

def close_db():
    """Closes the database connection."""
    db_manager.disconnect()

def get_db():
    """Returns the current database instance."""
    if db_manager.db is None:
        raise DatabaseConnectionError("Database has not been initialized.")
    return db_manager.db
