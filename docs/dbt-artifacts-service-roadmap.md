# dbt Artifacts Service — 12 Week Build Plan

**Goal:** by end of December 2026 (may slip to late January 2027), open an empty directory and get to a typed, tested FastAPI service running in a container with green CI — without help.

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
- [ ] Never use Trustpilot artifacts. Public repo. Use your own `dbt_tennis` fixtures only.
- [ ] Branch per session (`session-3-edge`, etc.) instead of committing straight to `main`.
- [ ] Before every commit: `uv run mypy src`, `uv run ruff check`, `uv run pytest`.

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

**Session 1 — Scaffold (2 hrs)** ✅ done
- [x] `uv init --package`, `src/` layout
- [x] Add deps: `uv add fastapi pydantic`, `uv add --dev mypy pytest ruff`
- [x] Configure `pyproject.toml`: mypy **strict mode**
- [x] `uv run pytest` passes with one trivial test
- [x] `uv run mypy src` clean
- [x] Commit

*Goal: tooling green before there's anything to break.*

**Session 2 — One model, by hand (2 hrs)** ✅ done
- [x] Write a single `Node` Pydantic model (database, schema_/alias, resource_type, original_file_path, unique_id, description, created_at)
- [x] `parse_manifest()`: open manifest → pull `nodes` → return `list[Node]`
- [x] One test asserting node count + every node has a `unique_id`
- [x] Commit

**Loose ends carried over from Week 1** ✅ done
- [x] Add ruff config: `line-length = 100`, `select = ["E", "F", "I", "UP"]`
- [x] Remove unused `import pytest` in `test_parse.py`; run `uv run ruff format`
- [x] Rename test to `test_parse_manifest_returns_nodes`
- [x] Fixed `Optional`/`List` `NameError` in `model.py` by switching to built-in `str | None` / `list[...]` (Python 3.12, no `typing` import needed)

*Expected friction (this is the curriculum): sometimes-null fields, `resource_type` wanting to be an enum, nested config objects.*

### Week 2 ✅ done

Read Robust Python chapters on enums and Optional/Union first.

- [x] Replace `resource_type: str` with an `Enum` or `Literal` — try both, decide which fits
- [x] Add `name`, `package_name` to `Node` — only add more fields once something downstream actually needs them (keep it minimal, not the full original field list)
- [x] `Edge` model from `parent_map` (`unique_id: [parent unique_ids]`) — attempt cold before asking for help
- [x] Tests for awkward cases: node with no parents, seed vs model vs test
- [x] Failure-case test: broken/missing field → `pytest.raises(ValidationError)`
- [x] mypy strict clean throughout
- [x] Commit

### Week 3
- [x] `Invocation` model: invocation_id, generated_at, dbt_version, target, elapsed_time
- [x] `NodeResult` model: invocation_id, unique_id, status, execution_time, rows_affected, bytes_processed, message
- [x] Dig `bytes_processed` out of `adapter_response`
- [x] Tiny CLI (argparse is fine): takes both file paths, prints 5 slowest models
- [x] Commit

**Checkpoint:** something that runs end to end and produces an answer you'd actually want.

---

## Phase 2 — Testing (Weeks 4–6)

**Reading:** Okken, *Python Testing with pytest* — fixtures and parametrization chapters before Week 4,
test doubles / monkeypatch before Week 5. Apply within 24 hours, note in `NOTES.md`.

**Entry check:** `uv run mypy src` clean on the Week 3 code before starting. Fix first if not.

### Week 4 — Fixtures & parametrisation

**Session 1 — conftest.py (2 hrs)**
- [ ] Create `tests/conftest.py`. Move fixture-path logic (`Path(__file__).parent / "fixtures"`) into fixtures
- [ ] Fixture for the parsed manifest and parsed run_results. Decide the scope (`function` vs `module` vs `session`)
      and write down in NOTES.md why — what's the risk of sharing a parsed object across tests?
- [ ] Use the built-in `tmp_path` fixture to write small, deliberately broken JSON files inside the test,
      instead of committing broken fixture files
- [ ] Use the built-in `capsys` fixture to test the CLI's output (the 5 slowest models, in order)
- [ ] `uv run pytest --fixtures` — find yours in the list

**Session 2 — Parametrise (2 hrs)**
- [ ] Parametrise one test over every `ResourceType` member you support
- [ ] Parametrise `NodeResult` over each `status` value in your fixture (success / error / skipped / pass / fail / warn — check which actually appear)
- [ ] Parametrise `adapter_response` shapes: `bytes_processed` present, missing, empty dict. Predict each outcome first
- [ ] Give parametrised cases readable `ids` so failures say *which* case broke
- [ ] Commit

