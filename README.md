# AI Study Buddy — Full Stack

A personalized AI tutor: React frontend + FastAPI backend + swappable LLM provider
(Gemini / OpenAI / Claude), with a dedicated prompt-engineering layer.

## Quick start (two terminals)

**Terminal 1 — backend**
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1          # Windows PowerShell  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env             # Mac/Linux: cp .env.example .env
# edit .env and paste your GEMINI_API_KEY
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend**
```bash
cd frontend
npm install
copy .env.example .env             # Mac/Linux: cp .env.example .env
npm run dev
```
Open **http://localhost:5173**. API docs live at http://localhost:8000/docs.

> If you're upgrading from an earlier zip: **delete `backend/study_buddy.db`** once.
> `quiz_attempts` gained a column (`results_json`) and SQLite won't alter existing tables.

## Features
Chat (context-aware) · Explain (beginner/intermediate/advanced/ELI5) · MCQ quizzes with scoring ·
Practice questions with AI feedback · Flashcards · Summarizer (map-reduce for long text) ·
Upload material and chat with it (RAG-lite) · Progress dashboard with weak-topic detection and
adaptive difficulty · Personalized study plans built from your weak topics.

---

# Backend build notes (phase-by-phase history)


A personalized AI tutor web app — built as a Generative AI + Prompt Engineering
portfolio project.

This repo is being built **phase by phase**. Current state = **Phase 4: study-material
summarization (map-reduce chunking) + open-ended practice-question generator with AI feedback**.

---

## What's new in Phase 4

- **Summarizer**: `POST /api/sessions/{id}/summarize` — paste raw study material
  (lecture notes, textbook excerpt, anything). Long text is automatically **chunked**
  and summarized piece-by-piece (map), then combined into one structured, validated
  summary (reduce) — short text skips the extra step entirely. Tested directly:
  short text triggered exactly 1 LLM call, long text (3 chunks) triggered exactly
  4 (3 map + 1 reduce).
- **`GET /api/sessions/{id}/summaries`** — all summaries generated in a session.
- **Practice question generator**: `POST /api/sessions/{id}/practice` — open-ended
  (not multiple-choice) questions, each with a self-check checklist
  (`ideal_answer_points`) instead of a single hidden answer.
- **AI feedback on written answers**: `POST /api/practice/{set_id}/feedback` —
  submit your own written answer to a practice question, get back which key
  points you covered, which you missed, and constructive feedback with a rough
  score estimate.
- **A third distinct prompt-chaining pattern**: map-reduce (`chains/summarize_chain.py`),
  alongside Phase 2's validate-retry and Phase 3's batch-then-selective-regenerate.

### Prompt-engineering techniques (cumulative, now complete except evaluation)

| Technique | Where |
|---|---|
| Role prompting | Reused across chat, notes, quiz, practice questions |
| Context-aware prompting | Chat assistant |
| Zero-shot prompting | Explainer, practice questions, summarizer's map step |
| Few-shot prompting | Quiz generator |
| Structured prompting | Every JSON-producing feature |
| Structured JSON output | Explainer, quiz, summarizer, practice questions — all schema-validated |
| Prompt chaining/refinement | Validate-retry (Phase 2), batch+selective-regen (Phase 3), map-reduce (this phase) |
| AI response validation | Every structured feature, via the shared validated_generation chain |

Only **prompt evaluation/comparison** remains — planned alongside the final
project report, comparing prompt variants side-by-side for the write-up.

---

## What exists from Phase 3 (unchanged)

- **Quiz generator**: `POST /api/sessions/{id}/quiz` — generates N multiple-choice
  questions on a topic at a difficulty level. The response is **sanitized**
  (no correct answers, no explanations) — the answer key only comes back
  after submission, so it's never sitting in the browser's network tab while
  the student is taking the quiz.
- **`GET /api/quizzes/{quiz_id}`** — re-fetch a quiz (e.g. on page reload).
- **`POST /api/quizzes/{quiz_id}/submit`** — submit answers, get back the
  score, full per-question breakdown (correct answer + explanation for every
  question), and a `weak_topics` list (the sub-topics you got wrong) — this
  is exactly the data future phases will use for weak-topic detection and
  adaptive difficulty.
