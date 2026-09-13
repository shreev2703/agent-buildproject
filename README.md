# agent-buildproject

A small Python LLM agent (mirroring a `BaseAgent` structure) deployed as a Vercel
serverless function. Built as a learning exercise before joining a research team's
agentic AI system for engineering lab courses.

Live: https://agent-buildproject.vercel.app

## How it works

```
browser  --POST /api/agent {agent, input}-->  api/agent.py (handler)
                                                  |  builds a fresh agent
                                                  |  agent.process_request(input)
                                                  |     -> generate_response(prompt)
                                                  v
                                             Gemini REST API  (key from env var)
browser  <--JSON {agent, response}-----------  handler
```

- `agents/base_agent.py` — abstract `BaseAgent`. Holds the "index card"
  (`system_message`, `instructions`, `knowledge_base`), model settings
  (`model`, `temperature`, `seed`), a `status` field, and `generate_response()`,
  the only method that touches the network. Subclasses must implement
  `process_request()`.
- `agents/feedback_agent.py` — reviews student code. Keeps one turn of memory by
  concatenating the previous input/response into the next prompt.
- `agents/tutor_agent.py` — explains concepts. Stateless; uses `knowledge_base`
  to describe what students have and haven't covered.
- `agents/utils.py` — `file_to_string(path)`.
- `api/agent.py` — the Vercel function. Stateless: a new agent object per request.
- `public/index.html` — minimal front end that calls `/api/agent`.
- `dev_server.py` — local stand-in for Vercel (its Python dev tooling breaks on Windows).
- `test_agent.py`, `test_memory.py`, `test_tutor.py` — run agents locally; save
  input / assembled prompt / output to `outputs/`.

## Run locally

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
echo GEMINI_API_KEY=your-key > .env
python test_agent.py                # one-shot feedback on samples/buggy_average.py
python test_memory.py               # two turns, shows the memory concatenation
python dev_server.py                # http://localhost:3000
```

## Deploy

```
vercel --prod
```

Set `GEMINI_API_KEY` in the Vercel dashboard (Settings > Environment Variables).
The key never reaches the browser: the page only calls `/api/agent`.

## Things I learned

- **System message vs. instructions vs. user prompt.** The API has two slots:
  system (the rules) and user (the thing to work on). `system_message`,
  `instructions` and `knowledge_base` are glued into the system slot; the split
  is a convention for us, not the model.
- **temperature / seed.** Temperature 0 = pick the most likely next token every
  time (consistent, good for grading); higher = more varied. Seed fixes the
  randomness so reruns match (best effort, not guaranteed).
- **Memory by concatenation** is simple and transparent but: remembers one turn,
  grows the prompt (cost + context limit), and lives in the Python object, so it
  vanishes between serverless requests. Real memory must live in a database.
- **Agent vs. wrapper.** A wrapper calls the model once on a fixed path. An agent
  lets the model *decide* the next step (call a tool, loop). This code is a
  configured wrapper; the base class is what agents get built on.
- **Tools** are functions the model can *request* mid-task. Something run before
  the model call (like reading a file) is preprocessing, not a tool.
- **Orchestrator** = the code that decides which agent runs, in what order, with
  what data. Either hard-coded Python or an LLM agent with other agents as tools.
  Agents coordinate through shared state (DB), not by talking directly.
- **Serverless:** stateless, cold starts (~1-3s), ~60s max on Hobby, key via
  dashboard env var. Moving a persistent server here means: in-memory state ->
  DB, long jobs -> background worker, startup work -> keep light.
- **Scale breakpoints:** free-tier rate limits at deadline spikes (first to hit),
  latency when chaining agents, context limits with growing history, and API
  failures that need retries/fallbacks/logging.

## Still unsure — questions for the team

1. Is the orchestrator hard-coded (Python calls agents in order) or LLM-driven
   (an agent picks which agents to run)? Does it call the model itself?
2. Is the PDF extractor run *before* the model (preprocessing) or *requested by*
   the model (a real tool)?
3. Which agents actually need memory across turns? On serverless that means a
   MongoDB read/write on every request.
4. Which LLM provider, and what are its rate limits? A class submitting at
   11:59pm will hit per-minute caps before anything else breaks.
5. Do any agents run longer than ~60s (batch grading, multi-agent chains)?
   Vercel Hobby kills those; they'd need a background worker (Northflank?).
6. What in the old Azure app held state in memory (sessions, caches, agent
   objects)? Each one has to move to the DB during migration.
7. Is Vercel Hobby's non-commercial clause OK for a funded research project?
