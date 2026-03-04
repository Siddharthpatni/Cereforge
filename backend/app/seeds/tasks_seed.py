from __future__ import annotations

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
            {
                "title": "Prompt Engineering Guide by DAIR.AI",
                "url": "https://www.promptingguide.ai/",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "What is an LLM? Visual Explainer by Jay Alammar",
                "url": "https://jalammar.github.io/illustrated-transformer/",
                "resource_type": "article",
                "display_order": 2,
            },
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
            {
                "title": "OpenAI Tokenizer Tool",
                "url": "https://platform.openai.com/tokenizer",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "Token Efficiency in Production by Simon Willison",
                "url": "https://simonwillison.net/",
                "resource_type": "article",
                "display_order": 2,
            },
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
            {
                "title": "HuggingFace Fine-Tuning Tutorial",
                "url": "https://huggingface.co/docs/transformers/training",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "Fine-tuning vs RAG comparison by Anyscale",
                "url": "https://www.anyscale.com/blog",
                "resource_type": "article",
                "display_order": 2,
            },
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
            {
                "title": "RAG Explained by Pinecone",
                "url": "https://www.pinecone.io/learn/retrieval-augmented-generation/",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "LangChain RAG Tutorial",
                "url": "https://python.langchain.com/docs/tutorials/rag/",
                "resource_type": "docs",
                "display_order": 2,
            },
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
            {
                "title": "Chunking Strategies by Greg Kamradt",
                "url": "https://www.youtube.com/watch?v=8OJC21T2SL4",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "Weaviate vs Pinecone vs Chroma comparison",
                "url": "https://weaviate.io/blog",
                "resource_type": "article",
                "display_order": 2,
            },
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
            {
                "title": "RAGAS Evaluation Framework on GitHub",
                "url": "https://github.com/explodinggradients/ragas",
                "resource_type": "docs",
                "display_order": 1,
            },
            {
                "title": "NLI for Fact Checking by HuggingFace",
                "url": "https://huggingface.co/tasks/text-classification",
                "resource_type": "article",
                "display_order": 2,
            },
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
            {
                "title": "Stanford CS231n Course Notes",
                "url": "https://cs231n.github.io/",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "State of Computer Vision 2024 by Roboflow",
                "url": "https://blog.roboflow.com/",
                "resource_type": "article",
                "display_order": 2,
            },
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
            {
                "title": "Ultralytics YOLOv8 Documentation",
                "url": "https://docs.ultralytics.com/",
                "resource_type": "docs",
                "display_order": 1,
            },
            {
                "title": "Edge Deployment Guide by NVIDIA",
                "url": "https://developer.nvidia.com/embedded/jetson-orin",
                "resource_type": "article",
                "display_order": 2,
            },
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
            {
                "title": "OpenAI CLIP Paper on arXiv",
                "url": "https://arxiv.org/abs/2103.00020",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "Faiss: Efficient Similarity Search by Meta",
                "url": "https://github.com/facebookresearch/faiss",
                "resource_type": "article",
                "display_order": 2,
            },
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
            {
                "title": "ReAct Paper: Synergizing Reasoning and Acting",
                "url": "https://arxiv.org/abs/2210.03629",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "LangChain Agents Introduction",
                "url": "https://python.langchain.com/docs/modules/agents/",
                "resource_type": "docs",
                "display_order": 2,
            },
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
            "LangChain is like LEGO for AI agents — it gives you pre-built blocks (tools, memory, prompts, parsers) "
            'that you snap together. An agent has a "brain" (LLM), "hands" (tools), "memory" (history), and "goals".'
        ),
        "hint": (
            "Tools needed: TavilySearch (web), ArxivQueryRun, WebBaseLoader, PythonREPL. Memory: ConversationSummaryMemory. "
            "Stop condition: 5+ unique sources. Use structured output: {title, sections, sources, confidence}."
        ),
        "resources": [
            {
                "title": "LangChain LCEL Expression Language",
                "url": "https://python.langchain.com/docs/expression_language/",
                "resource_type": "docs",
                "display_order": 1,
            },
            {
                "title": "Build a Research Agent Tutorial",
                "url": "https://python.langchain.com/docs/tutorials/agents/",
                "resource_type": "article",
                "display_order": 2,
            },
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
            {
                "title": "LangGraph Multi-Agent Tutorial",
                "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/",
                "resource_type": "docs",
                "display_order": 1,
            },
            {
                "title": "Microsoft AutoGen Documentation",
                "url": "https://microsoft.github.io/autogen/",
                "resource_type": "docs",
                "display_order": 2,
            },
        ],
    },
    # ─── ADDITIONAL LLM TASKS ───
    {
        "slug": "llm-structured-output",
        "track": "llm",
        "difficulty": "intermediate",
        "title": "Structured JSON from Any LLM",
        "xp_reward": 100,
        "display_order": 4,
        "colab_url": "https://colab.research.google.com/drive/NF_llm_004_structured_output",
        "description": (
            "Production LLM systems almost never consume raw text — they need clean JSON. "
            "In this task you will: (1) define a Pydantic schema for a job posting extraction model "
            "(company, role, salary_range, required_skills, remote_friendly), (2) use an instructor-patched "
            "OpenAI client to extract structured data from 5 raw job descriptions, (3) handle validation errors "
            "gracefully with retry logic, and (4) measure extraction accuracy. Target: >90% field accuracy "
            "on the provided test set."
        ),
        "beginner_guide": (
            "Structured output means getting the LLM to always respond in a format your code can parse, "
            "like JSON. The library `instructor` wraps OpenAI and forces the model to match your Pydantic schema. "
            "Think of it as giving the model a form to fill in, not a blank page to write on."
        ),
        "hint": (
            "Use `instructor.patch(client)` then pass `response_model=YourSchema` to `chat.completions.create`. "
            "For retry logic, `instructor` has a built-in `max_retries` parameter."
        ),
        "resources": [
            {
                "title": "Instructor library docs",
                "url": "https://python.useinstructor.com/",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "OpenAI Function Calling Guide",
                "url": "https://platform.openai.com/docs/guides/function-calling",
                "resource_type": "article",
                "display_order": 2,
            },
        ],
    },
    {
        "slug": "llm-fine-tuning-intro",
        "track": "llm",
        "difficulty": "expert",
        "title": "Fine-Tune a Small LLM on Custom Data",
        "xp_reward": 200,
        "display_order": 5,
        "colab_url": "https://colab.research.google.com/drive/NF_llm_005_fine_tuning",
        "description": (
            "When prompting isn't enough, you fine-tune. In this task you will: "
            "(1) prepare a dataset of 200 customer service Q&A pairs in JSONL chat format, "
            "(2) fine-tune `Qwen2.5-0.5B-Instruct` using `trl` + `peft` with LoRA (r=8, alpha=16) "
            "on a free T4 Colab GPU, (3) evaluate using ROUGE-L and a held-out test set, "
            "(4) compare base model vs fine-tuned model responses on 10 edge cases. "
            "Submit your training metrics and a 3-sentence reflection on what improved."
        ),
        "beginner_guide": (
            "Fine-tuning means taking a pre-trained model and teaching it your specific style or vocabulary "
            "by training it on your own examples. LoRA is a smart technique that only trains a tiny fraction "
            "of the model weights, making it affordable even on a free GPU. Think of it as giving the AI "
            "a short apprenticeship in your domain."
        ),
        "hint": (
            "Use `datasets.Dataset.from_list()` for your JSONL data. For LoRA config, start with "
            "`target_modules=['q_proj', 'v_proj']`. The `SFTTrainer` from `trl` handles the training loop."
        ),
        "resources": [
            {
                "title": "HuggingFace PEFT Documentation",
                "url": "https://huggingface.co/docs/peft",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "TRL SFTTrainer Guide",
                "url": "https://huggingface.co/docs/trl/sft_trainer",
                "resource_type": "article",
                "display_order": 2,
            },
        ],
    },
    {
        "slug": "llm-eval-framework",
        "track": "llm",
        "difficulty": "intermediate",
        "title": "Build an LLM Evaluation Framework",
        "xp_reward": 150,
        "display_order": 6,
        "colab_url": "https://colab.research.google.com/drive/NF_llm_006_eval_framework",
        "description": (
            "How do you know if your LLM is actually good? In this task you will build a mini evaluation "
            "framework that tests a chatbot on 3 dimensions: (1) factual accuracy (using a QA dataset with "
            "known answers), (2) instruction following (does it maintain format/length constraints?), "
            "(3) safety (does it refuse harmful requests?). Run your evaluation against both GPT-4o-mini "
            "and a Gemini Flash model. Produce a comparison report table showing pass rates per category."
        ),
        "beginner_guide": (
            "Evaluation is the most underrated part of LLM engineering. This task teaches you how to "
            "systematically test if your AI is actually doing what you want across accuracy, logic, "
            "and safety. You'll build a 'judge' model that evaluates your 'student' model."
        ),
        "hint": "Use LangSmith or a simple dict-based scorer. For safety, curate 10 red-team prompts.",
        "resources": [
            {
                "title": "OpenAI Evals Framework",
                "url": "https://github.com/openai/evals",
                "resource_type": "article",
                "display_order": 1,
            },
        ],
    },
    # ─── ADDITIONAL RAG TASKS ───
    {
        "slug": "rag-reranker",
        "track": "rag",
        "difficulty": "intermediate",
        "title": "Add a Neural Reranker to Your RAG Pipeline",
        "xp_reward": 150,
        "display_order": 5,
        "colab_url": "https://colab.research.google.com/drive/NF_rag_005_reranker",
        "description": (
            "Basic embedding search ranks documents by cosine similarity, but a neural reranker reads "
            "both the query and each candidate together — like a human judging relevance. "
            "In this task: (1) build a baseline retrieval pipeline using ChromaDB on 200 Wikipedia chunks, "
            "(2) add `cross-encoder/ms-marco-MiniLM-L-12-v2` as a reranker on top of the top-20 retrieved chunks, "
            "(3) measure NDCG@5 with and without the reranker on 50 test queries, "
            "(4) analyze the 3 biggest improvements. Target: ≥ 8% NDCG@5 improvement."
        ),
        "beginner_guide": (
            "A reranker is like a second, smarter judge that looks at the top results from your first "
            "search and re-orders them to be even more relevant. It's slower than the first search, "
            "so we only use it on the top 20 candidates."
        ),
        "hint": "Use `sentence_transformers.CrossEncoder`. Sort by `.predict()` scores descending.",
        "resources": [
            {
                "title": "SentenceTransformers Cross-Encoder",
                "url": "https://www.sbert.net/docs/cross_encoder/pretrained_models.html",
                "resource_type": "article",
                "display_order": 1,
            },
        ],
    },
    {
        "slug": "rag-multimodal",
        "track": "rag",
        "difficulty": "expert",
        "title": "Multimodal RAG — Search Over Documents with Images",
        "xp_reward": 200,
        "display_order": 6,
        "colab_url": "https://colab.research.google.com/drive/NF_rag_006_multimodal",
        "description": (
            "Most RAG systems ignore images in PDFs. This task makes them first-class citizens. "
            "Using LlamaParse or PyMuPDF, extract text AND images from a 50-page technical PDF. "
            "Embed images using CLIP and text using text-embedding-3-small. Store both in Qdrant with "
            "payload metadata. Build a unified retriever that searches both modalities and fuses results. "
            "Demonstrate: a query about a chart in the PDF returns the correct image chunk."
        ),
        "beginner_guide": (
            "Standard RAG only sees text. Multimodal RAG sees everything — charts, photos, and diagrams. "
            "We use CLIP to turn images into math (vectors) just like we do with text, so you can search "
            "for 'a chart showing revenue growth' and actually find it."
        ),
        "hint": "Qdrant supports multiple vector fields per point. Use `vectors={'text': ..., 'image': ...}`.",
        "resources": [
            {
                "title": "Qdrant Multi-vector Tutorial",
                "url": "https://qdrant.tech/documentation/tutorials/multimodal/",
                "resource_type": "article",
                "display_order": 1,
            },
        ],
    },
    {
        "slug": "rag-streaming-pipeline",
        "track": "rag",
        "difficulty": "intermediate",
        "title": "Real-Time Streaming RAG Responses",
        "xp_reward": 125,
        "display_order": 7,
        "colab_url": "https://colab.research.google.com/drive/NF_rag_007_streaming",
        "description": (
            "Waiting 10 seconds for a full RAG response kills UX. Streaming changes everything. "
            "In this task: (1) build a FastAPI endpoint that retrieves context then streams an LLM response "
            "token-by-token using Server-Sent Events, (2) build a simple React frontend that displays "
            "the streaming text, (3) add a source citations sidebar that appears when retrieval completes, "
            "(4) measure time-to-first-token and compare to non-streaming. Target: TTFT < 300ms."
        ),
        "beginner_guide": (
            "Streaming makes AI feel fast by showing you words as they are generated, rather than making "
            "you wait for the whole paragraph. It's a key part of great AI user experience, especially "
            "for long RAG answers."
        ),
        "hint": "Use `StreamingResponse` in FastAPI with `async def generate()` yielding `f'data: {chunk}\\n\\n'`.",
        "resources": [
            {
                "title": "FastAPI Streaming Response Docs",
                "url": "https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse",
                "resource_type": "article",
                "display_order": 1,
            },
        ],
    },
    # ─── ADDITIONAL VISION TASKS ───
    {
        "slug": "cv-object-detection",
        "track": "vision",
        "difficulty": "intermediate",
        "title": "Real-Time Object Detection with YOLOv8",
        "xp_reward": 150,
        "display_order": 5,
        "colab_url": "https://colab.research.google.com/drive/NF_cv_005_yolo",
        "description": (
            "YOLO (You Only Look Once) is the industry standard for real-time object detection. "
            "In this task: (1) load YOLOv8n from Ultralytics and run inference on 20 provided street images, "
            "(2) fine-tune on a custom 500-image dataset of hard hats and safety vests from Roboflow, "
            "(3) evaluate with mAP@0.5 on a held-out test set, (4) export to ONNX and measure inference "
            "latency on CPU. Target: mAP@0.5 > 0.75 on the safety gear dataset."
        ),
        "beginner_guide": (
            "Object detection doesn't just see 'there is a person' — it draws a box exactly where they are. "
            "YOLOv8 is the fastest way to do this, making it possible to track moving objects in real-time "
            "video on a standard computer."
        ),
        "hint": "Use `model.train(data='safety.yaml', epochs=30, imgsz=640)`. Roboflow provides the YAML automatically.",
        "resources": [
            {
                "title": "Ultralytics YOLOv8 Docs",
                "url": "https://docs.ultralytics.com/",
                "resource_type": "article",
                "display_order": 1,
            },
            {
                "title": "Roboflow Universe Datasets",
                "url": "https://universe.roboflow.com/",
                "resource_type": "article",
                "display_order": 2,
            },
        ],
    },
    {
        "slug": "cv-image-classification-cnn",
        "track": "vision",
        "difficulty": "beginner",
        "title": "Train Your First Image Classifier",
        "xp_reward": 75,
        "display_order": 6,
        "colab_url": "https://colab.research.google.com/drive/NF_cv_006_classifier",
        "description": (
            "Before transformers, CNNs ruled computer vision. Understanding them makes everything else click. "
            "In this task: (1) use PyTorch to build a 4-layer CNN (Conv → ReLU → Pool, repeated twice + FC layers), "
            "(2) train on CIFAR-10 for 10 epochs, (3) visualize feature maps from the first conv layer using "
            "matplotlib, (4) apply data augmentation (random flip, color jitter) and show the accuracy improvement. "
            "Target: ≥ 75% test accuracy on CIFAR-10."
        ),
        "beginner_guide": (
            "A CNN is like a grid of filters that scan across an image looking for patterns. "
            "Early filters detect edges, later filters detect shapes, the final layer classifies. "
            "CIFAR-10 has 60,000 tiny 32x32 images across 10 classes — perfect for learning."
        ),
        "hint": "Use `torchvision.datasets.CIFAR10`. Start with `nn.Conv2d(3, 32, 3)` for the first layer.",
        "resources": [
            {
                "title": "PyTorch CNN Tutorial",
                "url": "https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html",
                "resource_type": "article",
                "display_order": 1,
            },
        ],
    },
    {
        "slug": "cv-segmentation",
        "track": "vision",
        "difficulty": "expert",
        "title": "Semantic Segmentation for Autonomous Driving",
        "xp_reward": 225,
        "display_order": 7,
        "colab_url": "https://colab.research.google.com/drive/NF_cv_007_segmentation",
        "description": (
            "While object detection draws boxes, segmentation labels every single pixel. "
            "In this task: (1) download 500 images from the Cityscapes dataset, "
            "(2) fine-tune a SegFormer-B0 model for road, car, pedestrian, and sky classes, "
            "(3) evaluate with mIoU (mean Intersection over Union), (4) generate a video overlay "
            "showing the segmentation mask on a 30-second dashcam clip. "
            "Target: mIoU >= 0.60 on the validation split."
        ),
        "beginner_guide": (
            "Segmentation is the 'surgical' version of computer vision. Instead of boxes, it colors "
            "every pixel based on what it is — road, car, sidewalk, or tree. This is how self-driving "
            "cars know exactly where the drivable road ends and the sidewalk begins."
        ),
        "hint": "Use `transformers.SegformerForSemanticSegmentation.from_pretrained('nvidia/segformer-b0')`. "
        "Use bilinear interpolation to upsample output logits to input image size.",
        "resources": [
            {
                "title": "HuggingFace SegFormer Guide",
                "url": "https://huggingface.co/docs/transformers/model_doc/segformer",
                "resource_type": "article",
                "display_order": 1,
            },
        ],
    },
    # ─── ADDITIONAL AGENTS TASKS ───
    {
        "slug": "agent-tool-builder",
        "track": "agents",
        "difficulty": "intermediate",
        "title": "Build and Register 5 Custom Agent Tools",
        "xp_reward": 150,
        "display_order": 5,
        "colab_url": "https://colab.research.google.com/drive/NF_ag_005_tool_builder",
        "description": (
            "The power of an AI agent is only as large as its toolbox. "
            "In this task, implement 5 custom tools using LangChain's `@tool` decorator: "
            "(1) `web_search` using DuckDuckGo API, (2) `code_executor` using a sandboxed Python REPL, "
            "(3) `file_reader` with PDF and CSV support, (4) `calculator` with safe eval, "
            "(5) `memory_store` backed by a JSON file. "
            "Create an agent with all 5 tools and demo it solving a multi-step research task."
        ),
        "beginner_guide": (
            "A 'tool' is a function the agent can call when it decides it needs help. "
            "You define what the function does; the agent decides WHEN to call it based on the task. "
            "This is how AI agents browse the web, run code, or read files."
        ),
        "hint": "Decorate with `@tool` and write a clear docstring — the agent reads the docstring to "
        "decide when to use the tool. Bad docstring = agent misuses the tool.",
        "resources": [
            {
                "title": "LangChain Custom Tools Guide",
                "url": "https://python.langchain.com/docs/how_to/custom_tools/",
                "resource_type": "article",
                "display_order": 1,
            },
        ],
    },
    {
        "slug": "agent-memory-system",
        "track": "agents",
        "difficulty": "intermediate",
        "title": "Long-Term Memory for AI Agents",
        "xp_reward": 175,
        "display_order": 6,
        "colab_url": "https://colab.research.google.com/drive/NF_ag_006_memory",
        "description": (
            "Stateless agents forget everything between sessions. Memory fixes that. "
            "Build a personal assistant agent with 3-tier memory: "
            "(1) working memory (current conversation in context window), "
            "(2) episodic memory (past conversations stored in a vector DB, retrieved by similarity), "
            "(3) semantic memory (distilled facts about the user stored as structured JSON). "
            "Demonstrate: start a conversation, end it, start a new one, and show the agent "
            "correctly recalls facts from the previous session without them being in context."
        ),
        "beginner_guide": (
            "Memory gives agents a 'life story'. Without it, they are like someone with amnesia — "
            "every conversation starts from zero. By storing past interactions in a database, the agent "
            "can remember your name, your preferences, and what you worked on yesterday."
        ),
        "hint": "Use Mem0 or build custom with ChromaDB. For semantic memory, ask the LLM to "
        "extract key facts and store them in a `user_facts.json` file after each session.",
        "resources": [
            {
                "title": "Mem0 Documentation",
                "url": "https://docs.mem0.ai/",
                "resource_type": "article",
                "display_order": 1,
            },
        ],
    },
    {
        "slug": "agent-orchestrator",
        "track": "agents",
        "difficulty": "expert",
        "title": "Build a Multi-Agent Orchestration System",
        "xp_reward": 250,
        "display_order": 7,
        "colab_url": "https://colab.research.google.com/drive/NF_ag_007_orchestrator",
        "description": (
            "Real-world AI pipelines use teams of specialized agents, not one monolith. "
            "Design a 4-agent research pipeline: (1) Planner agent that breaks a question into subtasks, "
            "(2) Researcher agent that calls web search tools, (3) Analyst agent that synthesizes findings, "
            "(4) Writer agent that produces the final report. Implement using LangGraph with a shared "
            "state graph. Add a human-in-the-loop approval checkpoint before the Writer publishes. "
            "Demo: produce a 1-page research report on 'impact of AI on software engineering jobs'."
        ),
        "beginner_guide": (
            "Orchestration is like being a conductor for an AI orchestra. Instead of one model doing "
            "everything, you have specialists (Researcher, Analyst, Writer) and a 'brain' that directs "
            "the flow of work between them to complete complex projects."
        ),
        "hint": "LangGraph's `StateGraph` is the key. Each node is an agent. Use `conditional_edges` "
        "for the human checkpoint. The state dict passes between all nodes.",
        "resources": [
            {
                "title": "LangGraph Multi-Agent Tutorial",
                "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-network/",
                "resource_type": "article",
                "display_order": 1,
            },
        ],
    },
]


async def seed_tasks(db: AsyncSession):
    """Seed all 24 tasks with resources — idempotent."""

    for task_data in TASKS_DATA:
        resources_data = task_data.pop("resources", [])

        # Check if exists
        existing = await db.execute(select(Task).where(Task.slug == task_data["slug"]))
        task = existing.scalar_one_or_none()

        sample_text = f"# Sample solution for {task_data['title']}\\n# Code goes here..."
        if "sample_solution" not in task_data:
            task_data["sample_solution"] = sample_text

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
