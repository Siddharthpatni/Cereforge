# CereForge System Architecture & Flows

This document outlines the core architecture and user flows of the CereForge application using standard Mermaid.js sequence and system diagrams. These can be rendered directly in GitHub or viewed in markdown presentation tools.

## 1. High-Level System Architecture

This diagram shows the container-level architecture of the CereForge platform.

```mermaid
graph TD
    User([User / Browser])
    
    subgraph Frontend [Frontend Tier]
        Vite[React + Vite App\nZustand, Tailwind, React Query]
    end
    
    subgraph Backend [Backend API Tier]
        FastAPI[FastAPI Server\nPython 3.11, Uvicorn, Pydantic]
        Celery[Celery Workers\nOptional Background Tasks]
    end
    
    subgraph Data [Data Tier]
        PG[(PostgreSQL 15\nUsers, Tasks, Submissions)]
        Redis[(Redis 7\nCache & Rate Limiting)]
    end
    
    subgraph External [External Services]
        Gemini[Google Gemini API\nAI Mentor & Grading]
    end

    User -->|HTTP/HTTPS| Vite
    Vite -->|REST API / JSON| FastAPI
    Vite -->|Server-Sent Events| FastAPI
    
    FastAPI -->|SQLAlchemy| PG
    FastAPI -->|aioredis| Redis
    Celery -->|aioredis| Redis
    
    FastAPI -->|HTTP REST| Gemini
    
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px,color:#000;
    classDef backend fill:#38bdf8,stroke:#333,stroke-width:2px,color:#000;
    classDef db fill:#336791,stroke:#333,stroke-width:2px,color:#fff;
    classDef redis fill:#dc382d,stroke:#333,stroke-width:2px,color:#fff;
    classDef external fill:#facc15,stroke:#333,stroke-width:2px,color:#000;
    
    class Vite frontend;
    class FastAPI,Celery backend;
    class PG db;
    class Redis redis;
    class Gemini external;
```


---

## 2. Proper Graphical Flow Chart: User Journey

This flowchart illustrates the overarching graphical flow a user takes through the CereForge application from landing to elite mastery.

```mermaid
flowchart TD
    %% Node Definitions
    Start([Landing Page])
    Register{Create Account}
    SkillSelect[Select Initial Skill Level]
    Dashboard[Dashboard Hub]
    
    subgraph Core Loop [Core Gamification Loop]
        Tasks[Task Explorer]
        TaskDetail{Take Challenge}
        Code[Write Solution in Colab]
        Submit[Submit GitHub Repo]
        Grade{AI Grading & AI Moderation}
        Win[Earn XP & Badges]
        Fail[Hint / Try Again]
    end
    
    subgraph Community [Social & Support]
        Mentor[Ask AI Mentor]
        Forum[Community Forum]
        Post[Ask Question]
        Answer[Provide Answer]
    end
    
    subgraph Competition [Growth]
        Leaderboard[View Leaderboard]
        Rank[Rank Up Tiers]
        Paths[Unlock Learning Paths]
    end

    %% Journey Flow
    Start --> Register
    Register --> SkillSelect
    SkillSelect --> Dashboard
    
    Dashboard --> Tasks
    Dashboard --> Leaderboard
    Dashboard --> Paths
    
    Tasks --> TaskDetail
    TaskDetail -->|Need Help?| Mentor
    TaskDetail --> Code
    Code --> Submit
    Submit --> Grade
    
    Grade -->|Failed Filter| Fail
    Fail --> TaskDetail
    
    Grade -->|Success!| Win
    Win --> Dashboard
    
    %% Community Tie-ins
    Fail -->|Ask Humans| Forum
    Forum --> Post
    Win -->|Help Others| Answer
    Answer --> Win
    
    %% Progression
    Win --> Rank
    Rank --> Leaderboard
    
    %% Styling
    classDef page fill:#f3f4f6,stroke:#4b5563,stroke-width:2px
    classDef action fill:#bae6fd,stroke:#0284c7,stroke-width:2px
    classDef decision fill:#fed7aa,stroke:#ea580c,stroke-width:2px
    
    class Start,Dashboard,Tasks,Forum,Leaderboard,Paths page
    class Register,SkillSelect,Code,Submit,Post,Answer,Mentor action
    class TaskDetail,Grade decision
```


---

## 2. Authentication & JWT Flow

How a user registers, logs in, and secures subsequent API requests across the platform.

