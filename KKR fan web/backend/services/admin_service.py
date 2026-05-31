from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Optional
from pymongo import ReturnDocument

from database import get_db
from schemas.admin import (
    PlayerCreate, PlayerUpdate,
    QuizCreate, QuizUpdate,
    LegendCreate, LegendUpdate
)
from utils.serializer import serialize_doc
from utils.logger import logger
from utils.exceptions import DatabaseOperationError, raise_bad_request_error

# --- PLAYERS CRUD SERVICES ---

def get_players(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    sort_by: str = "createdAt",
    order: str = "desc"
) -> List[Dict[str, Any]]:
    """Retrieve player profiles from MongoDB, supporting search, sorting, role filter, and pagination."""
    db = get_db()
    try:
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"country": {"$regex": search, "$options": "i"}},
                {"role": {"$regex": search, "$options": "i"}}
            ]
        if role:
            query["role"] = role
            
        sort_dir = -1 if order == "desc" else 1
        cursor = db.players.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
        
        return [serialize_doc(doc) for doc in cursor]
    except Exception as e:
        logger.error(f"Error querying players: {e}")
        raise DatabaseOperationError(str(e))

def get_player_by_id(player_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    try:
        if not ObjectId.is_valid(player_id):
            raise_bad_request_error(f"Invalid player ID format: '{player_id}'")
        doc = db.players.find_one({"_id": ObjectId(player_id)})
        return serialize_doc(doc)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error querying player by ID '{player_id}': {e}")
        raise DatabaseOperationError(str(e))

def create_player(payload: PlayerCreate, admin_username: str) -> Dict[str, Any]:
    db = get_db()
    try:
        now = datetime.utcnow()
        new_player = {
            "name": payload.name,
            "jersey": payload.jersey,
            "role": payload.role,
            "country": payload.country,
            "bio": payload.bio,
            "stats": [s.model_dump() for s in payload.stats],
            "image": payload.image,
            "createdAt": now,
            "createdBy": admin_username,
            "updatedAt": now,
            "updatedBy": admin_username
        }
        
        result = db.players.insert_one(new_player)
        new_player["_id"] = result.inserted_id
        
        logger.info(f"Admin Action: Player profile created by '{admin_username}' (ID: {result.inserted_id})")
        return serialize_doc(new_player)
    except Exception as e:
        logger.error(f"Error writing player: {e}")
        raise DatabaseOperationError(str(e))

def update_player(player_id: str, payload: PlayerUpdate, admin_username: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    try:
        if not ObjectId.is_valid(player_id):
            raise_bad_request_error(f"Invalid player ID format: '{player_id}'")
            
        update_data = {}
        payload_dict = payload.model_dump(exclude_unset=True)
        for key, value in payload_dict.items():
            if value is not None:
                if key == "stats":
                    update_data[key] = [s.model_dump() for s in value]
                else:
                    update_data[key] = value
                
        if not update_data:
            return get_player_by_id(player_id)
            
        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = admin_username
        
        result = db.players.find_one_and_update(
            {"_id": ObjectId(player_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if not result:
            logger.warning(f"Player update failure: Profile '{player_id}' not found.")
            return None
            
        logger.info(f"Admin Action: Player profile updated by '{admin_username}' (ID: {player_id})")
        return serialize_doc(result)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error updating player ID '{player_id}': {e}")
        raise DatabaseOperationError(str(e))

def delete_player(player_id: str, admin_username: str) -> bool:
    db = get_db()
    try:
        if not ObjectId.is_valid(player_id):
            raise_bad_request_error(f"Invalid player ID format: '{player_id}'")
            
        result = db.players.delete_one({"_id": ObjectId(player_id)})
        
        if result.deleted_count == 0:
            logger.warning(f"Player delete failure: Profile '{player_id}' not found.")
            return False
            
        logger.info(f"Admin Action: Player profile deleted by '{admin_username}' (ID: {player_id})")
        return True
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error deleting player ID '{player_id}': {e}")
        raise DatabaseOperationError(str(e))


# --- QUIZ CRUD SERVICES ---

def get_quizzes(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: str = "createdAt",
    order: str = "asc"
) -> List[Dict[str, Any]]:
    """Retrieve quiz questions from MongoDB, supporting search and pagination."""
    db = get_db()
    try:
        query = {}
        if search:
            query["$or"] = [
                {"q": {"$regex": search, "$options": "i"}},
                {"exp": {"$regex": search, "$options": "i"}}
            ]
            
        sort_dir = 1 if order == "asc" else -1
        cursor = db.quiz.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
        
        return [serialize_doc(doc) for doc in cursor]
    except Exception as e:
        logger.error(f"Error querying quiz questions: {e}")
        raise DatabaseOperationError(str(e))

def get_quiz_by_id(quiz_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    try:
        if not ObjectId.is_valid(quiz_id):
            raise_bad_request_error(f"Invalid quiz ID format: '{quiz_id}'")
        doc = db.quiz.find_one({"_id": ObjectId(quiz_id)})
        return serialize_doc(doc)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error querying quiz by ID '{quiz_id}': {e}")
        raise DatabaseOperationError(str(e))

def create_quiz(payload: QuizCreate, admin_username: str) -> Dict[str, Any]:
    db = get_db()
    try:
        now = datetime.utcnow()
        new_quiz = {
            "q": payload.q,
            "opts": payload.opts,
            "ans": payload.ans,
            "exp": payload.exp,
            "createdAt": now,
            "createdBy": admin_username,
            "updatedAt": now,
            "updatedBy": admin_username
        }
        
        result = db.quiz.insert_one(new_quiz)
        new_quiz["_id"] = result.inserted_id
        
        logger.info(f"Admin Action: Quiz question created by '{admin_username}' (ID: {result.inserted_id})")
        return serialize_doc(new_quiz)
    except Exception as e:
        logger.error(f"Error writing quiz: {e}")
        raise DatabaseOperationError(str(e))

def update_quiz(quiz_id: str, payload: QuizUpdate, admin_username: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    try:
        if not ObjectId.is_valid(quiz_id):
            raise_bad_request_error(f"Invalid quiz ID format: '{quiz_id}'")
            
        update_data = {}
        payload_dict = payload.model_dump(exclude_unset=True)
        for key, value in payload_dict.items():
            if value is not None:
                update_data[key] = value
                
        if not update_data:
            return get_quiz_by_id(quiz_id)
            
        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = admin_username
        
        result = db.quiz.find_one_and_update(
            {"_id": ObjectId(quiz_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if not result:
            logger.warning(f"Quiz update failure: Question '{quiz_id}' not found.")
            return None
            
        logger.info(f"Admin Action: Quiz question updated by '{admin_username}' (ID: {quiz_id})")
        return serialize_doc(result)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error updating quiz ID '{quiz_id}': {e}")
        raise DatabaseOperationError(str(e))

def delete_quiz(quiz_id: str, admin_username: str) -> bool:
    db = get_db()
    try:
        if not ObjectId.is_valid(quiz_id):
            raise_bad_request_error(f"Invalid quiz ID format: '{quiz_id}'")
            
        result = db.quiz.delete_one({"_id": ObjectId(quiz_id)})
        
        if result.deleted_count == 0:
            logger.warning(f"Quiz delete failure: Question '{quiz_id}' not found.")
            return False
            
        logger.info(f"Admin Action: Quiz question deleted by '{admin_username}' (ID: {quiz_id})")
        return True
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error deleting quiz ID '{quiz_id}': {e}")
        raise DatabaseOperationError(str(e))


# --- LEGENDS CRUD SERVICES ---

def get_legends(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: str = "createdAt",
    order: str = "asc"
) -> List[Dict[str, Any]]:
    """Retrieve Hall of Fame legends from MongoDB, supporting search and pagination."""
    db = get_db()
    try:
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"achievement": {"$regex": search, "$options": "i"}}
            ]
            
        sort_dir = 1 if order == "asc" else -1
        cursor = db.legends.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
        
        return [serialize_doc(doc) for doc in cursor]
    except Exception as e:
        logger.error(f"Error querying legends: {e}")
        raise DatabaseOperationError(str(e))

def get_legend_by_id(legend_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    try:
        if not ObjectId.is_valid(legend_id):
            raise_bad_request_error(f"Invalid legend ID format: '{legend_id}'")
        doc = db.legends.find_one({"_id": ObjectId(legend_id)})
        return serialize_doc(doc)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error querying legend by ID '{legend_id}': {e}")
        raise DatabaseOperationError(str(e))

def create_legend(payload: LegendCreate, admin_username: str) -> Dict[str, Any]:
    db = get_db()
    try:
        now = datetime.utcnow()
        new_legend = {
            "name": payload.name,
            "years": payload.years,
            "achievement": payload.achievement,
            "stat": payload.stat,
            "avatar": payload.avatar,
            "createdAt": now,
            "createdBy": admin_username,
            "updatedAt": now,
            "updatedBy": admin_username
        }
        
        result = db.legends.insert_one(new_legend)
        new_legend["_id"] = result.inserted_id
        
        logger.info(f"Admin Action: Legend profile created by '{admin_username}' (ID: {result.inserted_id})")
        return serialize_doc(new_legend)
    except Exception as e:
        logger.error(f"Error writing legend: {e}")
        raise DatabaseOperationError(str(e))

def update_legend(legend_id: str, payload: LegendUpdate, admin_username: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    try:
        if not ObjectId.is_valid(legend_id):
            raise_bad_request_error(f"Invalid legend ID format: '{legend_id}'")
            
        update_data = {}
        payload_dict = payload.model_dump(exclude_unset=True)
        for key, value in payload_dict.items():
            if value is not None:
                update_data[key] = value
                
        if not update_data:
            return get_legend_by_id(legend_id)
            
        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = admin_username
        
        result = db.legends.find_one_and_update(
            {"_id": ObjectId(legend_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if not result:
            logger.warning(f"Legend update failure: Profile '{legend_id}' not found.")
            return None
            
        logger.info(f"Admin Action: Legend profile updated by '{admin_username}' (ID: {legend_id})")
        return serialize_doc(result)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error updating legend ID '{legend_id}': {e}")
        raise DatabaseOperationError(str(e))

def delete_legend(legend_id: str, admin_username: str) -> bool:
    db = get_db()
    try:
        if not ObjectId.is_valid(legend_id):
            raise_bad_request_error(f"Invalid legend ID format: '{legend_id}'")
            
        result = db.legends.delete_one({"_id": ObjectId(legend_id)})
        
        if result.deleted_count == 0:
            logger.warning(f"Legend delete failure: Profile '{legend_id}' not found.")
            return False
            
        logger.info(f"Admin Action: Legend profile deleted by '{admin_username}' (ID: {legend_id})")
        return True
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error deleting legend ID '{legend_id}': {e}")
        raise DatabaseOperationError(str(e))
