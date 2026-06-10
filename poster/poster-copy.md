# Poster copy — ACS WA Tech Summit 2026 Intern Poster Showcase

Format reminder: A0 portrait (841 x 1189 mm), build in PowerPoint, readable from 3 m.
Replace every [BRACKET] placeholder. Keep text tight — judges penalise wordy posters.

---

## TITLE BLOCK (top, very large)

**[Internship title — e.g. "Building an AI-Powered Learning Assistant for University IT Students"]**

[Your Name]  ·  Sponsor: [Internship Sponsor / Host Organisation]  ·  Murdoch University

> Note: this is the *Intern* Poster Showcase, so the title must name your internship
> sponsor. If your internship work and this system differ, present this as the
> engineering project you delivered/explored during the internship and credit the
> sponsor + supervisor honestly.

---

## 1. CENTRAL MESSAGE (one bold sentence, near the top)

I designed and built an AI tutoring platform that helps IT students learn their
course content through Socratic dialogue grounded in real lecture material —
integrating cloud microservices, applied machine learning, and agentic LLMs into
one working, deployable system.

---

## 2. THE PROBLEM (short)

- Students need accurate, course-specific help outside class hours.
- Generic chatbots hallucinate and simply hand over answers instead of teaching.
- Goal: a trustworthy assistant that retrieves from the *actual* unit materials and
  guides students to understanding rather than spoon-feeding them.

---

## 3. MY ROLE (Situation)

Sole developer / full-stack + AI engineer. I owned the design, build, integration
and deployment of every component end-to-end:
frontend, secure backend, AI services, and the data pipeline behind them.

---

## 4. WHAT I BUILT  (place next to the architecture diagram — keep callouts to one line each)

- **Secure microservices backend** — Spring Boot + Spring Cloud: API Gateway,
  Eureka discovery, centralised Config Server, OAuth2 + JWT authentication, Postgres.
- **Agentic RAG chatbot** — LangGraph tool-calling agent that retrieves from real
  course material (Pinecone vector DB) and teaches Socratically; multi-LLM
  (Gemini / OpenAI / Ollama) with Tavily web search.
- **Topic classifier** — FastAPI + scikit-learn LinearSVC routes each question to the
  correct unit, with a confidence threshold that falls back to "OTHER".
- **Data pipeline** — `unit_extractor` pulls course content; a fine-tuned Phi-3 model
  generates synthetic training data for the classifier.
- **One-command deployment** — fully containerised: `docker compose up`.

> Use the architecture diagram (poster/architecture-diagram.svg) as the centre of
> the poster. Add a small screenshot of the chat UI answering a real unit question.

---

## 5. HOW IT WORKS (one short flow line under the diagram)

Question -> Gateway (JWT auth) -> Classifier picks the unit -> LangGraph agent
retrieves from Pinecone -> grounded, Socratic answer.

---

## 6. EVIDENCE & IMPACT (use plots/tables — fill in your real numbers)

**Topic classifier**
- Accuracy: [XX]%  ·  Macro-F1: [0.XX]  across [N] units/topics.
- Add a small **confusion matrix** image.
- (Optional) Before vs after adding synthetic data: F1 [0.XX] -> [0.XX].

**RAG quality (from LangSmith)**
- Answer relevance / groundedness: [XX]% on [N] sample questions.
- Retrieval hit-rate: [XX]%.
- Add one **LangSmith trace screenshot** showing the agent choosing the right
  retrieval tool.

**System scale**
- 8 backend microservices + 5 AI/data components, single-command deploy.

---

## 7. SKILLS DEVELOPED (work-readiness beyond coursework)

**Technical:** distributed systems design, API security (OAuth2/JWT), LLM/RAG
engineering, applied ML, containerisation & deployment.
**Professional:** system-level decision-making, integrating many moving parts,
designing for security & configuration from day one, self-directed delivery.

**Optional SFIA v9 self-assessment table** (skill — level of autonomy):
| SFIA skill | What I practised | Level |
|---|---|---|
| PROG (software development) | Built all services | [2/3] |
| DESN (systems design) | Microservice + AI architecture | [2/3] |
| SCTY (security) | OAuth2 / JWT auth | [2] |
| MLNG / DATS (machine learning / data science) | Classifier + fine-tuning | [2/3] |
| DEPL (deployment) | Docker Compose | [2] |

---

## 8. CRITICAL REFLECTION (STAR-L) — edit to your truth

- **Situation:** I set out to build an AI learning assistant for IT students, with no
  prior production microservices or LLM experience.
- **Task:** Deliver an end-to-end system — secure backend, AI chatbot, and the data
  pipeline behind it.
- **Action:** Built a Spring Cloud backend with OAuth2/JWT security, an agentic RAG
  chatbot (LangGraph + Pinecone), a scikit-learn topic classifier, and fine-tuned an
  LLM to generate training data — integrated behind one gateway and containerised.
- **Result:** A working platform giving accurate, course-grounded, Socratic tutoring
  [add a metric, e.g. classifier F1 / RAG relevance].
- **Lesson learned:** Real engineering is mostly integration and trade-offs, not
  isolated coding; designing for security, configuration and deployment early matters
  as much as features.

---

## 9. ACKNOWLEDGEMENTS (the guidelines explicitly require this)

Thanks to [Supervisor name(s)] and [Sponsor / Host Organisation] for their guidance,
and to Murdoch University.

---

## Design tips
- 3-column portrait layout; titles huge; body ~28–36 pt min.
- Restrained palette (the diagram uses blue = backend, amber = AI, purple = data).
- Let the diagram + 2 plots do the talking; cut text ruthlessly.
- Print well in advance — don't rely on same-day printing.