- **Few-shot prompting** (`prompt_engine/few_shot_examples/quiz_examples.py` +
  `templates/quiz_gen.py`) — unlike the explainer (zero-shot), the quiz
  generator is shown 1-2 example questions from unrelated subjects before
  generating real ones, to steer format and difficulty calibration.
- **A more elaborate prompt chain** (`prompt_engine/chains/quiz_chain.py`):
  generate the full batch → validate the JSON shape → run a deeper
  per-question semantic check (duplicate options, blank text) → **selectively
  regenerate only the questions that fail**, leaving good questions
  untouched. Tested directly: a 3-question batch with one deliberately
  broken question (duplicate "Tokyo" option) came back with that one
  question fixed and the other two exactly as generated — 2 total LLM
  calls, not a full-batch retry.

### Prompt-engineering techniques so far (cumulative)

| Technique | Where |
|---|---|
| Role prompting | `prompt_builder.build_role_instruction` — reused by chat, notes, and quiz |
| Context-aware prompting | Chat assistant — injects prior turns |
| Zero-shot prompting | Topic explainer |
| Few-shot prompting | Quiz generator — example Q&A pairs steer format/difficulty |
| Structured prompting | Chat transcript format, explainer's and quiz's JSON specs |
| Structured JSON output | Explainer (`ExplanationOutput`), Quiz (`QuizOutput`/`QuizQuestionOutput`) |
| Prompt chaining/refinement | Generic validate→refine (Phase 2) + quiz's batch→validate→selective-regenerate (this phase) |
| AI response validation | Pydantic schema validation (all structured features) + quiz's deeper semantic checks |

Still to come: **prompt evaluation/comparison** (Phase 8, alongside a written
report comparing prompt variants) — everything else in the "make prompt
engineering a major part of the project" list is now demonstrated somewhere
in the codebase.

---

## What exists from Phase 2 (unchanged)

- **Topic explainer / study notes feature**: `POST /api/sessions/{id}/explain` —
  give it a topic and a difficulty level (`beginner` / `intermediate` / `advanced` /
  `eli5`), get back a structured explanation (summary, key points, an analogy,
  common mistakes, follow-up questions), saved as a `Note`.
- **`GET /api/sessions/{id}/notes`** — all notes generated in a session so far.
- **A reusable validate → refine chain** (`prompt_engine/chains/validated_generation.py`)
  — this is the important one. Every structured-JSON feature from here on (quiz,
  flashcards, study plans) is built on top of this one function:
  1. Ask the LLM for JSON matching a Pydantic schema
  2. Parse and validate it
  3. If it fails, send the model **its own broken output plus the exact
     validation error** and ask it to fix itself
  4. Only give up (with a clean `502`, never a crash) if it's still broken
     after the retry

  This was tested directly with a broken-then-fixed fake response and it
  correctly recovers on the retry — see `docs` note below.

- **Zero-shot + structured prompting** (`prompt_engine/templates/explain.py`) —
  no examples are given to the model, but the exact JSON shape it must return
  is spelled out field-by-field.
- **Small refactor**: session lookup/creation moved out of `chat_service.py`
  into a shared `services/session_service.py`, since notes now needs it too.
  `chat_service.py`'s public functions are unchanged, so nothing calling it broke.

### Prompt-engineering techniques so far (cumulative)

| Technique | Where |
|---|---|
| Role prompting | `prompt_builder.build_role_instruction` — reused by both chat and notes |
| Context-aware prompting | Chat assistant (Phase 1) — injects prior turns |
| Zero-shot prompting | Topic explainer (this phase) |
| Structured prompting | Both chat's transcript format and the explainer's JSON spec |
| Structured JSON output | Explainer, validated against `ExplanationOutput` |
| Prompt chaining/refinement | `validated_generation.py`'s generate → validate → refine loop |
| AI response validation | Same — Pydantic schema validation before anything is stored |

Few-shot prompting and prompt evaluation/comparison are still to come (Phase 3 —
the quiz generator is a natural fit for few-shot, since example Q&A pairs steer
format and difficulty far better than instructions alone).

---

## What exists from Phase 1 (unchanged)

- **SQLite database** (via SQLAlchemy) with two tables:
  - `sessions` — one row per study session (subject + difficulty + title)
  - `messages` — every chat turn, linked to a session (this is the conversation memory)
