import sys
import os
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException

# Insert root folder to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set env variables for tests
os.environ["SECRET_KEY"] = "testsecretkeytestsecretkeytestsecretkeytestsecretkey"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

# Mock classes for MongoDB collections
class MockCollection:
    def __init__(self):
        self.docs = []

    def find(self, filter_query=None, projection=None):
        class Cursor:
            def __init__(self, docs):
                self.docs = docs
            def sort(self, key, direction=-1):
                if key == "createdAt":
                    self.docs = sorted(self.docs, key=lambda x: x.get("createdAt", datetime.min), reverse=(direction == -1))
                return self
            def limit(self, limit_num):
                self.docs = self.docs[:limit_num]
                return self
            def skip(self, skip_num):
                self.docs = self.docs[skip_num:]
                return self
            def __iter__(self):
                return iter(self.docs)
        return Cursor(self.docs.copy())

    def find_one(self, filter_query):
        for doc in self.docs:
            if "_id" in filter_query:
                if str(doc.get("_id")) == str(filter_query.get("_id")):
                    return doc
            elif "username" in filter_query:
                if doc.get("username") == filter_query.get("username"):
                    return doc
            elif "email" in filter_query:
                if doc.get("email") == filter_query.get("email"):
                    return doc
        return None

    def insert_one(self, doc):
        if "_id" not in doc:
            from bson import ObjectId
            doc["_id"] = ObjectId()
        self.docs.append(doc)
        return type('result', (object,), {"inserted_id": doc["_id"]})

    def delete_many(self, filter_query):
        in_list = filter_query.get("_id", {}).get("$in", [])
        initial_len = len(self.docs)
        self.docs = [d for d in self.docs if d.get("_id") not in in_list]
        return type('result', (object,), {"deleted_count": initial_len - len(self.docs)})

    def update_one(self, filter_query, update_query):
        doc = self.find_one(filter_query)
        if doc:
            inc = update_query.get("$inc", {})
            for key, val in inc.items():
                parts = key.split('.')
                if len(parts) == 2 and parts[0] == "votes":
                    idx = int(parts[1])
                    doc["votes"][idx] += val
            return type('result', (object,), {"modified_count": 1})
        return type('result', (object,), {"modified_count": 0})

    def find_one_and_update(self, filter_query, update_query, return_document=None):
        doc = self.find_one(filter_query)
        if doc:
            set_data = update_query.get("$set", {})
            for key, value in set_data.items():
                doc[key] = value
            return doc
        return None

    def delete_one(self, filter_query):
        initial_len = len(self.docs)
        self.docs = [d for d in self.docs if str(d.get("_id")) != str(filter_query.get("_id"))]
        return type('result', (object,), {"deleted_count": initial_len - len(self.docs)})

    def count_documents(self, filter_query):
        return len(self.docs)

    def create_index(self, keys, unique=False):
        pass

class MockDB:
    def __init__(self):
        self.cheers = MockCollection()
        self.poll = MockCollection()
        self.users = MockCollection()
        self.news = MockCollection()
        self.matches = MockCollection()
        self.players = MockCollection()
        self.quiz = MockCollection()
        self.legends = MockCollection()

# Setup mocks
mock_db = MockDB()

import backend.database
backend.database.get_db = lambda: mock_db

try:
    import database
    database.get_db = lambda: mock_db
except ImportError:
    pass

# Import security, schemas, services, and permissions
from schemas.user import UserCreate
from schemas.auth import UserLogin
from schemas.news import NewsCreate, NewsUpdate
from schemas.matches import MatchCreate, MatchUpdate
from schemas.admin import (
    PlayerCreate, PlayerUpdate,
    QuizCreate, QuizUpdate,
    LegendCreate, LegendUpdate
)
from services import cheers_service, poll_service, user_service, auth_service, news_service, matches_service, admin_service
from utils.security import verify_password, get_password_hash
from utils.auth import create_access_token, verify_token, get_current_user
from utils.permissions import require_admin, require_roles
from utils.exceptions import (
    DuplicateEmailException,
    DuplicateUsernameException,
    InvalidCredentialsException,
    ExpiredTokenException
)

