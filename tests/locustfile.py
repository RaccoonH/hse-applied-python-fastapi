from locust import HttpUser, task, between
import threading
import random
import string


def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


class APIUser(HttpUser):
    wait_time = between(1, 3)
    token = None
    generated_codes = []
    codes_lock = threading.Lock()
    always_existed_code = None

    generated_emails = []
    email_lock = threading.Lock()
    always_existed_email = "locust@loadtest.com"

    def add_code(self, code):
        with self.codes_lock:
            self.generated_codes.append(code)

    def get_code(self, remove=False):
        with self.codes_lock:
            if remove is False:
                return random.choice(self.generated_codes) if len(self.generated_codes) > 0 else self.always_existed_code
            else:
                if len(self.generated_codes) == 0:
                    return None
                code = random.choice(self.generated_codes)
                self.generated_codes.remove(code)
                return code

    def remove_code(self, code):
        with self.codes_lock:
            self.generated_codes.remove(code)

    def get_user(self):
        with self.email_lock:
            return random.choice(self.generated_emails) if len(self.generated_emails) > 0 else self.always_existed_email

    def add_user(self, email):
        with self.email_lock:
            self.generated_emails.append(email)

    def on_start(self):
        with self.client.post("/auth/register", json={
            "email": self.always_existed_email,
            "password": "password",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False
        }, catch_response=True) as response:
            if response.json()["detail"] == "REGISTER_USER_ALREADY_EXISTS":
                response.success()

        response = self.client.post("/auth/jwt/login", data={
            "username": self.always_existed_email,
            "password": "password",
            "grant_type": "password",
        })

        self.token = response.json()["access_token"]

        with self.client.post("/links/shorten", headers=self.get_auth(), json={"orig_url": "http://google.com"}) as response:
            data = response.json()
            self.always_existed_code = data["data"]

    def get_auth(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def create_link(self):
        with self.client.post("/links/shorten", headers=self.get_auth(), json={"orig_url": "http://google.com"}) as response:
            data = response.json()
            self.add_code(data["data"])

    @task(5)
    def create_wrong_link(self):
        with self.client.post("/links/shorten", headers=self.get_auth(), json={"orig_url": "wrong_url"}, catch_response=True) as response:
            if response.status_code == 400:
                response.success()

    @task(5)
    def get_link(self):
        self.client.get(f"/links/{self.get_code()}", headers=self.get_auth())

    @task(5)
    def get_non_existed_link(self):
        with self.client.get("/links/00000000", headers=self.get_auth(), catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    @task(5)
    def get_wrong_link(self):
        with self.client.get("/links/wrong_url", headers=self.get_auth(), catch_response=True) as response:
            if response.status_code == 400:
                response.success()

    @task(5)
    def update_link(self):
        old_code = self.get_code(True)
        if old_code is None:
            return
        with self.client.put(f"/links/{old_code}", headers=self.get_auth(), json={}) as response:
            self.add_code(response.json()['data'])

    @task(5)
    def update_wrong_link(self):
        with self.client.put("/links/wrong_url", headers=self.get_auth(), json={}, catch_response=True) as response:
            if response.status_code == 400:
                response.success()

    @task(5)
    def update_nonexisted_link(self):
        with self.client.put("/links/00000000", headers=self.get_auth(), json={}, catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    @task(1)
    def delete_link(self):
        code = self.get_code(True)
        if code is not None:
            self.client.delete(f"/links/{code}", headers=self.get_auth())

    @task(1)
    def delete_wrong_link(self):
        with self.client.delete("/links/wrong_url", headers=self.get_auth(), catch_response=True) as response:
            if response.status_code == 400:
                response.success()

    @task(1)
    def delete_nonexisted_link(self):
        with self.client.delete("/links/00000000", headers=self.get_auth(), catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    @task(5)
    def get_stats(self):
        self.client.get(f"/links/{self.get_code()}/stats", headers=self.get_auth())

    @task(5)
    def get_stats_wrong_code(self):
        with self.client.get("/links/wrong_url/stats", headers=self.get_auth(), catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    @task(5)
    def get_stats_nonexisted_code(self):
        with self.client.get("/links/00000000/stats", headers=self.get_auth(), catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    @task(1)
    def register(self):
        email = f"locust@{generate_code()}.com"
        self.client.post("/auth/register", json={
            "email": email,
            "password": "password",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False
        })
        self.add_user(email)

    @task(3)
    def login(self):
        self.client.post("/auth/jwt/login", data={
            "username": self.get_user(),
            "password": "password",
            "grant_type": "password",
        })

    @task(3)
    def login_wrong_creds(self):
        with self.client.post("/auth/jwt/login", data={
            "username": "non_existed_user@test.com",
            "password": "password",
            "grant_type": "password",
        }, catch_response=True) as response:
            if response.status_code == 400:
                response.success()