- **Dedicated prompt-engineering layer** (`app/prompt_engine/prompt_builder.py`)
  demonstrating **role prompting** (the tutor persona + difficulty-adapted teaching
  rules) and **context-aware prompting** (prior turns are injected into the prompt
  so the assistant can handle follow-ups like "give me an example of that")
- **Service layer** (`app/services/chat_service.py`) that orchestrates DB + prompt
  engine + LLM provider — routes never touch the database or build prompts directly
- Endpoints:
  - `POST /api/sessions` — start a new study session
  - `GET /api/sessions` — list all sessions (study history)
  - `GET /api/sessions/{id}/messages` — full transcript of one session
  - `POST /api/sessions/{id}/chat` — send a message, get the tutor's reply
- **Error handling that doesn't lose data**: if the LLM call fails (bad key,
  network issue, rate limit), the student's message is still saved — only the
  AI's reply is missing, so nothing is lost and they can just retry

Tested end-to-end: session creation auto-creates the tables, the prompt engine
correctly builds a role-prompted + context-aware prompt from real message history,
and a simulated LLM failure returns a clean `502` while still preserving the
user's message in the database.

---

## What exists right now (Phase 0)

- FastAPI backend skeleton
- A `BaseLLMProvider` interface + 3 concrete implementations (Gemini, OpenAI, Claude)
- A `provider_factory` that picks the active provider from `.env` — **swap providers
  by changing one config value, zero code changes**
- Two working endpoints:
  - `GET /api/health` — confirms the server is up and which provider is active
  - `POST /api/test-llm` — sends a prompt through the full chain (route → factory →
    provider → real LLM API) and returns the response

No database, no prompt-engineering layer, no study-buddy features yet — those come
in Phases 1–8 (see project architecture doc). This phase exists purely to prove the
foundation is solid before we build on it.

---

## Folder structure so far

```
ai-study-buddy/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, DB startup, router mounting
│   │   ├── config.py                # loads .env into a typed Settings object
│   │   ├── database.py              # SQLAlchemy engine, session factory, Base
│   │   ├── models/
│   │   │   ├── session.py           # StudySession ORM model
│   │   │   ├── message.py           # Message ORM model
│   │   │   ├── note.py              # Note ORM model (AI-generated study notes)
│   │   │   ├── quiz.py              # Quiz ORM model (full answer key stored here)
│   │   │   ├── quiz_attempt.py      # QuizAttempt ORM model (scored submissions)
│   │   │   ├── summary.py           # Summary ORM model
│   │   │   └── practice_set.py      # PracticeQuestionSet ORM model
│   │   ├── schemas/
│   │   │   ├── chat.py              # Pydantic request/response schemas for chat
│   │   │   ├── notes.py             # Pydantic request/response schemas for notes
│   │   │   ├── quiz.py              # Pydantic request/response schemas for quiz
│   │   │   ├── summarize.py         # Pydantic request/response schemas for summarizer
│   │   │   └── practice.py          # Pydantic request/response schemas for practice questions
│   │   ├── prompt_engine/
│   │   │   ├── prompt_builder.py    # ★ role prompting + context-aware prompting (chat)
│   │   │   ├── output_schemas.py    # ★ every structured JSON contract in the app
│   │   │   ├── templates/
│   │   │   │   ├── explain.py       # ★ zero-shot + structured prompt for the explainer
│   │   │   │   ├── quiz_gen.py      # ★ few-shot + structured prompt for the quiz generator
│   │   │   │   ├── summarize.py     # ★ map + reduce prompts for summarization
│   │   │   │   └── practice_gen.py  # ★ zero-shot prompts for practice Qs + feedback
│   │   │   ├── few_shot_examples/
│   │   │   │   └── quiz_examples.py # ★ example Q&A pairs shown to the model
│   │   │   └── chains/
│   │   │       ├── validated_generation.py  # ★ generic generate->validate->refine chain
│   │   │       ├── explain_chain.py          # feature wrapper for the explainer
│   │   │       ├── quiz_chain.py             # ★ batch generate -> per-item validate -> selective regen
│   │   │       ├── summarize_chain.py        # ★ map-reduce chunked summarization
│   │   │       └── practice_chain.py         # feature wrapper for practice Qs + feedback
│   │   ├── services/
│   │   │   ├── session_service.py   # shared session lookup/creation (used by all features)
│   │   │   ├── chat_service.py      # chat-specific logic
│   │   │   ├── notes_service.py     # notes/explainer-specific logic
│   │   │   ├── quiz_service.py      # quiz generation + scoring logic
│   │   │   ├── summarize_service.py # summarization logic
│   │   │   └── practice_service.py  # practice question + feedback logic
│   │   ├── routers/
│   │   │   ├── chat.py              # thin HTTP layer for chat — no business logic
│   │   │   ├── notes.py             # thin HTTP layer for notes — no business logic
│   │   │   ├── quiz.py              # thin HTTP layer for quiz — no business logic
│   │   │   ├── summarize.py         # thin HTTP layer for summarizer — no business logic
│   │   │   └── practice.py          # thin HTTP layer for practice Qs — no business logic
│   │   ├── utils/
│   │   │   └── text_chunking.py     # ★ splits long text into LLM-sized chunks
│   │   ├── providers/
│   │   │   ├── base_provider.py     # abstract interface
│   │   │   ├── gemini_provider.py
│   │   │   ├── openai_provider.py
│   │   │   ├── claude_provider.py
│   │   │   └── provider_factory.py  # picks provider based on config
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

---

## How to run it

### 1. Get an API key for at least one provider
- **Gemini (recommended — free tier):** https://aistudio.google.com/apikey
- OpenAI: https://platform.openai.com/api-keys
- Claude: https://console.anthropic.com/settings/keys

### 2. Set up the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# now open .env and paste your API key(s) in
# make sure LLM_PROVIDER matches the key you filled in (gemini / openai / claude)
```

