import requests

data = {"email_or_username": "engineer", "password": "password123"}
r_login = requests.post("http://localhost:8000/api/v1/auth/login", json=data)
if r_login.status_code != 200:
    print("Login failed:", r_login.text)
    exit(1)
token = r_login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

post_data = {"title": "Test Delete Post", "body": "This is a test to reproduce delete."}
r_post = requests.post("http://localhost:8000/api/v1/posts", headers=headers, json=post_data)
if r_post.status_code != 201:
    print("Post creation failed:", r_post.text)
    exit(1)
post_id = r_post.json()["post"]["id"]
print("Created post:", post_id)

r_del = requests.delete(f"http://localhost:8000/api/v1/posts/{post_id}", headers=headers)
print("Delete status:", r_del.status_code)
print("Delete response:", r_del.text)
