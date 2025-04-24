from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import redis
from redis.exceptions import RedisError
from threading import Lock

app = FastAPI()

# Redis 설정
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# 예약 가능한 인원 수
MAX_RESERVATIONS = 500

# 관리자 토큰 (테스트용)
ADMIN_TOKEN = "my-secret-token"

# Lock 객체로 동시성 제어
reserve_lock = Lock()

class ReserveRequest(BaseModel):
    user_id: str

# 예약 처리 함수
def process_reservation(user_id: str):
    # 이미 예약했거나 대기 중인 유저라면 무시
    if r.sismember("reserved_users", user_id):
        return {"status": "already_reserved"}
    if r.sismember("queue_users", user_id):
        return {"status": "already_in_queue"}

    # 예약 가능 인원이면 예약 처리
    if r.scard("reserved_users") < MAX_RESERVATIONS:
        r.sadd("reserved_users", user_id)
        return {"status": "reserved"}

    # 그렇지 않으면 대기열에 추가
    r.rpush("waiting_queue", user_id)
    r.sadd("queue_users", user_id)
    return {"status": "queued"}

@app.post("/reserve")
def reserve_ticket(req: ReserveRequest):
    user_id = req.user_id
    
    # 동시성 처리: 예약 처리 중에는 다른 요청을 기다리게 함
    with reserve_lock:
        try:
            return process_reservation(user_id)
        except RedisError as e:
            raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.get("/status/{user_id}")
def check_status(user_id: str):
    try:
        if r.sismember("reserved_users", user_id):
            return {"status": "reserved"}
        elif r.sismember("queue_users", user_id):
            position = r.lpos("waiting_queue", user_id)
            return {"status": "in_queue", "position": position + 1 if position is not None else "unknown"}
        else:
            return {"status": "not_found"}
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.post("/process_queue")
def process_queue():
    promoted_users = []

    try:
        # 대기열에서 사용자들을 예약 처리
        while r.scard("reserved_users") < MAX_RESERVATIONS:
            user_id = r.lpop("waiting_queue")
            if not user_id:
                break
            r.srem("queue_users", user_id)
            r.sadd("reserved_users", user_id)
            promoted_users.append(user_id)
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

    return {"status": "queue_processed", "promoted_users": promoted_users}

@app.post("/admin/reset")
def reset_data(x_token: str = Header(None)):
    if x_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Redis 데이터 삭제
        r.delete("reserved_users")
        r.delete("queue_users")
        r.delete("waiting_queue")
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

    return {"status": "reset_done"}

