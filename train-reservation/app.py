"""
1. 요구사항 요약
기차표 1장이 남은 상태

여러 명이 동시에 예약 요청

Redis 락을 이용해 하나의 사용자만 예약 가능하도록 처리

락은 일정 시간 후 자동 해제

락 해제는 락을 획득한 사용자만 가능하도록
"""

from fastapi import FastAPI, HTTPException
from redis import Redis
import uuid
import time

app = FastAPI()
redis_client = Redis(host='redis', port=6379, db=0, decode_responses=True)

TICKET_KEY = "train_ticket"         # 실제 티켓 수를 저장하는 키
LOCK_KEY = "train_ticket_lock"      # 락 키
LOCK_EXPIRE = 5                     # 락 TTL (초)

# 초기화: 티켓 1장만 있다고 가정
@app.on_event("startup")
def init_ticket():
    redis_client.set(TICKET_KEY, 1)


@app.post("/reserve")
def reserve_ticket():
    user_id = str(uuid.uuid4())  # 각 요청을 구분하는 고유 ID

    # 1. 락 획득 시도
    lock_acquired = redis_client.set(LOCK_KEY, user_id, nx=True, ex=LOCK_EXPIRE)
    
    if not lock_acquired:
        raise HTTPException(status_code=429, detail="예약 중입니다. 잠시 후 다시 시도해주세요.")

    try:
        # 2. 티켓 수 확인
        ticket_count = int(redis_client.get(TICKET_KEY) or 0)
        if ticket_count <= 0:
            raise HTTPException(status_code=400, detail="티켓 매진")

        # 3. 티켓 차감
        redis_client.decr(TICKET_KEY)

        # 4. 예약 성공 응답
        return {"message": "예약 성공!", "user_id": user_id}

    finally:
        # 5. 락 해제 (내가 획득한 락일 때만 해제)
        lock_value = redis_client.get(LOCK_KEY)
        if lock_value == user_id:
            redis_client.delete(LOCK_KEY)


