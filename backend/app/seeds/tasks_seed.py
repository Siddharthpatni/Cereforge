"""Seed all 12 tasks with resources — idempotent (can run multiple times safely)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskResource

TASKS_DATA = [
    # ─── LLM ENGINEERING TRACK ───
    {
        "slug": "llm-prompt-chain",
        "track": "llm",
        "difficulty": "beginner",
        "title": "Your First Prompt Chain",
        "xp_reward": 50,
        "display_order": 1,
        "colab_url": "https://colab.research.google.com/drive/NF_llm_001_prompt_chain",
        "description": (
            "Design a 3-step sequential prompt chain that: (1) reads a product review and extracts the core "
            "sentiment and key complaints, (2) rewrites the extracted points in a professional tone for a business "
            "report, (3) generates a recommended action item for the product team. No coding required — write the "
            "3 prompts and explain what each one receives as input and sends as output."
        ),
        "beginner_guide": (
            'A "prompt" is just an instruction you type to an AI. A "chain" means you line up prompts so the output '
            "of one becomes the input of the next — like an assembly line where each worker does one specific job. "
            "This task teaches you the most fundamental skill in LLM engineering."
        ),
        "hint": (
            "Think about what information each step actually needs. Step 1 only needs the raw review. Step 2 only "
            "needs the extracted points from Step 1. Step 3 only needs the clean summary from Step 2. Keep each "
            "prompt focused on one job."
        ),
        "resources": [
            {"title": "Prompt Engineering Guide by DAIR.AI", "url": "https://www.promptingguide.ai/", "resource_type": "article", "display_order": 1},
            {"title": "What is an LLM? Visual Explainer by Jay Alammar", "url": "https://jalammar.github.io/illustrated-transformer/", "resource_type": "article", "display_order": 2},
        ],
    },
    {
        "slug": "llm-token-optimizer",
        "track": "llm",
        "difficulty": "beginner",
        "title": "Token Budget Mastery",
        "xp_reward": 50,
        "display_order": 2,
        "colab_url": "https://colab.research.google.com/drive/NF_llm_002_token_optimizer",
        "description": (
            "You are given 5 verbose, inefficient prompts. Rewrite each one to use at least 35% fewer tokens while "
            "maintaining identical instruction clarity. For each rewrite, explain which words you removed and why "
            "they were unnecessary. Then calculate the approximate cost savings at $0.001 per 1K input tokens if "
            "this prompt runs 100,000 times per day."
        ),
        "beginner_guide": (
            'AI models process text in "tokens" — roughly 1 token per word. Fewer tokens means faster responses and '
            "lower costs. Learning to write lean, precise prompts is a core professional skill. A single bloated "
            "prompt repeated millions of times costs real money."
        ),
        "hint": (
            'Remove phrases like "Please kindly", "As an AI language model", "I would like you to", "Can you please", '
            '"Thank you in advance". Be direct. Every word must earn its place.'
        ),
        "resources": [
            {"title": "OpenAI Tokenizer Tool", "url": "https://platform.openai.com/tokenizer", "resource_type": "article", "display_order": 1},
            {"title": "Token Efficiency in Production by Simon Willison", "url": "https://simonwillison.net/", "resource_type": "article", "display_order": 2},
        ],
    },
    {
        "slug": "llm-finetuning-blueprint",
        "track": "llm",
        "difficulty": "intermediate",
        "title": "Fine-Tuning Blueprint",
        "xp_reward": 150,
        "display_order": 3,
        "colab_url": "https://colab.research.google.com/drive/NF_llm_003_finetuning_blueprint",
        "description": (
            "A SaaS company has 50,000 historical customer support chat logs and wants to fine-tune an LLM to handle "
            "support tickets automatically. Design the complete fine-tuning strategy: dataset format (provide 3 example "
            "JSONL records), train/val/test split ratios with justification, choice of base model (justify your "
            "selection among GPT-3.5, Llama-3, Mistral-7B), key hyperparameters (learning rate, epochs, batch size), "
            "evaluation metrics, and a cost estimate for the training run."
        ),
        "beginner_guide": (
            "Fine-tuning means taking a powerful pre-trained AI and teaching it new specialized behavior using your "
            "own data. Think of hiring an experienced chef and training them specifically on your restaurant's menu "
            "and style — they keep all their cooking knowledge but now specialize in your cuisine."
        ),
        "hint": (
            'JSONL format with "messages" array (role: system/user/assistant). 80/10/10 split. For cost estimation: '
            "Mistral-7B fine-tuning on Together.ai is roughly $0.0008 per 1K tokens. Evaluate with perplexity "
            "(automated) + human eval (sample 100 responses)."
        ),
        "resources": [
            {"title": "HuggingFace Fine-Tuning Tutorial", "url": "https://huggingface.co/docs/transformers/training", "resource_type": "article", "display_order": 1},
            {"title": "Fine-tuning vs RAG comparison by Anyscale", "url": "https://www.anyscale.com/blog", "resource_type": "article", "display_order": 2},
        ],
    },
    # ─── RAG PIPELINES TRACK ───
    {
        "slug": "rag-intro-flow",
        "track": "rag",
        "difficulty": "beginner",
        "title": "Design Your First RAG System",
        "xp_reward": 50,
        "display_order": 1,
        "colab_url": "https://colab.research.google.com/drive/NF_rag_001_intro_flow",
        "description": (
            "A law firm wants a chatbot that can answer questions about their 500-page policy manual. Design the RAG "
            "pipeline in plain English and ASCII diagram form. Your design must include: (1) document ingestion step, "
            "(2) chunking strategy with reasoning, (3) embedding model selection with justification, (4) vector "
            "database choice, (5) retrieval step, (6) generation step. Label every arrow in your diagram."
        ),
        "beginner_guide": (
            "RAG stands for Retrieval-Augmented Generation. Instead of hoping the AI memorized your document, you "
            "give it a library card. The AI can search your library (retrieval), find the relevant pages, and then "
            "answer using exactly those pages (augmented generation). This makes AI answers accurate, sourced, and up-to-date."
        ),
        "hint": (
            "Your diagram should flow left to right: PDF → Loader → Chunks → Embeddings → Vector DB [offline pipeline]. "
            "Then: User Question → Query Embedding → Similarity Search → Top K Chunks → LLM + Context → Answer [online pipeline]."
        ),
        "resources": [
            {"title": "RAG Explained by Pinecone", "url": "https://www.pinecone.io/learn/retrieval-augmented-generation/", "resource_type": "article", "display_order": 1},
            {"title": "LangChain RAG Tutorial", "url": "https://python.langchain.com/docs/tutorials/rag/", "resource_type": "docs", "display_order": 2},
        ],
    },
    {
        "slug": "rag-vector-architect",
        "track": "rag",
        "difficulty": "intermediate",
        "title": "Vector Store Architecture",
        "xp_reward": 150,
        "display_order": 2,
        "colab_url": "https://colab.research.google.com/drive/NF_rag_002_vector_architect",
        "description": (
            "Design a production RAG system for a medical knowledge base (10,000 research papers, average 8,000 words "
            "each). Specify: chunk size and overlap strategy with reasoning, embedding model choice (compare "
            "text-embedding-3-small vs text-embedding-ada-002 vs BGE-M3), vector database selection (compare Pinecone "
            "vs Chroma vs Weaviate vs pgvector), metadata filtering strategy, and a hybrid search design."
        ),
        "beginner_guide": (
            'A vector database stores "fingerprints" of text — mathematical representations that capture meaning '
            "rather than exact words. When you search, it finds fingerprints most similar to your question's "
            'fingerprint. This is how "AI search" understands context rather than just keywords.'
        ),
        "hint": (
            "Medical papers need semantic chunking by section, not fixed-size chunks. Abstract gets its own chunk. "
            "For medical accuracy, consider smaller chunks (256-512 tokens) with more overlap (20%). Weaviate handles "
            "hybrid search natively. pgvector is cheapest if you already run PostgreSQL."
        ),
        "resources": [
            {"title": "Chunking Strategies by Greg Kamradt", "url": "https://www.youtube.com/watch?v=8OJC21T2SL4", "resource_type": "article", "display_order": 1},
            {"title": "Weaviate vs Pinecone vs Chroma comparison", "url": "https://weaviate.io/blog", "resource_type": "article", "display_order": 2},
        ],
    },
    {
        "slug": "rag-hallucination-guard",
        "track": "rag",
        "difficulty": "expert",
        "title": "Hallucination Detection System",
        "xp_reward": 300,
        "display_order": 3,
        "colab_url": "https://colab.research.google.com/drive/NF_rag_003_hallucination_guard",
        "description": (
            "Design a 3-layer hallucination prevention and detection system for a medical RAG application. "
            "Layer 1 (Prevention): retrieval confidence gating. Layer 2 (Detection): answer-source grounding check "
            "using NLI. Layer 3 (Escalation): human escalation trigger. Include a decision flowchart and explain "
            "how you would evaluate the system's performance."
        ),
        "beginner_guide": (
            'AI can confidently state wrong facts — this is called "hallucination". In medical applications, '
            "hallucinations can literally kill people. This task is about building safety nets: before answering, "
            "check if we found relevant sources (Layer 1); after answering, verify the answer is actually supported "
            "by those sources (Layer 2); if uncertain, escalate to a human (Layer 3)."
        ),
        "hint": (
            "Layer 1: cosine similarity threshold (e.g., 0.75 minimum). Layer 2: use cross-encoder models "
            "(ms-marco-MiniLM-L-6-v2) to score entailment. RAGAS framework for automated evaluation. Layer 3: trigger "
            'escalation on keywords ("diagnosis", "dosage", "treatment") + low confidence.'
        ),
        "resources": [
            {"title": "RAGAS Evaluation Framework on GitHub", "url": "https://github.com/explodinggradients/ragas", "resource_type": "docs", "display_order": 1},
            {"title": "NLI for Fact Checking by HuggingFace", "url": "https://huggingface.co/tasks/text-classification", "resource_type": "article", "display_order": 2},
        ],
    },
    # ─── COMPUTER VISION TRACK ───
    {
        "slug": "cv-real-world-survey",
        "track": "vision",
        "difficulty": "beginner",
        "title": "Computer Vision in the Real World",
        "xp_reward": 50,
        "display_order": 1,
        "colab_url": "https://colab.research.google.com/drive/NF_cv_001_real_world_survey",
        "description": (
            "Create a structured survey of Computer Vision applications. For each of 10 distinct industries "
            "(healthcare, automotive, retail, agriculture, manufacturing, security, sports, media, construction, "
            "logistics), identify: (1) the specific CV problem, (2) the CV technique used, (3) one real company "
            "solving it today, (4) the measurable business impact. Then write a paragraph on untapped potential."
        ),
        "beginner_guide": (
            "Computer Vision teaches machines to interpret images and video — like giving a computer eyes that can "
            "understand what they see. Your smartphone using Face ID, a Tesla detecting stop signs, a doctor's AI "
            "spotting cancer in an X-ray — all Computer Vision."
        ),
        "hint": (
            "Don't just list generic uses. Be specific. For healthcare: 'Diabetic retinopathy screening using CNN "
            "classification on retinal fundus photographs — Google's DeepMind achieved 94% accuracy, matching "
            "specialist ophthalmologists.' That's the level of depth required."
        ),
        "resources": [
            {"title": "Stanford CS231n Course Notes", "url": "https://cs231n.github.io/", "resource_type": "article", "display_order": 1},
            {"title": "State of Computer Vision 2024 by Roboflow", "url": "https://blog.roboflow.com/", "resource_type": "article", "display_order": 2},
        ],
    },
    {
        "slug": "cv-yolo-pipeline",
        "track": "vision",
        "difficulty": "intermediate",
        "title": "YOLO Object Detection System Design",
        "xp_reward": 150,
        "display_order": 2,
        "colab_url": "https://colab.research.google.com/drive/NF_cv_002_yolo_pipeline",
        "description": (
            "Design a production object detection system for a warehouse where robots need to identify and locate "
            "47 product SKUs on shelves in real-time (minimum 15 FPS at 1080p). Cover: YOLOv8 variant selection, "
            "dataset requirements, preprocessing, confidence/NMS thresholds, deployment target comparison, "
            "post-processing, and monitoring for model drift."
        ),
        "beginner_guide": (
            "YOLO (You Only Look Once) is a real-time object detection algorithm. Imagine teaching a computer to look "
            "at a warehouse photo and instantly circle every product, label what it is, and report its location — in "
            'under 70 milliseconds. "Production design" means making it work reliably at scale.'
        ),
        "hint": (
            "YOLOv8s (small) hits 45 FPS on a Jetson Orin NX at 640px input — good balance. You need minimum 300 "
            "images per class for 47 SKUs = ~14,100 training images. Use confidence 0.45, NMS IoU 0.5."
        ),
        "resources": [
            {"title": "Ultralytics YOLOv8 Documentation", "url": "https://docs.ultralytics.com/", "resource_type": "docs", "display_order": 1},
            {"title": "Edge Deployment Guide by NVIDIA", "url": "https://developer.nvidia.com/embedded/jetson-orin", "resource_type": "article", "display_order": 2},
        ],
    },
    {
        "slug": "cv-vision-language",
        "track": "vision",
        "difficulty": "expert",
        "title": "Vision-Language Multimodal System",
        "xp_reward": 300,
        "display_order": 3,
        "colab_url": "https://colab.research.google.com/drive/NF_cv_003_vision_language",
        "description": (
            "Architect a multimodal product search system for an e-commerce platform. Users upload a photo and the "
            "system returns a text description and 5 most visually similar products from a 2M catalog. Requirements: "
            "P95 latency <800ms, 500 QPS peak. Cover: vision encoder selection, embedding pipeline, vector search "
            "strategy, caching, API contract, and failure mode analysis."
        ),
        "beginner_guide": (
            '"Vision-language" means the system understands both images and text in the same mathematical space. '
            "CLIP by OpenAI learned to match images with text descriptions — so 'a red leather handbag' and a photo "
            "of a red handbag end up near each other mathematically. This makes image search work like text search."
        ),
        "hint": (
            "CLIP ViT-L/14 gives better accuracy but 4x slower than ViT-B/32. For 2M products, Faiss with IVF-PQ "
            "index gets sub-100ms search. Cache the top 1000 most searched embeddings in Redis. Pre-compute all product "
            "embeddings offline. LLaVA description generation will be the latency bottleneck."
        ),
        "resources": [
            {"title": "OpenAI CLIP Paper on arXiv", "url": "https://arxiv.org/abs/2103.00020", "resource_type": "article", "display_order": 1},
            {"title": "Faiss: Efficient Similarity Search by Meta", "url": "https://github.com/facebookresearch/faiss", "resource_type": "article", "display_order": 2},
        ],
    },
    # ─── AUTONOMOUS AGENTS TRACK ───
    {
        "slug": "agent-fundamentals",
        "track": "agents",
        "difficulty": "beginner",
        "title": "Understand AI Agents",
        "xp_reward": 50,
        "display_order": 1,
        "colab_url": "https://colab.research.google.com/drive/NF_agent_001_fundamentals",
        "description": (
            "Demonstrate your understanding of AI agents through three deliverables: (1) Explain the difference between "
            "a chatbot and an AI agent with 3 concrete examples. (2) Draw the Observe-Think-Act loop in ASCII with a "
            "specific example. (3) Identify 3 failure modes of autonomous agents and explain handling."
        ),
        "beginner_guide": (
            "A chatbot answers questions. An agent DOES things in the world — it can browse the web, write and run "
            "code, send emails, fill forms, book flights. The key difference is the ability to TAKE ACTIONS with real "
            "consequences. With that power comes new risks."
        ),
        "hint": (
            "The 3 key failure modes are: (1) Tool failure — the API is down, (2) Planning loop — retrying the same "
            "failed approach, (3) Scope creep — unintended actions. Detection: timeouts, max-retry limits, human "
            "checkpoints before irreversible actions."
        ),
        "resources": [
            {"title": "ReAct Paper: Synergizing Reasoning and Acting", "url": "https://arxiv.org/abs/2210.03629", "resource_type": "article", "display_order": 1},
            {"title": "LangChain Agents Introduction", "url": "https://python.langchain.com/docs/modules/agents/", "resource_type": "docs", "display_order": 2},
        ],
    },
    {
        "slug": "agent-langchain-research",
        "track": "agents",
        "difficulty": "intermediate",
        "title": "LangChain Research Agent Design",
        "xp_reward": 150,
        "display_order": 2,
        "colab_url": "https://colab.research.google.com/drive/NF_agent_002_langchain_research",
        "description": (
            "Design a research agent that autonomously researches a topic and produces a structured report. Cover: "
            "complete tool list, memory architecture, system prompt template, output schema (Pydantic model), and a "
            "critique of what could go wrong."
        ),
        "beginner_guide": (
            'LangChain is like LEGO for AI agents — it gives you pre-built blocks (tools, memory, prompts, parsers) '
            'that you snap together. An agent has a "brain" (LLM), "hands" (tools), "memory" (history), and "goals".'
        ),
        "hint": (
            "Tools needed: TavilySearch (web), ArxivQueryRun, WebBaseLoader, PythonREPL. Memory: ConversationSummaryMemory. "
            "Stop condition: 5+ unique sources. Use structured output: {title, sections, sources, confidence}."
        ),
        "resources": [
            {"title": "LangChain LCEL Expression Language", "url": "https://python.langchain.com/docs/expression_language/", "resource_type": "docs", "display_order": 1},
            {"title": "Build a Research Agent Tutorial", "url": "https://python.langchain.com/docs/tutorials/agents/", "resource_type": "article", "display_order": 2},
        ],
    },
    {
        "slug": "agent-multi-agent-system",
        "track": "agents",
        "difficulty": "expert",
        "title": "Multi-Agent Software Development System",
        "xp_reward": 300,
        "display_order": 3,
        "colab_url": "https://colab.research.google.com/drive/NF_agent_003_multi_agent_system",
        "description": (
            "Architect a multi-agent system for autonomous software development. Cover: Supervisor, Coder, Tester, "
            "Reviewer agents with roles and tools, communication protocol, shared state schema, human-in-the-loop "
            "checkpoints, failure handling, and token budget strategy (under $0.50 per feature request)."
        ),
        "beginner_guide": (
            "Imagine a software team where every person is an AI: a PM who breaks down requests, a developer who "
            "writes code, a QA who tests it, a tech lead who reviews it. Each is a separate AI model with a specific "
            "role. They communicate by passing structured messages."
        ),
        "hint": (
            "Use LangGraph for stateful multi-agent orchestration. Supervisor uses Pydantic structured output. Human "
            "checkpoint before file writes. If Tester rejects 3x: escalate. Token budget: Coder uses GPT-4o-mini, "
            "Reviewer uses GPT-4o, Supervisor uses GPT-4o-mini."
        ),
        "resources": [
            {"title": "LangGraph Multi-Agent Tutorial", "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/", "resource_type": "docs", "display_order": 1},
            {"title": "Microsoft AutoGen Documentation", "url": "https://microsoft.github.io/autogen/", "resource_type": "docs", "display_order": 2},
        ],
    },
]


async def seed_tasks(db: AsyncSession):
    """Seed all 12 tasks with resources — idempotent."""
    for task_data in TASKS_DATA:
        resources_data = task_data.pop("resources", [])

        # Check if exists
        existing = await db.execute(select(Task).where(Task.slug == task_data["slug"]))
        task = existing.scalar_one_or_none()

        if task:
            # Update
            for key, value in task_data.items():
                setattr(task, key, value)
        else:
            task = Task(**task_data)
            db.add(task)

        await db.flush()

        # Upsert resources
        for res_data in resources_data:  # type: ignore
            existing_res = await db.execute(
                select(TaskResource).where(
                    TaskResource.task_id == task.id,
                    TaskResource.title == res_data["title"],
                )
            )
            res = existing_res.scalar_one_or_none()
            if res:
                for key, value in res_data.items():
                    setattr(res, key, value)
            else:
                resource = TaskResource(task_id=task.id, **res_data)
                db.add(resource)

    await db.commit()
    print(f"✅ Seeded {len(TASKS_DATA)} tasks with resources")
