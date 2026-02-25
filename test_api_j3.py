import urllib.request
import json
import sys

base_url = "http://localhost:8000/api/v1"

def request(method, url, data=None, token=None):
    req = urllib.request.Request(url, method=method)
    if data:
        json_data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
        req.data = json_data
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        response = urllib.request.urlopen(req)
        return response.getcode(), json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except:
            return e.code, None

# Get Beginner Token
status, data = request("POST", f"{base_url}/auth/login", data={
    "email_or_username": "beginner_e2e_2",
    "password": "Beginner123!"
})
beg_token = data.get("access_token")

# 3.1 Register Expert User
print("\n--- 3.1 Register Expert ---")
expert_user = "expert_user_j3"
status, data = request("POST", f"{base_url}/auth/register", data={
    "username": expert_user,
    "email": f"{expert_user}@cereforge.io",
    "password": "ExpertPassword1!",
    "skill_level": "advanced",
    "background": "Senior AI Systems Engineer"
})
if status != 201:
    status, data = request("POST", f"{base_url}/auth/login", data={
        "email_or_username": expert_user,
        "password": "ExpertPassword1!"
    })
exp_token = data.get("access_token")
print("Expert token present:", bool(exp_token))

# Get Expert starting XP
status, data = request("GET", f"{base_url}/auth/me", token=exp_token)
expert_start_xp = data.get("user", {}).get("xp", 0)
print("Expert Starting XP:", expert_start_xp)

# 3.2 Beginner posts question
print("\n--- 3.2 Beginner Posts ---")
post_req = {
    "title": "Stuck on embedding dimensions",
    "body": "Why does text-embedding-ada-002 output 1536 dimensions but the newer model outputs 3072? What happens if I put 1536 into a database expecting 3072?",
    "tags": ["embeddings", "vector-db", "openai"]
}
status, data = request("POST", f"{base_url}/posts", data=post_req, token=beg_token)
print("Status:", status)
post_id = data.get("post", {}).get("id")
print("Post ID:", post_id)

# 3.3 Expert answers question
print("\n--- 3.3 Expert Answers ---")
ans_req = {
    "body": "Different embedding models construct their latent spaces differently. Sending a 1536 length array to a 3072 dimension column in pgvector or Chroma will crash immediately because vector arithmetic requires identical dimensions. You need to migrate your database column or pad with zeros (which ruins the semantic math). Always match your DB schema to your model output shape."
}
status, data = request("POST", f"{base_url}/posts/{post_id}/comments", data=ans_req, token=exp_token)
print("Status:", status)
ans_id = data.get("comment", {}).get("id")
print("Answer ID:", ans_id)

# 3.4 Beginner accepts the answer
print("\n--- 3.4 Beginner Accepts ---")
status, data = request("POST", f"{base_url}/posts/{post_id}/comments/{ans_id}/accept", token=beg_token)
print("Status:", status)
print("Is accepted:", data.get("comment", {}).get("is_accepted"))

# 3.5 Verify XP awarded to Expert
print("\n--- 3.5 Verify Expert XP ---")
status, data = request("GET", f"{base_url}/auth/me", token=exp_token)
expert_new_xp = data.get("user", {}).get("xp", 0)
print("Expert final XP:", expert_new_xp)
print("Change:", expert_new_xp - expert_start_xp)

# 3.6 AI Mentor Interaction
print("\n--- 3.6 AI Mentor Interaction ---")
mentor_req = {
    "task_slug": "llm-prompt-chain",
    "user_message": "Can you give me a hint on how to extract sentiment?"
}
req = urllib.request.Request(f"{base_url}/ai-mentor/guidance", method="POST")
req.add_header("Content-Type", "application/json")
req.add_header("Authorization", f"Bearer {beg_token}")
req.data = json.dumps(mentor_req).encode("utf-8")
try:
    response = urllib.request.urlopen(req)
    print("Mentor AI response starts with:", response.read(60).decode("utf-8"))
except Exception as e:
    print("Mentor API failed:", getattr(e, "code", e))