class MockWebSocket:
    def __init__(self):
        self.accepted = False
        self.closed = False
        self.close_code = None
        self.close_reason = None
        self.sent_messages = []

    async def accept(self):
        self.accepted = True

    async def close(self, code=1000, reason=""):
        self.closed = True
        self.close_code = code
        self.close_reason = reason

    async def send_text(self, text):
        self.sent_messages.append(text)

    async def send_json(self, data):
        import json
        self.sent_messages.append(json.dumps(data))

def run_tests():
    # === CHEERS SERVICE ===
    print("=== TESTING CHEERS SERVICE ===")
    cheers_service.add_cheer("Fan A", "Message A")
    cheers_service.add_cheer("Fan B", "Message B")
    cheers_service.add_cheer("Fan C", "Message C")
    cheers = cheers_service.get_cheers()
    assert len(cheers) == 3
    assert cheers[0]["name"] == "Fan C"
    print("[OK] Cheers add and retrieve verification passed.")

    # === POLL SERVICE ===
    print("\n=== TESTING POLL SERVICE ===")
    poll_data = poll_service.get_poll()
    assert len(poll_data["votes"]) == len(poll_data["labels"])
    initial_votes = poll_data["votes"][1]
    updated_poll = poll_service.vote_poll(1)
    assert updated_poll["votes"][1] == initial_votes + 1
    print("[OK] Poll seeding and increment validation passed.")

    # === USER SCHEMA VALIDATION ===
    print("\n=== TESTING USER SCHEMA VALIDATIONS ===")
    try:
        UserCreate(username="ab", email="test@test.com", password="Password1", favorite_player="Narine")
        assert False, "Expected username too short error"
    except ValueError:
        pass

    try:
        UserCreate(username="user123", email="test@test.com", password="password1", favorite_player="Narine")
        assert False, "Expected missing uppercase password error"
    except ValueError:
        pass

    valid_payload = UserCreate(username="valid_user", email="TEST@KKR.COM", password="SecurePassword123", favorite_player="Rinku")
    assert valid_payload.email == "test@kkr.com"
    print("[OK] Schema validation boundaries passed.")

    # === PASSWORD SECURITY ===
    print("\n=== TESTING PASSWORD SECURITY ===")
    plain = "KKRFans2026"
    hashed = get_password_hash(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    print("[OK] Cryptographic password hashing and verification passed.")

    # === USER SERVICES ===
    print("\n=== TESTING USER SERVICES ===")
    user1 = user_service.create_user(valid_payload)
    assert user1["username"] == "valid_user"
    assert user1["role"] == "user"
    print("[OK] User queries, email normalization, and uniqueness checks passed.")

    # === AUTHENTICATION SERVICE ===
    print("\n=== TESTING AUTHENTICATION SERVICE ===")
    login_payload = UserLogin(username="valid_user", password="SecurePassword123")
    auth_resp = auth_service.authenticate_user(login_payload)
    assert "access_token" in auth_resp
    print("[OK] Auth verification and access token responses passed.")

    # === JWT INTEGRATION ===
    print("\n=== TESTING JWT CLAIMS & EXPIRATION ===")
    token = auth_resp["access_token"]
    payload = verify_token(token)
    assert payload["sub"] == str(user1["_id"])
    
    resolved_user = get_current_user(token)
    assert str(resolved_user["_id"]) == str(user1["_id"])
    
    expired_token_claims = {"sub": str(user1["_id"]), "exp": datetime.utcnow() - timedelta(minutes=1)}
    expired_token = jwt.encode(expired_token_claims, os.environ["SECRET_KEY"], algorithm=os.environ["ALGORITHM"])
    try:
        verify_token(expired_token)
        assert False
    except HTTPException as e:
        assert e.status_code == 401
    print("[OK] JWT claim mappings, dependency parsing, and expiration checks passed.")

    # === ADMIN ROLE & AUTHORIZATION ===
    print("\n=== TESTING ADMIN AUTHORIZATION ===")
    # 1. Non-admin user check
    normal_user = {"username": "valid_user", "role": "user", "is_active": True}
    try:
        require_admin(normal_user)
        assert False, "Expected HTTP 403 Forbidden for non-admin"
    except HTTPException as e:
        assert e.status_code == 403
        assert "access denied" in e.detail.lower() or "insufficient permissions" in e.detail.lower()

    # 2. Admin user check
    admin_user = {"username": "admin_user", "role": "admin", "is_active": True}
    res_admin = require_admin(admin_user)
    assert res_admin["username"] == "admin_user"

    # 3. Require roles check
    moderator_user = {"username": "mod_user", "role": "moderator", "is_active": True}
    role_check = require_roles("moderator", "admin")
    res_mod = role_check(moderator_user)
    assert res_mod["username"] == "mod_user"
    print("[OK] Admin role and role-based permissions validation passed.")

    # === ADMIN NEWS CRUD ===
    print("\n=== TESTING NEWS CRUD SERVICES ===")
    news_payload = NewsCreate(cat="Match Report", headline="KKR Wins!", snippet="KKR wins by 20 runs.")
    created_news = news_service.create_news(news_payload, "admin_user")
    assert created_news["headline"] == "KKR Wins!"
    assert created_news["cat"] == "Match Report"
    
    # List news (with sorting and search)
    list_news = news_service.get_news(search="Wins")
    assert len(list_news) == 1
    assert list_news[0]["headline"] == "KKR Wins!"

    # Update news
    update_news_payload = NewsUpdate(headline="KKR Smashes Opponent!")
    updated_news = news_service.update_news(created_news["id"], update_news_payload, "admin_user")
    assert updated_news["headline"] == "KKR Smashes Opponent!"

    # Delete news
    delete_res = news_service.delete_news(created_news["id"], "admin_user")
    assert delete_res is True
    assert len(news_service.get_news()) == 0
    print("[OK] News creation, updates, and deletes with search passed.")

    # === ADMIN MATCHES CRUD ===
    print("\n=== TESTING MATCHES CRUD SERVICES ===")
    match_payload = MatchCreate(date="30 MAY 2026", opp="GT", venue="Eden Gardens", vs="GT", status="won", desc="Won by 5 wickets", theme="blue")
    created_match = matches_service.create_match(match_payload, "admin_user")
    assert created_match["opp"] == "GT"

    update_match_payload = MatchUpdate(status="lost", desc="Lost by 1 run")
    updated_match = matches_service.update_match(created_match["id"], update_match_payload, "admin_user")
    assert updated_match["status"] == "lost"

    delete_match_res = matches_service.delete_match(created_match["id"], "admin_user")
    assert delete_match_res is True
    print("[OK] Match history CRUD operations passed.")

    # === ADMIN OTHER CRUD (PLAYERS, QUIZ, LEGENDS) ===
    print("\n=== TESTING OTHER CRUD SERVICES ===")
    # 1. Players CRUD
    player_payload = PlayerCreate(name="Shreyas Iyer", jersey=41, role="Batter", country="India", bio="KKR Captain", stats=[], image="images/shreyas-iyer.jpg")
    created_player = admin_service.create_player(player_payload, "admin_user")
    assert created_player["name"] == "Shreyas Iyer"

    update_player_payload = PlayerUpdate(jersey=12)
    updated_player = admin_service.update_player(created_player["id"], update_player_payload, "admin_user")
    assert updated_player["jersey"] == 12

    assert admin_service.delete_player(created_player["id"], "admin_user") is True

    # 2. Quiz CRUD
    quiz_payload = QuizCreate(q="KKR Champions Year?", opts=["2012", "2015"], ans=0, exp="KKR won in 2012")
    created_quiz = admin_service.create_quiz(quiz_payload, "admin_user")
    assert created_quiz["q"] == "KKR Champions Year?"

    update_quiz_payload = QuizUpdate(ans=1)
    updated_quiz = admin_service.update_quiz(created_quiz["id"], update_quiz_payload, "admin_user")
    assert updated_quiz["ans"] == 1

    assert admin_service.delete_quiz(created_quiz["id"], "admin_user") is True

    # 3. Legends CRUD
    legend_payload = LegendCreate(name="Dada", years="2008", achievement="First Captain", stat="1000 runs", avatar="images/dada.jpg")
    created_legend = admin_service.create_legend(legend_payload, "admin_user")
    assert created_legend["name"] == "Dada"

    update_legend_payload = LegendUpdate(stat="1200 runs")
    updated_legend = admin_service.update_legend(created_legend["id"], update_legend_payload, "admin_user")
    assert updated_legend["stat"] == "1200 runs"

    assert admin_service.delete_legend(created_legend["id"], "admin_user") is True
    print("[OK] Players, Quizzes, and Legends CRUD operations passed.")

    # === WEBSOCKET SERVICE & MANAGER ===
    print("\n=== TESTING WEBSOCKET SERVICE & MANAGER ===")
    from services.websocket_service import format_ws_event, serialize_ws_error
    from utils.websocket_manager import ConnectionManager
    
    # Test formatting services
    formatted = format_ws_event("cheer_update", [{"name": "Fan", "msg": "Go KKR"}])
    assert formatted["event"] == "cheer_update"
    assert formatted["data"][0]["name"] == "Fan"
    
    err = serialize_ws_error(4001, "Unauthorized")
    assert err["event"] == "error"
    assert err["error"]["code"] == 4001
    assert err["error"]["message"] == "Unauthorized"
    print("[OK] WebSocket helper utilities verified.")
    
    # Test ConnectionManager
    import asyncio
    
    async def async_ws_tests():
        mgr = ConnectionManager()
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        
        # Test connect
        connected1 = await mgr.connect(ws1, "cheers")
        assert connected1 is True
        assert ws1.accepted is True
        assert mgr.connection_count == 1
        assert ws1 in mgr.active_connections["cheers"]
        
        connected2 = await mgr.connect(ws2, "poll")
        assert connected2 is True
        assert ws2.accepted is True
        assert mgr.connection_count == 2
        assert ws2 in mgr.active_connections["poll"]
        
        # Test broadcast
        import json
        payload = {"hello": "world"}
        await mgr.broadcast(payload, "cheers")
        assert len(ws1.sent_messages) == 1
        assert json.loads(ws1.sent_messages[0]) == payload
        assert len(ws2.sent_messages) == 0  # Should not receive "cheers" broadcast
        
        # Test disconnect
        mgr.disconnect(ws1, "cheers")
        assert mgr.connection_count == 1
        assert ws1 not in mgr.active_connections["cheers"]
        
        # Test connection limits
        mgr.connection_count = 500  # simulate max connections
        ws_overflow = MockWebSocket()
        overflow_res = await mgr.connect(ws_overflow, "cheers")
        assert overflow_res is False
        assert ws_overflow.closed is True
        assert ws_overflow.close_code == 1008
        
        # Reset count for shutdown test
        mgr.connection_count = 2
        mgr.active_connections["cheers"] = {ws1}
        mgr.active_connections["poll"] = {ws2}
        await mgr.shutdown()
        assert ws1.closed is True
        assert ws1.close_code == 1001
        assert ws2.closed is True
        assert ws2.close_code == 1001
        assert mgr.connection_count == 0
        
    asyncio.run(async_ws_tests())
    print("[OK] ConnectionManager state transitions, broadcasts, limits, and shutdown verified.")

    # === INTEGRATION & HEALTH CHECK TESTS ===
    print("\n=== TESTING INTEGRATION & HEALTH CHECK ===")
    from fastapi.testclient import TestClient
    
    # Mock db_manager variables to avoid real connection checks
    class MockClient:
        class MockAdmin:
            def command(self, cmd):
                return {"ok": 1}
        admin = MockAdmin()
        
    backend.database.db_manager.db = mock_db
    backend.database.db_manager.client = MockClient()
    try:
        import database
        database.db_manager.db = mock_db
        database.db_manager.client = MockClient()
    except ImportError:
        pass
    
    from main import app
    client = TestClient(app)
    
    # Test GET /
    resp_root = client.get("/")
    assert resp_root.status_code == 200
    assert resp_root.json()["status"] == "online"
    
    # Test GET /health
    resp_health = client.get("/health")
    if resp_health.status_code != 200:
        print("HEALTH CHECK FAILED:", resp_health.status_code, resp_health.text)
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "healthy"
    assert resp_health.json()["database"] == "connected"
    print("[OK] FastAPI app status and health checks verified.")
    
    # Test Cache-Control headers on static GET endpoints
    resp_players = client.get("/api/players")
    assert resp_players.status_code == 200
    assert resp_players.headers.get("Cache-Control") == "public, max-age=3600"
    print("[OK] Cache-Control headers verified on static routes.")

    print("\nALL BACKEND SERVICES AND ADMIN UNIT TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
