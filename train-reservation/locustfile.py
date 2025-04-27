from locust import HttpUser, task, between

class ReserveUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def reserve_ticket(self):
        self.client.post(
            "/reserve",
            json={},  # 빈 JSON이라도 보내줘야 FastAPI가 오류 없이 처리함
        )

