from datetime import datetime
from typing import List

from database import get_db
from utils.logger import logger
from utils.exceptions import DatabaseOperationError

def format_date(dt: datetime) -> str:
    """Format UTC datetime into '%b %d' with no leading zero on day."""
    if not isinstance(dt, datetime):
        return ""
    date_str = dt.strftime('%b %d')
    parts = date_str.split()
    if len(parts) == 2 and parts[1].startswith('0'):
        return f"{parts[0]} {parts[1][1:]}"
    return date_str

def get_cheers() -> List[dict]:
    """Retrieve the newest 30 cheers from the MongoDB cheers collection."""
    db = get_db()
    try:
        cursor = db.cheers.find().sort("createdAt", -1).limit(30)
        cheers = []
        for doc in cursor:
            cheers.append({
                "name": doc.get("name", ""),
                "msg": doc.get("msg", ""),
                "time": format_date(doc.get("createdAt"))
            })
        return cheers
    except Exception as e:
        logger.error(f"Error querying cheers from MongoDB: {e}")
        raise DatabaseOperationError(str(e))

def add_cheer(name: str, msg: str) -> List[dict]:
    """Insert a new cheer, prune the collection to maximum 30 cheers, and return the updated list."""
    db = get_db()
    try:
        new_doc = {
            "name": name,
            "msg": msg,
            "createdAt": datetime.utcnow()
        }
        db.cheers.insert_one(new_doc)
        logger.info(f"Database write: Added new cheer from '{name}'")
        
        # Enforce maximum of 30 cheers
        cursor = db.cheers.find({}, {"_id": 1}).sort("createdAt", -1)
        ids = [doc["_id"] for doc in cursor]
        if len(ids) > 30:
            to_delete = ids[30:]
            db.cheers.delete_many({"_id": {"$in": to_delete}})
            logger.info(f"Database clean: Pruned {len(to_delete)} older cheers from cheers collection.")
            
        return get_cheers()
    except Exception as e:
        logger.error(f"Error inserting cheer into MongoDB: {e}")
        raise DatabaseOperationError(str(e))
