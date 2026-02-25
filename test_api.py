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

# Create a new user to start fresh
username = "beginner_e2e_2"
print("--- REGISTER ---")
status, data = request("POST", f"{base_url}/auth/register", data={
    "username": username,
    "email": f"{username}@cereforge.io",
    "password": "Beginner123!",
    "skill_level": "absolute_beginner",
    "background": "I am a web developer wanting to learn AI"
})
if status != 201:
    print(f"Register failed: {status} {data}")
    # try logging in if already exists
    status, data = request("POST", f"{base_url}/auth/login", data={
        "email_or_username": username,
        "password": "Beginner123!"
    })
token = data.get("access_token")

# 1.4 Submit first task
print("\n--- 1.4 Submit Task 1 ---")
req_data = {
    "solution_text": "My solution uses three chained prompts. Step 1 prompt extracts the core sentiment and key complaints from the product review using clear extraction instructions. Step 2 prompt takes those extracted points and rewrites them in professional business report language. Step 3 prompt takes the clean summary and generates one specific action item for the product team to address the top complaint.",
    "colab_link": "https://colab.research.google.com/drive/example123",
    "notes": "I found the hint about input/output flow very helpful"
}
status, data = request("POST", f"{base_url}/tasks/llm-prompt-chain/submit", data=req_data, token=token)
print("Status:", status)
print("XP Earned:", data.get("xp_earned"))
print("Total XP:", data.get("total_xp"))
print("Rank:", data.get("rank", {}).get("name"))
badges = [b.get("slug") for b in data.get("newly_earned_badges", [])]
print("Newly Earned Badges:", badges)
print("Zero-to-AI badge present:", "zero-to-ai" in badges)
print("Prompt-Whisperer badge present:", "prompt-whisperer" in badges)

# 1.5 Double submission
print("\n--- 1.5 Double Submit ---")
status, data2 = request("POST", f"{base_url}/tasks/llm-prompt-chain/submit", data=req_data, token=token)
print("Status:", status)
print("Response Message:", data2.get("detail"))

# 1.6 Submit second LLM task
print("\n--- 1.6 Submit Task 2 ---")
req_data2 = {
    "solution_text": "I rewrote all 5 prompts with significant token reduction. For prompt 1, I removed the preamble phrase Please kindly help me and the filler I would like you to, reducing from 45 tokens to 28 tokens which is a 38 percent reduction. For prompt 2, I eliminated the redundant restatement of context and the closing thank you phrase, reducing from 60 tokens to 35 tokens which is a 42 percent reduction. For prompt 3 I replaced the multi-sentence explanation of what I want with a direct imperative command, achieving 44 percent reduction. The daily cost saving at 100000 calls per day and $0.001 per 1K tokens would be approximately $3.20 per day or $1168 per year."
}
status, data = request("POST", f"{base_url}/tasks/llm-token-optimizer/submit", data=req_data2, token=token)
print("Status:", status)
print("XP Earned:", data.get("xp_earned"))
badges = [b.get("slug") for b in data.get("newly_earned_badges", [])]
print("Newly Earned Badges:", badges)
print("Chain-Master badge NOT present:", "chain-master" not in badges)

# 1.7 Submit third LLM task
print("\n--- 1.7 Submit Task 3 ---")
req_data3 = {
    "solution_text": "Fine-tuning strategy for SaaS customer support LLM. Dataset format: JSONL with messages array containing role and content fields. Example record: {messages: [{role: system, content: You are a helpful SaaS support agent}, {role: user, content: How do I reset my password?}, {role: assistant, content: To reset your password go to Settings then Security}]}. Split ratios: 80 percent training 10 percent validation 10 percent test. Base model: Mistral-7B-Instruct because it has strong instruction following, fits on a single A100, and costs 0.0008 per 1K tokens to fine-tune on Together.ai. Hyperparameters: learning rate 2e-5 with cosine decay, 3 epochs, batch size 16, max sequence length 512 tokens. Evaluation metrics: perplexity on validation set automated, BLEU score for response similarity, and human evaluation on 100 sampled responses for helpfulness and accuracy. Estimated cost: 50000 conversations at average 300 tokens each is 15 million tokens, at $0.0008 per 1K = $12 total training cost."
}
status, data = request("POST", f"{base_url}/tasks/llm-finetuning-blueprint/submit", data=req_data3, token=token)
print("Status:", status)
print("XP Earned:", data.get("xp_earned"))
badges = [b.get("slug") for b in data.get("newly_earned_badges", [])]
print("Newly Earned Badges:", badges)
print("Chain-Master badge IS present:", "chain-master" in badges)

# Check total XP and Rank
status, data = request("GET", f"{base_url}/auth/me", token=token)
print("\n--- Final Check (Step 1.7 Rank check) ---")
print("Total XP:", data.get("user", {}).get("xp"))
print("Rank Name:", data.get("rank", {}).get("name"))
print("Total Badges:", len(data.get("badges", [])))
