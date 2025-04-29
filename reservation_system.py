from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import redis
from redis.exceptions import RedisError
import uuid
import time

app = FastAPI()

# Redis Configuration
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# Constants
MAX_RESERVATIONS = 500
ADMIN_TOKEN = "my-secret-token"
LOCK_KEY = "reservation_lock"
LOCK_EXPIRE = 5  # seconds

class ReserveRequest(BaseModel):
    user_id: str = None  # Optional: if not provided, will generate UUID

def acquire_lock(user_id: str) -> bool:
    """Acquire Redis lock with expiration"""
    return bool(r.set(LOCK_KEY, user_id, nx=True, ex=LOCK_EXPIRE))

def release_lock(user_id: str) -> bool:
    """Release Redis lock if owned by the user"""
    if r.get(LOCK_KEY) == user_id:
        return bool(r.delete(LOCK_KEY))
    return False

def process_reservation(user_id: str):
    """Process reservation with proper checks"""
    # Check if user already has a reservation or is in queue
    if r.sismember("reserved_users", user_id):
        return {"status": "already_reserved"}
    if r.sismember("queue_users", user_id):
        return {"status": "already_in_queue"}

    # Check if spots are available
    if r.scard("reserved_users") < MAX_RESERVATIONS:
        r.sadd("reserved_users", user_id)
        return {"status": "reserved", "user_id": user_id}

    # Add to waiting queue if no spots available
    r.rpush("waiting_queue", user_id)
    r.sadd("queue_users", user_id)
    position = r.llen("waiting_queue")
    return {"status": "queued", "position": position, "user_id": user_id}

@app.post("/reserve")
async def reserve_ticket(req: ReserveRequest):
    user_id = req.user_id or str(uuid.uuid4())
    
    try:
        # Acquire lock for atomic operation
        if not acquire_lock(user_id):
            raise HTTPException(
                status_code=429, 
                detail="System is processing another request. Please try again."
            )
        
        try:
            return process_reservation(user_id)
        finally:
            release_lock(user_id)
            
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.get("/status/{user_id}")
async def check_status(user_id: str):
    try:
        if r.sismember("reserved_users", user_id):
            return {"status": "reserved", "user_id": user_id}
        elif r.sismember("queue_users", user_id):
            position = r.lpos("waiting_queue", user_id)
            return {
                "status": "in_queue",
                "position": position + 1 if position is not None else "unknown",
                "user_id": user_id
            }
        return {"status": "not_found", "user_id": user_id}
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.post("/process_queue")
async def process_queue(x_token: str = Header(None)):
    if x_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    promoted_users = []
    lock_id = str(uuid.uuid4())

    try:
        if not acquire_lock(lock_id):
            raise HTTPException(
                status_code=429,
                detail="Queue is being processed. Please try again later."
            )

        try:
            while r.scard("reserved_users") < MAX_RESERVATIONS:
                user_id = r.lpop("waiting_queue")
                if not user_id:
                    break
                r.srem("queue_users", user_id)
                r.sadd("reserved_users", user_id)
                promoted_users.append(user_id)
        finally:
            release_lock(lock_id)

        return {
            "status": "queue_processed",
            "promoted_users": promoted_users,
            "promoted_count": len(promoted_users)
        }
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.post("/admin/reset")
async def reset_data(x_token: str = Header(None)):
    if x_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        r.delete("reserved_users", "queue_users", "waiting_queue", LOCK_KEY)
        return {"status": "reset_done"}
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        r.ping()
        return {"status": "healthy"}
    except RedisError:
        raise HTTPException(status_code=503, detail="Redis connection error") 