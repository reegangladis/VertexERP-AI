import random
from locust import HttpUser, between, task


class EnterpriseERPUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Simulated authentication
        self.org_id = "00000000-0000-0000-0000-000000000001"
        self.headers = {"Authorization": "Bearer mock_enterprise_jwt_token"}

    @task(3)
    def test_hr_employees_list(self):
        self.client.get(f"/api/v1/employees?org_id={self.org_id}", headers=self.headers)

    @task(2)
    def test_crm_leads_list(self):
        self.client.get(f"/api/v1/crm/leads?org_id={self.org_id}", headers=self.headers)

    @task(2)
    def test_inventory_products_list(self):
        self.client.get(f"/api/v1/inventory/products?org_id={self.org_id}", headers=self.headers)

    @task(2)
    def test_finance_dashboard(self):
        self.client.get(f"/api/v1/finance/dashboard?org_id={self.org_id}", headers=self.headers)

    @task(2)
    def test_manufacturing_dashboard(self):
        self.client.get(f"/api/v1/manufacturing/dashboard?org_id={self.org_id}", headers=self.headers)

    @task(3)
    def test_ai_copilot_chat(self):
        self.client.post(
            "/api/v1/ai/copilot/chat",
            json={
                "session_id": "00000000-0000-0000-0000-000000000001",
                "role": "user",
                "message": "What is the status of Q3 financial audit?",
            },
            headers=self.headers,
        )

    @task(1)
    def test_analytics_dashboard(self):
        self.client.get(f"/api/v1/analytics/dashboard?org_id={self.org_id}", headers=self.headers)

    @task(1)
    def test_ops_monitoring_dashboard(self):
        self.client.get(f"/api/v1/ops/dashboard?org_id={self.org_id}", headers=self.headers)
