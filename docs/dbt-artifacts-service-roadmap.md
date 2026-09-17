# dbt Artifacts Service — 12 Week Build Plan

**Goal:** by end of December 2026, open an empty directory and get to a typed, tested FastAPI service running in a container with green CI — without help.

**Budget:** ~4 hrs/week, two 2-hour sessions.
**Window:** September – December 2026 (autumn technical sprint, before N2 prep starts).

---

## The AI rule

Claude can **explain, review, and unblock**. It cannot produce code you keep.

- Stuck 20+ min → ask *why* something fails, or ask for the concept. Then close the tab and write it yourself.
- Finished something → paste it in, ask *"what would a senior Python engineer flag in code review?"* This is the highest-value use.
- Never accept a generated function into the repo. If you didn't type it, you didn't learn it.
- Type everything by hand, including doc examples. Copy-paste kills recall.

**Drill:** build a small thing, delete it entirely, rebuild from scratch two days later. The second build is where learning lands.

---

## Standing habits

- [ ] Commit after every session with a real message. The git history is part of what you show people. "1000 lines, initial commit" reads as generated.
- [ ] Keep `NOTES.md` — what confused you, how you resolved it. Five minutes a session. In six months it's what you draw on in interviews.
- [ ] Never use Trustpilot artifacts. Public repo. Use `jaffle_shop_duckdb` only.

---

## Session 0 — Setup (1 hr, no Python)

- [ ] Install dbt + duckdb adapter
- [ ] Clone `dbt-labs/jaffle_shop_duckdb`, run `dbt build`
- [ ] Run `dbt build` a **second time** (need 2+ invocations for the fact table later)
- [ ] Open `target/manifest.json` in a JSON viewer. Navigate by hand:
  - [ ] Find `nodes`, pick one model, look at every key
  - [ ] Find `parent_map`
- [ ] Open `target/run_results.json`:
  - [ ] Find the `results` array
  - [ ] Find one node's `timing` and `adapter_response`
- [ ] Write a plain-text note listing the fields you actually want

**Don't parse anything yet.** Deciding what to ignore is the first real design decision — it's yours, not Claude's.

---

## Phase 1 — Parsing & typing (Weeks 1–3)

In-memory only. No database. Learn typing and parsing without fighting an ORM.

### Week 1

**Session 1 — Scaffold (2 hrs)**
- [ ] `uv init`, `src/` layout
- [ ] Add deps: pydantic, pytest, mypy, ruff
- [ ] Configure `pyproject.toml`: mypy **strict mode**, ruff
- [ ] `uv run pytest` passes with one trivial test
- [ ] `uv run mypy src` clean on empty package
- [ ] Commit

*Goal: tooling green before there's anything to break.*

**Session 2 — One model, by hand (2 hrs)**
- [ ] Write a single `Node` Pydantic model, ~6 fields, typed
- [ ] Function: open manifest → pull `nodes` → return `list[Node]`
- [ ] One test asserting expected model count
- [ ] Commit

*Expected friction (this is the curriculum): sometimes-null fields, `resource_type` wanting to be an enum, nested config objects.*

### Week 2
- [ ] Widen `Node` to full field set: unique_id, name, resource_type, package, path, materialization, tags, description, checksum
- [ ] Add `ResourceType` enum
- [ ] Add `Edge` model parsed from `parent_map`
- [ ] mypy strict passing on all of it
- [ ] Tests for awkward cases: node with no parents, source vs model
- [ ] Commit

### Week 3
- [ ] `Invocation` model: invocation_id, generated_at, dbt_version, target, elapsed_time
- [ ] `NodeResult` model: invocation_id, unique_id, status, execution_time, rows_affected, bytes_processed, message
- [ ] Dig `bytes_processed` out of `adapter_response`
- [ ] Tiny CLI (argparse is fine): takes both file paths, prints 5 slowest models
- [ ] Commit

**Checkpoint:** something that runs end to end and produces an answer you'd actually want.

---

## Phase 2 — Testing (Weeks 4–6)

- [ ] Fixtures — conftest.py, scope, shared test artifacts
- [ ] Parametrised tests
- [ ] Test doubles: what a fake/stub/mock is, when each is right
- [ ] Learn why you don't test implementation details
- [ ] Backfill coverage on the Week 1–3 parsers
- [ ] Defensive parsing: manifest schema is **versioned and changes between dbt releases**. Pin the version you support, fail loudly on unexpected ones. Test that failure path.

