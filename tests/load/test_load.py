from locust import HttpUser, task, between

class SubstansUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def test_agent_endpoint(self):
        self.client.post("/api/agent/process", json={
            "agent_id": "aad",
            "request": {"type": "analysis", "data": "test"}
        })
    
    @task(1)
    def test_document_generation(self):
        self.client.post("/api/documents/generate", json={
            "template": "report",
            "format": "pdf",
            "content": {"title": "Test Report"}
        })