### 3. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

You should see Uvicorn start on `http://127.0.0.1:8000`.

### 4. Test it

Open the auto-generated API docs in your browser — this is the fastest way to test
FastAPI endpoints without any frontend:

```
http://127.0.0.1:8000/docs
```

Or from the terminal:

```bash
# Health check
curl http://127.0.0.1:8000/api/health

# Full end-to-end LLM test
curl -X POST http://127.0.0.1:8000/api/test-llm \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain what a variable is, in one sentence."}'
```

**Expected result:** JSON containing `"provider"` (whichever you configured) and
`"response"` (the model's actual answer).

### 5. Try swapping providers (this is the point of this phase)

Edit `.env`:
```
LLM_PROVIDER=openai
```
Restart the server, hit `/api/test-llm` again — same endpoint, same code, different
model answering. This is the modularity the whole project architecture is built around.

---

## Testing Phase 1 (the chat assistant)

With the server running (`uvicorn app.main:app --reload --port 8000`), open
`http://127.0.0.1:8000/docs` and try these in order — or use curl:

```bash
# 1. Create a study session
curl -X POST http://127.0.0.1:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"subject": "Data Structures", "difficulty_level": "beginner"}'
# note the "id" in the response — you'll need it below

# 2. Chat within that session (replace 1 with your session id)
curl -X POST http://127.0.0.1:8000/api/sessions/1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a binary search tree?"}'

# 3. Ask a follow-up in the SAME session — this is the context-aware part.
# The assistant should understand "it" refers to a binary search tree
# without you repeating the term.
curl -X POST http://127.0.0.1:8000/api/sessions/1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Can you give me a simple example of it?"}'

# 4. View the full transcript
curl http://127.0.0.1:8000/api/sessions/1/messages

# 5. See your study history (all sessions)
curl http://127.0.0.1:8000/api/sessions
```

A SQLite file `study_buddy.db` will appear in `backend/` after your first request —
that's your whole database, viewable with any SQLite browser (e.g. "DB Browser for
SQLite") if you want to see the raw rows.

---

## Testing Phase 2 (the topic explainer / study notes)

Using the session id you created above (or make a new one):

```bash
# Generate a beginner explanation of a topic
curl -X POST http://127.0.0.1:8000/api/sessions/1/explain \
  -H "Content-Type: application/json" \
  -d '{"topic": "Recursion", "difficulty_level": "beginner"}'

# Try the SAME topic in "explain like I'm 5" mode — compare the tone/depth
curl -X POST http://127.0.0.1:8000/api/sessions/1/explain \
  -H "Content-Type: application/json" \
  -d '{"topic": "Recursion", "difficulty_level": "eli5"}'

# View every note generated in this session
curl http://127.0.0.1:8000/api/sessions/1/notes
```

Each response includes `summary`, `key_points`, `analogy`, `common_mistakes`, and
`follow_up_questions` — all guaranteed to be present and correctly typed, because
the response is validated against a schema before you ever see it. If you want to
see the self-correcting chain in action, you'd need to simulate a malformed LLM
response (that's what the automated test in this phase's development did) — in
normal use with a real API key you likely won't see it trigger often, since most
models get valid JSON right on the first try. It's there for the times they don't.

---

## Testing Phase 3 (the quiz generator)

```bash
# Generate a 5-question quiz (use a session id from earlier, or create a new one)
curl -X POST http://127.0.0.1:8000/api/sessions/1/quiz \
  -H "Content-Type: application/json" \
  -d '{"topic": "Recursion", "difficulty_level": "beginner", "num_questions": 5}'
```

Note the response has **no correct answers or explanations** — just questions,
options, and a `topic_tag` per question. Copy the `"id"` from the response, then:

```bash
# Submit your answers (replace 1 with your quiz id; these 5 indices are just an example)
curl -X POST http://127.0.0.1:8000/api/quizzes/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answers": [0, 1, 2, 0, 3]}'
```

This returns your `score`, `total`, `weak_topics` (sub-topics you got wrong), and
a full `results` breakdown with the correct answer and explanation for every
question — this is the reveal that only happens after submission.

You can also re-fetch a quiz without regenerating it:
```bash
curl http://127.0.0.1:8000/api/quizzes/1
```

**What to actually pay attention to when testing:** ask for a slightly unusual or
narrow topic and watch that every question stays on-topic and the 4 options per
question are genuinely distinct and plausible — that's the few-shot examples and
the deeper per-question validation doing their job. If you want to see the
selective-regeneration mechanic even more directly, that's demonstrated in this
phase's automated tests (a deliberately broken question got fixed individually
while the rest of the batch was left untouched, using 2 total LLM calls instead
of discarding and regenerating everything).

