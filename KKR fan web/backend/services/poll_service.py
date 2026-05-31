from database import get_db
from utils.helpers import read_json
from utils.logger import logger
from utils.exceptions import DatabaseOperationError, raise_bad_request_error

POLL_ID = "mvp_poll"

def get_poll() -> dict:
    """Retrieve the MVP poll status, seeding it from poll.json if missing in MongoDB."""
    db = get_db()
    try:
        doc = db.poll.find_one({"_id": POLL_ID})
        if not doc:
            # Seed from local JSON file to preserve existing votes if migrating
            logger.info("MVP Poll document not found in MongoDB. Seeding from local poll.json...")
            initial_data = read_json("poll.json")
            if initial_data and "votes" in initial_data:
                doc = {
                    "_id": POLL_ID,
                    "votes": initial_data["votes"],
                    "labels": initial_data["labels"]
                }
            else:
                # Default fallback seed
                doc = {
                    "_id": POLL_ID,
                    "votes": [0, 0, 0, 0],
                    "labels": ["Sunil Narine", "Rinku Singh", "Varun Chakravarthy", "Quinton de Kock"]
                }
            db.poll.insert_one(doc)
            logger.info("Successfully seeded MVP Poll database document.")
        
        return {
            "votes": doc.get("votes", []),
            "labels": doc.get("labels", [])
        }
    except Exception as e:
        logger.error(f"Error querying poll from MongoDB: {e}")
        raise DatabaseOperationError(str(e))

def vote_poll(index: int) -> dict:
    """Increment the vote at the specified index atomically in MongoDB and return the updated poll."""
    db = get_db()
    try:
        poll_state = get_poll()
        votes_count = len(poll_state["votes"])
        
        if index < 0 or index >= votes_count:
            raise_bad_request_error(f"Option index {index} is out of bounds (must be between 0 and {votes_count - 1}).")
            
        # Perform atomic update on MongoDB
        result = db.poll.update_one(
            {"_id": POLL_ID},
            {"$inc": {f"votes.{index}": 1}}
        )
        
        if result.modified_count == 0:
            logger.warning(f"Poll vote atomic update did not modify any documents.")
            
        logger.info(f"Database write: Registered MVP Poll vote at option index {index}.")
        return get_poll()
    except Exception as e:
        if isinstance(e, Exception) and hasattr(e, "status_code"):
            # Propagate FastAPI HTTPExceptions
            raise e
        logger.error(f"Error updating poll vote in MongoDB: {e}")
        raise DatabaseOperationError(str(e))
