from locust import HttpUser, task, between
import uuid

class ReservationUser(HttpUser):
    wait_time = between(1, 2)
    admin_token = "my-secret-token"
    
    def on_start(self):
        """Initialize user-specific data on start"""
        self.my_user_id = str(uuid.uuid4())
        self.headers = {"accept": "application/json", "content-type": "application/json"}
        self.admin_headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-token": self.admin_token
        }

    @task(4)  # Higher weight for the main reservation endpoint
    def reserve_ticket(self):
        """Test ticket reservation endpoint"""
        self.client.post(
            "/reserve",
            json={"user_id": self.my_user_id},
            headers=self.headers,
            name="/reserve"
        )

    @task(3)  # Check status frequently
    def check_status(self):
        """Test status check endpoint"""
        self.client.get(
            f"/status/{self.my_user_id}",
            headers=self.headers,
            name="/status"
        )

    @task(1)  # Less frequent admin operations
    def process_queue(self):
        """Test queue processing endpoint (admin only)"""
        self.client.post(
            "/process_queue",
            headers=self.admin_headers,
            name="/process_queue"
        )

    @task(1)  # Less frequent admin operations
    def reset_data(self):
        """Test system reset endpoint (admin only)"""
        self.client.post(
            "/admin/reset",
            headers=self.admin_headers,
            name="/admin/reset"
        )

    @task(2)  # Regular health checks
    def health_check(self):
        """Test health check endpoint"""
        self.client.get(
            "/health",
            headers=self.headers,
            name="/health"
        )

