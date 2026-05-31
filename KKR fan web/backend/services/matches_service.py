from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Optional

from database import get_db
from schemas.matches import MatchCreate, MatchUpdate
from utils.serializer import serialize_doc
from utils.logger import logger
from utils.exceptions import DatabaseOperationError, raise_bad_request_error

def get_matches(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "createdAt",
    order: str = "desc"
) -> List[Dict[str, Any]]:
    """Retrieve match records from MongoDB, supporting search, sorting, filtering, and pagination."""
    db = get_db()
    try:
        query = {}
        if search:
            query["$or"] = [
                {"opp": {"$regex": search, "$options": "i"}},
                {"venue": {"$regex": search, "$options": "i"}},
                {"desc": {"$regex": search, "$options": "i"}}
            ]
        if status:
            query["status"] = status
            
        sort_dir = -1 if order == "desc" else 1
        cursor = db.matches.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
        
        matches_list = []
        for doc in cursor:
            matches_list.append(serialize_doc(doc))
        return matches_list
    except Exception as e:
        logger.error(f"Error querying matches: {e}")
        raise DatabaseOperationError(str(e))

def get_match_by_id(match_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single match record by ID."""
    db = get_db()
    try:
        if not ObjectId.is_valid(match_id):
            raise_bad_request_error(f"Invalid match ID format: '{match_id}'")
        doc = db.matches.find_one({"_id": ObjectId(match_id)})
        return serialize_doc(doc)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error querying match by ID '{match_id}': {e}")
        raise DatabaseOperationError(str(e))

def create_match(payload: MatchCreate, admin_username: str) -> Dict[str, Any]:
    """Create a new match record in MongoDB."""
    db = get_db()
    try:
        now = datetime.utcnow()
        new_match = {
            "date": payload.date,
            "opp": payload.opp,
            "venue": payload.venue,
            "vs": payload.vs,
            "status": payload.status,
            "desc": payload.desc,
            "theme": payload.theme,
            "createdAt": now,
            "createdBy": admin_username,
            "updatedAt": now,
            "updatedBy": admin_username
        }
        
        result = db.matches.insert_one(new_match)
        new_match["_id"] = result.inserted_id
        
        logger.info(f"Admin Action: Match created by '{admin_username}' (ID: {result.inserted_id})")
        return serialize_doc(new_match)
    except Exception as e:
        logger.error(f"Error writing match to database: {e}")
        raise DatabaseOperationError(str(e))

def update_match(match_id: str, payload: MatchUpdate, admin_username: str) -> Optional[Dict[str, Any]]:
    """Update a match record in MongoDB, logging administrative authorship."""
    db = get_db()
    try:
        if not ObjectId.is_valid(match_id):
            raise_bad_request_error(f"Invalid match ID format: '{match_id}'")
            
        update_data = {}
        payload_dict = payload.model_dump(exclude_unset=True)
        for key, value in payload_dict.items():
            if value is not None:
                update_data[key] = value
                
        if not update_data:
            return get_match_by_id(match_id)
            
        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = admin_username
        
        from pymongo import ReturnDocument
        result = db.matches.find_one_and_update(
            {"_id": ObjectId(match_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if not result:
            logger.warning(f"Match update failure: Record '{match_id}' not found.")
            return None
            
        logger.info(f"Admin Action: Match updated by '{admin_username}' (ID: {match_id})")
        return serialize_doc(result)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error updating match ID '{match_id}': {e}")
        raise DatabaseOperationError(str(e))

def delete_match(match_id: str, admin_username: str) -> bool:
    """Delete a match record from MongoDB."""
    db = get_db()
    try:
        if not ObjectId.is_valid(match_id):
            raise_bad_request_error(f"Invalid match ID format: '{match_id}'")
            
        result = db.matches.delete_one({"_id": ObjectId(match_id)})
        
        if result.deleted_count == 0:
            logger.warning(f"Match delete failure: Record '{match_id}' not found.")
            return False
            
        logger.info(f"Admin Action: Match deleted by '{admin_username}' (ID: {match_id})")
        return True
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error deleting match ID '{match_id}': {e}")
        raise DatabaseOperationError(str(e))
