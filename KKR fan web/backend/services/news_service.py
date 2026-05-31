from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Optional

from database import get_db
from schemas.news import NewsCreate, NewsUpdate
from utils.serializer import serialize_doc
from utils.logger import logger
from utils.exceptions import DatabaseOperationError, raise_bad_request_error

def get_news(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    cat: Optional[str] = None,
    sort_by: str = "createdAt",
    order: str = "desc"
) -> List[Dict[str, Any]]:
    """Retrieve news articles from MongoDB, supporting search, sorting, filtering, and pagination."""
    db = get_db()
    try:
        query = {}
        if search:
            query["$or"] = [
                {"headline": {"$regex": search, "$options": "i"}},
                {"snippet": {"$regex": search, "$options": "i"}},
                {"cat": {"$regex": search, "$options": "i"}}
            ]
        if cat:
            query["cat"] = cat
            
        sort_dir = -1 if order == "desc" else 1
        cursor = db.news.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
        
        news_list = []
        for doc in cursor:
            # Map fallback dates if date field is empty
            if "date" not in doc and "createdAt" in doc:
                doc["date"] = doc["createdAt"].strftime('%B %d, %Y').upper()
            news_list.append(serialize_doc(doc))
        return news_list
    except Exception as e:
        logger.error(f"Error querying news articles: {e}")
        raise DatabaseOperationError(str(e))

def get_news_by_id(news_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single news article by ID."""
    db = get_db()
    try:
        if not ObjectId.is_valid(news_id):
            raise_bad_request_error(f"Invalid news ID format: '{news_id}'")
        doc = db.news.find_one({"_id": ObjectId(news_id)})
        return serialize_doc(doc)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error querying news article by ID '{news_id}': {e}")
        raise DatabaseOperationError(str(e))

def create_news(payload: NewsCreate, admin_username: str) -> Dict[str, Any]:
    """Create a news article record in MongoDB and write audit fields."""
    db = get_db()
    try:
        now = datetime.utcnow()
        display_date = payload.date if payload.date else now.strftime('%B %d, %Y').upper()
        
        new_article = {
            "cat": payload.cat,
            "headline": payload.headline,
            "snippet": payload.snippet,
            "date": display_date,
            "link": payload.link,
            "createdAt": now,
            "createdBy": admin_username,
            "updatedAt": now,
            "updatedBy": admin_username
        }
        
        result = db.news.insert_one(new_article)
        new_article["_id"] = result.inserted_id
        
        logger.info(f"Admin Action: News article created by '{admin_username}' (ID: {result.inserted_id})")
        return serialize_doc(new_article)
    except Exception as e:
        logger.error(f"Error writing news article to database: {e}")
        raise DatabaseOperationError(str(e))

def update_news(news_id: str, payload: NewsUpdate, admin_username: str) -> Optional[Dict[str, Any]]:
    """Update a news article in MongoDB, capturing updated timestamps and author metadata."""
    db = get_db()
    try:
        if not ObjectId.is_valid(news_id):
            raise_bad_request_error(f"Invalid news ID format: '{news_id}'")
            
        update_data = {}
        payload_dict = payload.model_dump(exclude_unset=True)
        for key, value in payload_dict.items():
            if value is not None:
                update_data[key] = value
                
        if not update_data:
            return get_news_by_id(news_id)
            
        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = admin_username
        
        from pymongo import ReturnDocument
        result = db.news.find_one_and_update(
            {"_id": ObjectId(news_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if not result:
            logger.warning(f"News update failure: Article '{news_id}' not found.")
            return None
            
        logger.info(f"Admin Action: News article updated by '{admin_username}' (ID: {news_id})")
        return serialize_doc(result)
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error updating news article ID '{news_id}': {e}")
        raise DatabaseOperationError(str(e))

def delete_news(news_id: str, admin_username: str) -> bool:
    """Delete a news article from MongoDB."""
    db = get_db()
    try:
        if not ObjectId.is_valid(news_id):
            raise_bad_request_error(f"Invalid news ID format: '{news_id}'")
            
        result = db.news.delete_one({"_id": ObjectId(news_id)})
        
        if result.deleted_count == 0:
            logger.warning(f"News delete failure: Article '{news_id}' not found.")
            return False
            
        logger.info(f"Admin Action: News article deleted by '{admin_username}' (ID: {news_id})")
        return True
    except Exception as e:
        if hasattr(e, "status_code"):
            raise e
        logger.error(f"Error deleting news article ID '{news_id}': {e}")
        raise DatabaseOperationError(str(e))
