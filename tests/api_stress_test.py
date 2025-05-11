from locust import HttpUser, task, between
from json import load, loads
from random import choice, random, randint
from users_generator import random_password

DOMAIN = "http://localhost:8000"
PROBLEMS = ['string1', 'string']
ADMIN_TOKEN = "e0cc4347-9d2b-4505-ab09-f0ccf46e3695"

users = []

with open("users.json", 'r', encoding='UTF-8') as file:
    users = load(file)

class ApiUserTest(HttpUser):
    user: dict
    token: str
    email: str
    password: str

    def on_start(self):
        self.user = choice(users)
        self.email = self.user.get('email', None)
        self.password = self.user.get('password', None)
        data = self.client.post(f"{DOMAIN}/api/v1/user/login", json=self.user).text
        self.token = loads(data).get('token', None)

    def on_stop(self):
        pass

    @task
    def login(self):
        self.client.post(f"{DOMAIN}/api/v1/user/login", json=choice(users))

    @task
    def user_list(self):
        self.client.post(f'{DOMAIN}/api/v1/user', json={
            "token": ADMIN_TOKEN
        })

    # @task
    # def verify_email(self):
    #     self.client.post(f"{DOMAIN}/api/v1/user/verify-email", json={"token": })

    # @task
    # def change_password(self):
    #     self.client.post(f"{DOMAIN}/api/v1/user/change-password", json={
    #         "token": self.token,
    #         "old_password": self.password,
    #         "new_password": self.password
    #     })

    # @task
    # def issue_delete(self):
    #     issues = loads(self.client.post(f"{DOMAIN}/api/v1/issue/find").text)
    #     if not(issues is None):
    #         self.client.delete(
    #             f'{DOMAIN}/api/v1/issue/delete', json={
    #                 "id": choice(issues).get('id'),
    #                 "token": ADMIN_TOKEN
    #         }
    #         )

    @task
    def issue_get(self):
        self.client.get(f"{DOMAIN}/api/v1/issue/find")

    @task
    def issue_amount(self):
        self.client.get(f"{DOMAIN}/api/v1/issue/amount")

    @task
    def issue_types(self):
        self.client.get(f"{DOMAIN}/api/v1/issue/types")

    @task
    def issue_create(self):
        self.client.post(
            f"{DOMAIN}/api/v1/issue/create", json={
                "token": self.token,
                "type": choice(PROBLEMS),
                "short_desc": "dgfbjsbiooibsfbfsiobfoishoisfhobisdfhboifsdihpbsdfsbhoifpsbfdophbsdfhifdsfsdbfdsohibsdfpohibodfshisdfhibfdshbhssbdfhopbsdfsbpsdfohpssfdbfdbfdbfphbfsdbfdbsdhdfbshdbsfhibsfdhpdsbhbdsfphsbdfoihbspdf",
                "full_desc": "dgfbjsbiooibsfbfsiobfoishoisfhobisdfhboifsdihpbsdfsbhoifpsbfdophbsdfhifdsfsdbfdsohibsdfpohibodfshisdfhibfdshbhssbdfhopbsdfsbpsdfohpssfdbfdbfdbfphbfsdbfdbsdhdfbshdbsfhibsfdhpdsbhbdsfphsbdfoihbspdf",
                "address": "41539046893528-3582-09572935729-357235235234",
                "latitude": f'{random() + randint(-89, 89): .15f}',
                "longitude": f'{random() + randint(-179, 179): .15f}'
            }
        )

    @task
    def issue_status(self):
        issues = loads(self.client.get(f"{DOMAIN}/api/v1/issue/find").text)
        if not(issues is None):
            self.client.post(
                f'{DOMAIN}/api/v1/issue/status', json={
                    "id": choice(issues).get('id'),
                    "token": ADMIN_TOKEN,
                    "status": choice(["в обработке", "выполнено"])
                }
            )

    @task
    def statistics_types(self):
        self.client.get(f"{DOMAIN}/api/v1/statistics/types")

    @task
    def statistics_status(self):
        self.client.get(f"{DOMAIN}/api/v1/statistics/status")