*Will feel familiar from dbt tests — but the mental model is different, and that difference is the point.*

*Consuming a versioned external contract is a genuine platform-engineering problem. Good thing to be able to talk about in interviews.*

**Read after Week 6, not before:** cosmicpython.com — it'll land once you've felt the pain it solves.

---

## Phase 3 — FastAPI (Weeks 7–9)

Work through FastAPI's official Tutorial - User Guide, but build **your** API alongside it, not theirs.

- [ ] Endpoints, path/query params
- [ ] Dependency injection
- [ ] Request/response models
- [ ] Error handling
- [ ] `TestClient` wired into your existing pytest suite

**Endpoints to build:**
- [ ] `POST /invocations` — ingest both artifacts
- [ ] `GET /nodes` — list with filters
- [ ] `GET /nodes/{unique_id}` — single node
- [ ] `GET /nodes/{unique_id}/runs` — run history
- [ ] `GET /nodes/{unique_id}/lineage` — upstream/downstream
- [ ] `GET /failures` — recent failures
- [ ] `GET /slowest` — slowest models over a window

**Add SQLite + SQLAlchemy around Week 5–7**, once tests exist to tell you when persistence breaks something.

**Schema — four tables. Resist adding more.**

| Table | Fields |
|---|---|
| `node` | unique_id, name, resource_type, package, path, materialization, tags, description, checksum |
| `edge` | parent_unique_id, child_unique_id |
| `invocation` | invocation_id, generated_at, dbt_version, target, elapsed_time |
| `node_result` | invocation_id, unique_id, status, execution_time, rows_affected, bytes_processed, message |

*manifest = slowly-changing dimension. run_results = append-only fact stream keyed on `invocation_id`.*

**One genuinely useful addition once reads work:**
- [ ] Flag a model whose `execution_time` exceeds some multiple of its trailing median

*Three lines of logic. It's a performance regression detector — exactly what an ML platform team builds for model latency.*

---

## Phase 4 — Logging, container, CI (Weeks 10–12)

- [ ] Structured JSON logging with correlation IDs (**not `print`**)
- [ ] Multi-stage Dockerfile
- [ ] GitHub Actions running: mypy, ruff, pytest, container build
- [ ] Deploy to Cloud Run

*Cloud Run deploy is where January's infrastructure work (Terraform, Vertex AI) picks up.*

---

## Cut ruthlessly

No auth. No web UI. No multi-tenancy. No async ingest queue.

Every one of those sounds plausible and will eat a month teaching you nothing you need.

**If it's still boring and small in December, it worked.**

---

## Resources, in priority order

1. **FastAPI official docs** — best official tutorial in the Python ecosystem. Do the whole Tutorial - User Guide.
2. **ArjanCodes (YouTube)** — Python software *design* for people who know the syntax. Watch the refactoring videos where he improves working-but-bad code. That's the skill you want.
3. **cosmicpython.com** (*Architecture Patterns with Python*) — free online. After Week 6.
4. **Brian Okken, *Python Testing with pytest*** — short, practical. *Test & Code* podcast is good commute material.
5. **Astral uv + ruff docs** — brief, both are now the Python default.
6. **mCoding (YouTube)** — his logging video is the clearest explanation of Python's logging module anywhere.

**Skip:** general Python courses, Real Python's beginner track, anything titled "Python for Data Science." You're past all of it.

---

## Where this sits in the bigger plan

| Period | Focus |
|---|---|
| **Sep–Dec 2026** | This project + PMLE cert. Japanese as steady background build. |
| **Jan–Mar 2027** | Dissertation scoped so building it *forces* Terraform / Cloud Run / Vertex AI. Lock scope by mid-Jan. Register for July JLPT in March. |
| **Apr 2027** | Dissertation due. Stop learning new tools. |
| **May–Jun 2027** | N2 sprint — mock papers under timing, daily listening. |
| **Jul 2027** | N2 exam. |
| **H2 2027** | **Get ML-platform work into the day job at Trustpilot.** This is the one that makes the pivot legible. Start N1 prep. |
| **Autumn 2027** | Zenn write-ups in Japanese. CV + 職務経歴書. Recruiter conversations. |
| **2028** | Application year. |

---

## Recalibrate if

Session 0 + Week 1 feel wrong — too easy or too hard. Scope is adjustable; the shape isn't.
