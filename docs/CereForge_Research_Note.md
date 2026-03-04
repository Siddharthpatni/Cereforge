# CereForge — Short Research Note

**Siddharth Patni · siddharth.patni@student.tu-chemnitz.de**  
March 2026

---

## What I built and why

I built a small learning platform for AI/ML engineering called CereForge. The idea was straightforward: most online courses teach you to understand concepts, but they don't put you in situations where you have to make actual design decisions. I wanted to build something where the challenges ask "how would you structure this system and why?" rather than "complete this tutorial."

The platform has 24 tasks across four areas — LLM prompting, RAG pipelines, computer vision, and multi-agent systems. Users write their solution and reasoning, and the submission gets evaluated by a Gemini model using a multi-dimensional rubric. There's also a community Q&A forum, a leaderboard, and a few structured learning paths.

The codebase is at: [github.com/Siddharthpatni/Cereforge](https://github.com/Siddharthpatni/Cereforge)

---

## The actual problem I ran into

The evaluation part doesn't work well enough to trust.

When a student submits an open-ended answer — for example, explaining how they'd handle hallucination in a RAG pipeline — the LLM evaluator gives inconsistent scores. Run the same submission twice and you get different numbers. Change the phrasing of the rubric and the scores shift in ways that aren't predictable.

This is a known issue with LLM-as-judge evaluation. RAGAS (Shahul et al., 2023) and MT-Bench (Zheng et al., 2023) both show that judge consistency depends heavily on rubric design and temperature settings. But those papers deal with fixed evaluation tasks. My problem is slightly different: the submissions are architectural reasoning, not factual answers, so there's no ground truth to compare against.

The open question is: **can you design rubrics for open-ended engineering decisions that produce consistent LLM judgments?** And if you can measure consistency — say, using Cohen's kappa against human expert raters — what does it actually take to reach an acceptable threshold?

---

## What I'm hoping for

I'm not looking for a paid position — I understand there isn't budget for that outside official channels.

What I'm actually asking is whether you'd be willing to look at the evaluation setup I've built and tell me if the research question I've described is worth pursuing, and whether it overlaps with anything you or your group are working on. If it doesn't, that's a useful answer too.

I can come with a short specific demo and a concrete set of questions rather than a long document. 30 minutes would be enough.

---

## On the previous email

The email I sent had an unfilled placeholder in it, which I didn't catch before sending. That was careless. The document I attached was also too long and too vague about what I was actually asking for. I should have sent something like this note instead.

---

*CereForge source code: [github.com/Siddharthpatni/Cereforge](https://github.com/Siddharthpatni/Cereforge)*  
*Live API docs (local): [localhost:8000/docs](http://localhost:8000/docs)*