---

## Testing Phase 4 (summarizer + practice questions)

```bash
# Summarize some pasted study material
curl -X POST http://127.0.0.1:8000/api/sessions/1/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Paste a paragraph or two of real lecture notes or textbook text here — needs to be at least 50 characters.", "difficulty_level": "beginner"}'

# Generate open-ended practice questions
curl -X POST http://127.0.0.1:8000/api/sessions/1/practice \
  -H "Content-Type: application/json" \
  -d '{"topic": "Recursion", "difficulty_level": "beginner", "num_questions": 3}'

# Submit a written answer to question 0 of that set (replace 1 with your set id)
curl -X POST http://127.0.0.1:8000/api/practice/1/feedback \
  -H "Content-Type: application/json" \
  -d '{"question_index": 0, "answer": "Write your own attempt at answering the question here."}'
```

To actually see the map-reduce chunking kick in, paste something long — several
paragraphs, 3000+ characters. Short text (a paragraph or two) intentionally skips
chunking and summarizes directly in one call; this is the efficiency trade-off
worth mentioning if this comes up in your viva.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `400 ... API_KEY is missing` | You forgot to fill in the key in `.env`, or `LLM_PROVIDER` doesn't match a key you set |
| `502 LLM provider error` | Network issue, invalid/expired key, or rate limit — the message will tell you which |
| `ModuleNotFoundError` | Activate your venv and re-run `pip install -r requirements.txt` |
| CORS errors (once frontend exists) | Check `CORS_ORIGINS` in `.env` matches your frontend's actual URL |

---

## What's next

The backend now covers every core content feature from the original spec:
conversational assistant, topic explanations (4 difficulty modes), study notes,
MCQ quizzes with scoring, practice questions with AI feedback, and material
summarization. Not yet built: the React frontend, and the "advanced" features
(weak-topic detection, adaptive difficulty, flashcards, study plans, progress
dashboard, document upload/chat-with-material) — pick up with those whenever
you're ready to continue.
