# 🚄 Train Ticket Reservation Service (FastAPI + Redis)

간단한 기차표 예약 서비스를 구현한 프로젝트입니다.  
**FastAPI** 기반으로 REST API를 제공하며, **Redis**를 사용하여 동시성 제어(락)를 구현하고,  
**Locust**로 동시 요청 부하 테스트를 수행할 수 있습니다.

---

## ✅ 요구사항
- 기차표 1장이 남은 상태
- 여러 명이 동시에 예약 요청
- Redis 락을 이용해 하나의 사용자만 예약 가능하도록 처리
- 락은 일정 시간 후 자동 해제
- 락 해제는 락을 획득한 사용자만 가능하도록
- 핵심은 Redis SETNX (SET key value NX PX)를 이용한 분산 락

---

## ✅ 기술 스택
- Python 3.10+
- Docker / Docker Compose
- Redis
- Locust (성능 테스트 도구)

---

## 📁 프로젝트 구조

```
train-reservation/
├── app.py                  # FastAPI 앱
├── requirements.txt        # 의존성 패키지
├── Dockerfile              # 앱 이미지 빌드용
├── docker-compose.yml      # 전체 서비스 구성
├── locustfile.py           # 부하 테스트 스크립트
└── README.md
```

---

## 📦 의존성 설치 (`requirements.txt`)

```text
fastapi
uvicorn
redis
```

---

## 🐳 Dockerfile

```Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🧱 docker-compose.yml

```yaml
version: "3.8"

services:
  app:
    build: .
    container_name: train-reservation-app
    ports:
      - "8000:8000"
    depends_on:
      - redis
    networks:
      - train-net

  redis:
    image: redis:latest
    container_name: redis-server
    ports:
      - "6379:6379"
    networks:
      - train-net

networks:
  train-net:
    driver: bridge
```

---

## 🚀 실행 방법

### 1. 전체 서비스 빌드 및 실행

```bash
docker-compose up --build
```

FastAPI → [http://localhost:8000/docs](http://localhost:8000/docs) 에서 Swagger 확인 가능

---

## 🎯 API 설명

```http
POST /reserve
```

- 기차표 예약 시도
- Redis 분산락을 통해 동시성 제어
- 티켓이 없을 경우 400 에러
- 락 획득 실패 시 429 에러

---

## 🧪 Locust 부하 테스트

### 1. Locust 설치 (로컬 테스트 시)

```bash
pip install locust
```

### 2. locustfile.py 작성

```python
from locust import HttpUser, task, between

class ReserveUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def reserve(self):
        self.client.post("/reserve")
```

### 3. 실행

```bash
locust -f locustfile.py --host=http://localhost:8000
```

### 4. 브라우저 접속

[http://localhost:8089](http://localhost:8089)

여기서 사용자 수, 요청 속도 등을 설정하여 테스트할 수 있습니다.

---

## 📌 예외 처리 및 개선 포인트

- Redis 연결 실패 시 재시도 로직 필요
- 락 해제를 Lua 스크립트로 보완 가능
- 사용자 인증 연동 시 세션 기반 제어 필요

---

## 🔗 참고

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Redis Python Client](https://pypi.org/project/redis/)
- [Locust 문서](https://docs.locust.io/en/stable/)