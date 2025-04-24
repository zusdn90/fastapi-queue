import asyncio
import httpx

API_URL = "http://localhost:8000"
ADMIN_TOKEN = "my-secret-token"
TOTAL_USERS = 100

# ✅ Redis 초기화 API 호출
async def reset_redis():
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{API_URL}/admin/reset",
            headers={"X-Token": ADMIN_TOKEN}
        )
        return res.json()

# ✅ 예매 요청
async def reserve_ticket(user_id):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{API_URL}/reserve",
            json={"user_id": user_id}
        )
        return res.json()

# ✅ 예약 상태 확인
async def check_status(user_id):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_URL}/status/{user_id}")
        return res.json()

# ✅ 큐 처리 API 호출
async def process_queue():
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_URL}/process_queue")
        return res.json()

# ✅ Redis 상태 확인
async def check_redis_status():
    async with httpx.AsyncClient() as client:
        reserved_res = await client.get(f"{API_URL}/status/reserved")
        queue_res = await client.get(f"{API_URL}/status/queue")
        return {"reserved": reserved_res.json(), "queue": queue_res.json()}

# ✅ 전체 테스트 실행
async def main():
    print("🔄 Resetting Redis...")
    reset_result = await reset_redis()
    print(f"Reset result: {reset_result}")

    print(f"🚀 Simulating {TOTAL_USERS} concurrent reservations...")
    users = [f"user_{i}" for i in range(TOTAL_USERS)]

    # 병렬로 예약 시도
    results = await asyncio.gather(*(reserve_ticket(uid) for uid in users))

    reserved = [r for r in results if r["status"] == "reserved"]
    queued = [r for r in results if r["status"] == "queued"]
    already_reserved = [r for r in results if r["status"] == "already_reserved"]

    print(f"✅ Reserved: {len(reserved)}")
    print(f"⏳ Queued: {len(queued)}")
    print(f"🚫 Already Reserved: {len(already_reserved)}")

    print("🧾 Processing queue (simulate time pass)...")
    queue_result = await process_queue()
    print(f"Queue Result: {queue_result}")

    print("🔍 Checking Redis status...")
    redis_status = await check_redis_status()
    print(f"Redis Status: {redis_status}")

    # 예약 상태 확인 (선택적으로 일부 사용자만 출력)
    check_users = [f"user_{i}" for i in range(0, TOTAL_USERS, 2)]  # 확인할 사용자 목록을 간단하게 변경
    print("📋 Checking status for sample users:")
    for uid in check_users:
        status = await check_status(uid)
        print(f"{uid}: {status}")

# ✅ 실행
if __name__ == "__main__":
    asyncio.run(main())

