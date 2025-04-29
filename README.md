# 🚄 Train Ticket Queue System (FastAPI + Redis)

명절 기차표 예약을 위한 대기열 시스템입니다.  
500명까지는 즉시 예약되며, 이후에는 대기열에 등록되어 순차적으로 예약 가능합니다.

FastAPI와 Redis 기반 REST API로 구현되었으며, Docker 환경에서 실행 가능합니다.

---

## 📦 기능 요약

| API 경로            | 메서드 | 설명 | 인증 필요 |
|-------------------|--------|------|-----------|
| `/reserve`        | POST   | 사용자 예약 요청 처리 | No |
| `/status/{id}`    | GET    | 예약 상태 및 대기열 순번 확인 | No |
| `/process_queue`  | POST   | 대기열 사용자 예약 처리 | Yes |
| `/admin/reset`    | POST   | Redis 상태 초기화 | Yes |
| `/health`         | GET    | 시스템 상태 확인 | No |

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
# UUID 자동 생성
curl -X POST http://localhost:8000/reserve \
  -H "Content-Type: application/json" \
  -d '{}'

# 사용자 ID 지정
curl -X POST http://localhost:8000/reserve \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123"}'
```

### ➤ 2. 예약 상태 확인
```bash
curl http://localhost:8000/status/user_123
```

### ➤ 3. 대기열 처리 실행 (관리자)
```bash
curl -X POST http://localhost:8000/process_queue \
  -H "X-Token: my-secret-token"
```

### ➤ 4. Redis 초기화 (관리자)
```bash
curl -X POST http://localhost:8000/admin/reset \
  -H "X-Token: my-secret-token"
```

### ➤ 5. 시스템 상태 확인
```bash
curl http://localhost:8000/health
```

---

## 🧪 부하 테스트

시스템은 Locust를 사용하여 부하 테스트를 수행할 수 있습니다.

### 1. Locust 설치
```bash
pip install locust
```

### 2. 테스트 실행
```bash
locust -f locustfile.py
```

### 3. 웹 인터페이스 접속
브라우저에서 `http://localhost:8089` 접속 후 테스트 구성:
- Number of users: 동시 사용자 수
- Spawn rate: 초당 생성할 사용자 수
- Host: http://localhost:8000

### 테스트 시나리오
locustfile.py는 다음 작업들을 시뮬레이션합니다:
- 티켓 예약 (가중치: 4)
- 상태 확인 (가중치: 3)
- 시스템 상태 확인 (가중치: 2)
- 대기열 처리 (가중치: 1)
- 시스템 초기화 (가중치: 1)

---

## 🧰 기술 스택

- Python 3.10+
- FastAPI
- Redis
- Docker / Docker Compose
- Locust (부하 테스트)

---

## 🔐 관리자 API 인증

관리자 전용 엔드포인트(`/admin/reset`, `/process_queue`)는 헤더에 토큰이 필요합니다:

```
X-Token: my-secret-token
```

> ⚠️ 운영 환경에서는 반드시 보안 강화가 필요합니다.

---

## 🧱 Redis 데이터 구조

| 키 | 타입 | 설명 |
|---|------|------|
| `reserved_users` | Set | 예약 완료된 사용자 목록 |
| `queue_users` | Set | 대기열 등록된 사용자 목록 (중복 방지) |
| `waiting_queue` | List | 대기열 순서 |
| `reservation_lock` | String | 동시성 제어를 위한 분산 락 |

---

## 📂 프로젝트 구조

```
.
├── main.py           # FastAPI 애플리케이션
├── locustfile.py     # 부하 테스트 스크립트
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔒 동시성 제어

- Redis의 분산 락을 사용하여 동시성 문제 해결
- 락 타임아웃(5초)으로 데드락 방지
- 락 소유자만 락 해제 가능

---

## 🚀 향후 개선 사항

- Redis Cluster 구성으로 가용성 향상
- WebSocket 기반 실시간 대기열 상태 알림
- Kafka 기반 비동기 예약 처리
- 예약 취소 및 자동 재할당 기능
- JWT 기반 사용자 인증
- 관리자 대시보드 추가

---

## 📧 문의

궁금한 점이나 제안 사항은 [gusdn90@gmail.com](mailto:gusdn90@gmail.com) 으로 문의 주세요.