```mermaid
sequenceDiagram
    participant U as User (React Client)
    participant API as FastAPI Backend
    participant DB as PostgreSQL Database
    
    %% Registration
    U->>API: POST /api/v1/auth/register (email, pass, skill_level)
    API->>API: Hash Password (Bcrypt)
    API->>DB: INSERT INTO users
    DB-->>API: Return User ID
    API-->>U: 201 Created (User Data + Tokens)
    
    %% Login
    U->>API: POST /api/v1/auth/login (email, pass)
    API->>DB: SELECT * FROM users WHERE email
    DB-->>API: User Record + Hashed Password
    API->>API: Verify Password
    API->>API: Generate Access & Refresh JWT Tokens
    API-->>U: 200 OK (access_token)
    
    %% Subsequent Request
    U->>API: GET /api/v1/dashboard (Header: Bearer {token})
    API->>API: Verify JWT Signature
    alt Invalid Token
        API-->>U: 401 Unauthorized
    else Valid Token
        API->>DB: Fetch Dashboard Data
        DB-->>API: User Stats & Badges
        API-->>U: 200 OK (Dashboard JSON)
    end
```


---

## 3. Challenge Task Submission & Grading Flow

The core gamification loop. Users write a solution in a notebook, submit the URL, and the system simulates grading, checks for AI moderation, and awards XP.

```mermaid
sequenceDiagram
    participant U as User (React Client)
    participant API as FastAPI
    participant AI as Gemini 2.5 API
    participant DB as PostgreSQL
    participant Badge as Badge Engine
    
    U->>API: POST /tasks/{id}/submit (github_url)
    
    %% Validation & Security
    API->>API: Validate URL Format
    API->>DB: Check if already submitted
    
    %% Simulated Delay for UX
    API->>API: asyncio.sleep(2.0) (Grading Simulation)
    
    %% AI Moderation Filter
    API->>AI: POST Analyze Solution for Bot Signatures
    AI-->>API: Return (is_ai_flagged, score, reason)
    
    %% Record Submission
    API->>DB: INSERT INTO task_submissions (including AI flags)
    
    %% Gamification Logic
    API->>DB: UPDATE users SET xp = xp + task_xp
    API->>Badge: evaluate_badges(user_id)
    Badge->>DB: Check rules (First Task? 1000 XP?)
    
    alt Earned New Badge
        Badge->>DB: INSERT INTO user_badges
        Badge-->>API: New Badges List
    end
    
    %% Response
    API-->>U: 200 OK (Success, XP Earned, Badges Awarded)
    U->>U: Trigger Confetti Animation!
```


---

## 4. Real-time AI Mentor Streaming Flow

When a user gets stuck, they can ask the AI Mentor for guidance. The platform uses Server-Sent Events (SSE) to stream the LLM response back to the React UI in real-time.

```mermaid
sequenceDiagram
    participant User as User (React Client)
    participant API as FastAPI Backend
    participant LLM as Google Gemini API
    
    User->>API: POST /ai-mentor/guidance (task_slug, user_message)
    
    Note over API: Load System Prompts & Task Context
    API->>API: Construct specialized engineering prompt
    
    API->>LLM: Stream request (generate_content_stream)
    
    loop Every Chunk Generated
        LLM-->>API: returns Token Chunk ("Use a ")
        API-->>User: Server-Sent Event (yield chunk)
        User->>User: Update UI State (Append Token)
        
        LLM-->>API: returns Token Chunk ("Retrieval ")
        API-->>User: Server-Sent Event (yield chunk)
        User->>User: Update UI State (Append Token)
    end
    
    LLM-->>API: [DONE]
    API-->>User: Connection Closed
```

---

## 5. Community Q&A & AI Summarization

The forum functionality where users can ask questions and request an AI to summarize a long thread.

```mermaid
sequenceDiagram
    participant U as User
    participant React as React UI
    participant API as FastAPI
    participant DB as PostgreSQL
    participant LLM as Gemini API
    
    U->>React: Clicks "Summarize Thread"
    React->>API: GET /api/v1/posts/{id}/summary
    
    API->>DB: Fetch Post and all nested Comments
    DB-->>API: JSON Data (Post body, Comment 1, Comment 2...)
    
    Note over API: Format thread chronologically into a single text block
    
    API->>LLM: Prompt: "Summarize this engineering discussion..."
    LLM-->>API: Return markdown summary
    
    API-->>React: 200 OK (summary markdown)
    React-->>U: Display AI Summary Modal
```
