import os
os.environ.setdefault("GMAIL_USER", "test@example.com")
os.environ.setdefault("GMAIL_APP_PASSWORD", "dummy")

from app import app

client = app.test_client()
resp = client.post('/signup', data={'email':'test@example.com'}, follow_redirects=True)
print('STATUS', resp.status_code)
print(resp.data.decode()[:800])
