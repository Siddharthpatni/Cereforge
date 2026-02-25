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

status, data = request("POST", f"{base_url}/auth/login", data={
    "email_or_username": "beginner_e2e_2",
    "password": "Beginner123!"
})
token = data.get("access_token")

# 2.7b Complete final task (Agent Fundamentals)
print("\n--- 2.7b Complete Agent Fundamentals ---")
req_agent = {
    "solution_text": "An AI agent is an autonomous system that perceives its environment, makes decisions, and takes actions to achieve a specific goal. LangChain allows building agents with its ReAct framework. Tools let the agent interact with APIs, perform internet searches, or query databases. Memory enables the agent to remember context across conversation turns."
}
status, data = request("POST", f"{base_url}/tasks/agent-fundamentals/submit", data=req_agent, token=token)
print("Status:", status)
print("XP:", data.get("xp_earned"))

# 2.8 Verify Zero to AI is complete
print("\n--- 2.8 Verify Zero to AI complete ---")
status, data = request("GET", f"{base_url}/paths/zero-to-ai-path", token=token)
print("Progress % (expect 100.0):", data.get("progress"))
