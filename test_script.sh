#!/bin/bash
RES=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "beginner_dash",
    "email": "beginner_dash@cereforge.io",
    "password": "Beginner123!",
    "skill_level": "absolute_beginner",
    "background": "I am a web developer wanting to learn AI"
  }')
echo "REG Response: $RES"
TOKEN=$(echo $RES | jq -r .access_token)

echo "Dashboard Response:"
curl -s http://localhost:8000/api/v1/dashboard -H "Authorization: Bearer $TOKEN" | jq .

echo "Task Detail Response:"
curl -s http://localhost:8000/api/v1/tasks/llm-prompt-chain -H "Authorization: Bearer $TOKEN" | jq .
