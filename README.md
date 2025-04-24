
# 🚄 Train Ticket Queue System (FastAPI + Redis)

명절 기차표 예약을 위한 대기열 시스템입니다.  
500명까지는 즉시 예약되며, 이후 500명은 대기열에 등록되어 순차적으로 예약 가능합니다.

FastAPI와 Redis 기반 REST API로 구현되었으며, Docker 환경에서 실행 가능합니다.

---

## 📦 기능 요약

| API 경로            | 설명 |
|---------------------|------|
| `POST /reserve`     | 사용자 예약 요청 처리 |
| `GET /status/{id}`  | 예약 상태 및 대기열 순번 확인 |
| `POST /process_queue` | 대기열 사용자 예약 처리 |
| `POST /admin/reset` | Redis 상태 초기화 (관리자 전용) |

---

## 🛠️ 실행 방법

### 1. 레포 클론
```bash
git clone https://github.com/yourname/train-queue-system.git
cd train-queue-system
```

### 2. Docker Compose로 서버 실행
```bash
docker-compose up --build
```

> FastAPI 서버는 `http://localhost:8000` 에서 실행됩니다.

---

## 🔁 API 예시 호출

### ➤ 1. 예약 요청
```bash
curl -X POST http://localhost:8000/reserve \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123"}'
```

### ➤ 2. 예약 상태 확인
```bash
curl http://localhost:8000/status/user_123
```

### ➤ 3. 대기열 처리 실행
```bash
curl -X POST http://localhost:8000/process_queue
```

### ➤ 4. Redis 초기화 (테스트용)
```bash
curl -X POST http://localhost:8000/admin/reset \
  -H "X-Token: my-secret-token"
```

---

## 🧪 테스트 시뮬레이션

`test_queue_simulation.py` 스크립트를 통해 1000명의 예약 요청을 병렬로 시뮬레이션하고 결과를 확인할 수 있습니다.

### 실행
```bash
pip install httpx
python test_queue_simulation.py
```

> 테스트 전 Redis를 초기화하고, 병렬 요청 → 큐 처리 → 상태 확인 순으로 흐름이 구성되어 있습니다.
- redis가 초기화됩니다.
- 10명의 사용자가 병렬로 예약을 시도합니다. 예약이 가능한 사용자들은 "reserved" 상태로, 나머지는 "queued" 상태로 대기열에 추가됩니다.
- 예약 후 큐 처리 API를 통해 대기열에서 일부 사용자들이 예약될 수 있도록 처리합니다.
- check_redis_status()를 통해 Redis에서의 reserved와 queue 상태를 출력합니다.
- 일부 사용자들에 대해 예약 상태를 출력합니다.

---

## 🧰 기술 스택

- Python 3.10
- FastAPI
- Redis
- Docker / Docker Compose
- httpx (비동기 HTTP 클라이언트)

---

## 🔐 관리자 API 인증

`/admin/reset` 호출 시 헤더에 아래 토큰을 포함해야 합니다.

```
X-Token: my-secret-token
```

> 운영 환경에서는 반드시 보안 강화를 고려하세요.

---

## 🧱 Redis 내부 구조

| 키              | 설명 |
|-----------------|------|
| `reserved_users` | 즉시 예약된 사용자 Set |
| `queue_users`    | 대기열에 등록된 사용자 Set (중복 방지용) |
| `waiting_queue`  | 예약 대기 순번이 들어있는 Redis List |

> 확장 시 Kafka 등 외부 큐 시스템으로 대체하거나 분산 Redis로 구성할 수 있습니다.

---

## 📂 디렉토리 구조

```
.
├── main.py                  # FastAPI 서버
├── test_queue_simulation.py # 병렬 테스트 스크립트
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🚀 향후 확장 아이디어

- Redis Cluster 및 Sentinel 기반 장애 대응 구조
- WebSocket 기반 실시간 대기 상태 알림
- Kafka 기반 비동기 예약 처리 구조
- 좌석 취소 및 대기열 자동 할당 로직
- 사용자 인증 (JWT, OAuth 등) 추가

---

## 📧 문의

궁금한 점이나 제안 사항은 [gusdn90@gmail.com](mailto:gusdn90@gmail.com) 으로 문의 주세요.
