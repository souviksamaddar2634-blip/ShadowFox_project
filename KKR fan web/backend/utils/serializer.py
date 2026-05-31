from bson import ObjectId
from typing import Any, Dict, List, Optional

def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Safely serialize a MongoDB document.
    Converts '_id' (ObjectId) to 'id' (str) and removes 'hashed_password'.
    """
    if doc is None:
        return None
    
    serialized = doc.copy()
    if "_id" in serialized:
        serialized["id"] = str(serialized.pop("_id"))
        
    # Strictly exclude passwords from all output responses
    serialized.pop("hashed_password", None)
    
    # Safely convert other nested ObjectIds to string
    for key, value in serialized.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
            
    return serialized

def serialize_list(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Serialize a list of MongoDB documents."""
    return [serialize_doc(d) for d in docs if d is not None]