*Done when: no test builds its own file path, and adding a new resource type is a one-line change in the tests.*

### Week 5 — Test doubles & testing behaviour

**Session 1 — Separate I/O from parsing (2 hrs)**
- [ ] Learn the vocabulary: dummy, stub, fake, spy, mock. One line each in NOTES.md, with an example from this project
- [ ] Question first: which of your functions read files, and which only transform data? Write the answer down
- [ ] Refactor so parsing takes already-loaded data and file reading lives in one thin place.
      Keep the public `parse_manifest(path)` working — existing tests must stay green through the refactor
- [ ] Rewrite the awkward-case tests to pass small hand-built dicts instead of reading files.
      Notice how many doubles you *didn't* need. That's the lesson.

**Session 2 — Factories, monkeypatch, coverage (2 hrs)**
- [ ] A factory fixture in conftest: returns a minimal valid node dict, with keyword overrides for the one field a test cares about
- [ ] `monkeypatch` once, for something genuinely external (e.g. `sys.argv` for the CLI). Then ask: would passing
      arguments in directly have been simpler?
- [ ] `uv add --dev pytest-cov`; run a coverage report. Backfill tests for anything in Weeks 1–3 that's uncovered *and matters*
- [ ] Find one test that checks *how* something is done rather than *what* comes out. Rewrite it or delete it
- [ ] Commit

*Coverage is a map of what's untested, not a target. Don't chase 100%.*

### Week 6 — Defensive parsing (versioned contract)

**Session 1 — Pin the schema version (2 hrs)**
- [ ] Look in your fixtures: where do `manifest.json` and `run_results.json` declare their schema version? Write the exact values down
- [ ] `Metadata` model for the bits you need from `metadata`
- [ ] Define the set of versions you support (one each is fine)
- [ ] Your own exception class for unsupported versions. The message should name the file, the version found and the versions supported
- [ ] Check the version *before* parsing nodes/results. Ask yourself why the order matters

**Session 2 — Failure paths (2 hrs)**
- [ ] Tests: supported version passes; unsupported version raises *your* exception (use `match=` to check the message);
      missing `metadata` fails clearly
- [ ] Decide what happens on malformed JSON: let `json.JSONDecodeError` through, or wrap it? Write the decision in NOTES.md
- [ ] Revisit `extra="forbid"`: would it make parsing safer or just break on every dbt release? Decide and note why
- [ ] CLI: a bad file gives a one-line error and a non-zero exit code, not a traceback. Test it (`pytest.raises(SystemExit)` + `capsys`)
- [ ] Commit

*Interview line: "I consume a versioned external contract — pinned, validated up front, loud on drift."*

**Phase 2 checkpoint**
- [ ] Full suite runs in well under a second
- [ ] You can explain every fixture in conftest.py without looking
- [ ] Drill: delete `conftest.py`, rebuild it from scratch two days later
- [ ] Then read cosmicpython.com

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
- [ ] Multi-stage Dockerfile (`uv sync --no-dev` in the final stage — dev deps stay out of the image)
- [ ] GitHub Actions running: mypy, ruff, pytest, container build
- [ ] Deploy to Cloud Run
- [ ] **Optional, only if on schedule:** one LLM call with Pydantic-validated structured output — small taste of the AI-engineering target without derailing the project

*Cloud Run deploy is where January's infrastructure work (Terraform, Vertex AI) picks up.*

---

## Cut ruthlessly

No auth. No web UI. No multi-tenancy. No async ingest queue.

Every one of those sounds plausible and will eat a month teaching you nothing you need.

**If it's still boring and small in December, it worked.**

---

## Resources, in priority order

1. **FastAPI official docs** — best official tutorial in the Python ecosystem. Do the whole Tutorial - User Guide. **TestDriven.io's FastAPI + Docker course** is a good companion for Weeks 7–12 (API, then container).
2. **Robert Viafore, *Robust Python*** — reference, not a cover-to-cover read. Pull the relevant chapter just-in-time (e.g. enums/Optional before Week 2), apply it within 24 hours, note the takeaway in `NOTES.md`.
3. **ArjanCodes (YouTube)** — Python software *design* for people who know the syntax. Watch the refactoring videos where he improves working-but-bad code. That's the skill you want.
4. **cosmicpython.com** (*Architecture Patterns with Python*) — free online. After Week 6.
5. **Brian Okken, *Python Testing with pytest*** — short, practical. *Test & Code* podcast is good commute material.
6. **Astral uv + ruff docs** — brief, both are now the Python default.
7. **mCoding (YouTube)** — his logging video is the clearest explanation of Python's logging module anywhere.

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
