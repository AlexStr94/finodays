# pip install locust==2.15.0
from locust import between, HttpUser, task


class MobileApp(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        while True:
            try:
                response = self.client.post(
                    '/api/v1/auth',
                    data={
                        'username': 'username',
                        'password': 'password2'
                    }
                )
                token = response.json().get('access_token')
                self.client.headers = {'Authorization': f'Bearer {token}'}

                response = self.client.get('/api/v1/cards')
                account_list = response.json()
                centr_invest_accounts = list(filter(lambda x: x['bank'] == 'Центр-инвест', account_list))
                self.account_number = centr_invest_accounts[0].get('account_number')
                break
            except Exception:
                continue

    @task
    def get_cards_list(self):
        self.client.get('/api/v1/cards')

    @task
    def get_transactions(self):
        self.client.get('/api/v1/transactions/')

    @task
    def get_cashback_for_choose(self):
        self.client.get(
            '/api/v1/get_cashback_for_choose/',
            params={
                'account_number': self.account_number
            }
        )