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

# Login as beginner_e2e_2 from Journey 1
status, data = request("POST", f"{base_url}/auth/login", data={
    "email_or_username": "beginner_e2e_2",
    "password": "Beginner123!"
})
token = data.get("access_token")

# 2.1 List Paths
print("\n--- 2.1 List Paths ---")
status, data = request("GET", f"{base_url}/paths", token=token)
print("Status:", status)
print("Paths Count:", len(data))
zero_to_ai = next((p for p in data if p["slug"] == "zero-to-ai-path"), None)
print("Zero-to-AI recommended:", zero_to_ai.get("is_recommended"))
agents = next((p for p in data if p["slug"] == "agents-masterclass-path"), None)
print("Agents recommended:", agents.get("is_recommended"))
print("Enrolled:", zero_to_ai.get("enrolled"))

# 2.2 Enroll
print("\n--- 2.2 Enroll Zero-to-AI ---")
status, data = request("POST", f"{base_url}/paths/zero-to-ai-path/enroll", token=token)
print("Status:", status)
print("Enrolled response:", data.get("enrolled"))
print("Next task slug:", data.get("next_task_slug"))

# 2.3 Verify enrollment saved
print("\n--- 2.3 Verify Enrollment ---")
status, data = request("GET", f"{base_url}/paths", token=token)
zero_to_ai = next((p for p in data if p["slug"] == "zero-to-ai-path"), None)
print("Enrolled state:", zero_to_ai.get("enrolled"))
print("Progress %:", zero_to_ai.get("progress"))

# 2.4 Path detail
print("\n--- 2.4 Path Detail ---")
status, data = request("GET", f"{base_url}/paths/zero-to-ai-path", token=token)
print("Modules count:", len(data.get("modules", [])))
print("First module lesson type:", data["modules"][0]["lessons"][0]["lesson_type"])
print("Task sequence length:", len(data.get("task_sequence", [])))
print("Enrolled:", data.get("enrolled"))
print("Next task:", data.get("next_task"))

# 2.5 Submit next task
print("\n--- 2.5 Continue Path (CV Task missed?) Wait, next should be rag-intro-flow ---")
# The QA script says submit rag-intro-flow
req_rag = {
    "solution_text": "RAG pipeline design for law firm policy manual chatbot. ASCII diagram: PDF_UPLOAD -> [LOADER: PyPDFLoader splits into pages] -> [CHUNKER: RecursiveCharacterTextSplitter 512 tokens 50 overlap] -> [EMBEDDER: text-embedding-3-small converts each chunk to 1536-dim vector] -> [VECTOR_DB: Chroma stores vectors with metadata] -> OFFLINE DONE. ONLINE: USER_QUESTION -> [QUERY_EMBEDDER: same model embeds question] -> [RETRIEVER: cosine similarity search returns top 5 chunks] -> [CONTEXT_BUILDER: concatenates retrieved chunks] -> [LLM: GPT-4o receives question plus context] -> ANSWER. The chunking uses 50 token overlap to avoid cutting sentences at chunk boundaries. I chose Chroma because it runs locally without an API key and is perfect for a 500 page document corpus."
}
status, data = request("POST", f"{base_url}/tasks/rag-intro-flow/submit", data=req_rag, token=token)
print("Status:", status)
print("XP:", data.get("xp_earned"))
badges = [b.get("slug") for b in data.get("newly_earned_badges", [])]
print("Badges:", badges)

# 2.6 Check path progress
print("\n--- 2.6 Check progress ---")
status, data = request("GET", f"{base_url}/paths/zero-to-ai-path", token=token)
print("Progress % (expect 80.0):", data.get("progress"))
print("Next task:", data.get("next_task"))

# 2.7 Complete final task
print("\n--- 2.7 Complete CV Task ---")
req_cv = {
    "solution_text": "Computer Vision industry survey. 1. Healthcare: diabetic retinopathy screening using CNN classification on retinal fundus photos. Google DeepMind achieved 94% specialist-level accuracy. Reduced diagnosis time from weeks to minutes. 2. Automotive: pedestrian and obstacle detection using YOLO real-time detection. Tesla Autopilot processes 2300 frames per second across 8 cameras. Enabled level 2 autonomous driving at scale. 3. Retail: cashierless checkout using multi-camera object tracking. Amazon Go tracks items picked up by customers. Reduced checkout friction to zero. 4. Agriculture: crop disease detection using CNN classification on drone imagery. Prospera identifies 50+ diseases with 95% accuracy. Saves 30% on pesticide costs. 5. Manufacturing: defect detection using anomaly detection CV. BMW uses it on assembly lines. Reduces defect escape rate by 90%. 6. Security: facial recognition using deep metric learning. Clearview AI searches 30 billion images in under 1 second. 7. Sports: player tracking using multi-object tracking algorithms. Stats Perform tracks every player in real time for broadcast analytics. 8. Media: deepfake detection using binary classification CNNs. Microsoft Video Authenticator detects manipulated videos. 9. Construction: progress monitoring using 3D reconstruction from photos. OpenSpace creates site digital twins automatically. 10. Logistics: package sorting using OCR and barcode detection. Amazon robotics processes 2 million packages per day. The industry with the largest untapped CV potential is healthcare diagnostics. AI can match specialist accuracy in radiology but there are 2 billion people globally without access to radiologists."
}
status, data = request("POST", f"{base_url}/tasks/cv-real-world-survey/submit", data=req_cv, token=token)
print("Status:", status)
print("XP:", data.get("xp_earned"))
badges = [b.get("slug") for b in data.get("newly_earned_badges", [])]
print("Badges:", badges)

# 2.8 Verify Zero to AI is complete
print("\n--- 2.8 Verify Zero to AI complete ---")
status, data = request("GET", f"{base_url}/paths/zero-to-ai-path", token=token)
print("Progress % (expect 100.0):", data.get("progress"))
