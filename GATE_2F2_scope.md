The queue is the seam. Everything upstream of it is HTTP + decode;
everything downstream is existing pipeline code. We do not introduce a
new data path through the pipeline — we feed the existing one from a
new source.

## Deferred decisions (explicitly parked, do not decide in 2.f.2)

These are called out so the implementation doesn't accidentally lock us
into one answer by being hasty:

1. **Response correlation.** The handler returns 200 on successful
   queue-put, not on pipeline completion. If a client wants to know
   "what did frame seq=42 produce," they poll `/stats/ingest` and
   `/objects`. A per-frame correlation mechanism (websocket side-channel
   or `/ingest/result/{seq}`) is a future gate.
2. **Backpressure policy.** When the queue is full, the handler returns
   HTTP 503 immediately — no blocking, no buffering beyond the queue.
   Whether the "right" queue size is 1, 4, or 16 is a tuning question
   that belongs downstream of a working first version.
3. **Consumer crash handling.** If `pipeline.run_forever()` dies, the
   queue fills, the handler starts 503ing. A supervisor / restart
   policy is not in 2.f.2.
4. **Multipart/binary body.** The ~11 ms framing overhead could be
   reduced by replacing base64-in-JSON with multipart or raw binary.
   Not now. Revisit if 2.f.2 integration reveals pipeline is comfortably
   inside budget.
5. **`FrozenWorkingMemory` in ingest mode.** Confirmed: ingest mode
   requires writable WM. Frozen WM stays serve-mode-only.

## Commit sequence (ordered, each a separate commit)

Each item below is intended to be a single commit small enough to
review in one sitting. If any one of them feels like it's growing
beyond that, stop and split it.

### Commit 1 — `run.py` gets an `--ingest` mode

- Add `--ingest` CLI flag parallel to `--serve`.
- In `--ingest` mode, construct:
  - writable `WorkingMemory`
  - full `Pipeline` (SAM, SigLIP, association, WM upsert)
  - an `IngestQueue` (bounded, size TBD during impl; start with 4)
  - the FastAPI app, with the queue wired into app state via lifespan
  - a background thread running `pipeline.run_forever(source=queue)`
- Does **not yet** modify `/ingest/keyframe`. The endpoint still
  returns `mode: "decode-only"` at the end of this commit.
- Acceptance: `run.py --ingest` starts up, `/stats/ingest` responds,
  pipeline thread is alive (add a heartbeat field to `/stats/ingest`
  showing queue depth and consumer-thread status).

### Commit 2 — handler pushes decoded frames to the queue

- Introduce `FramePacket.from_decoded(...)` classmethod (or factory
  function in `rtsm/api/` — decide during impl based on where
  `FramePacket` lives).
- Modify `/ingest/keyframe`: after successful decode, construct a
  `FramePacket` and `ingest_queue.put_nowait(packet)`.
- On queue-full: return HTTP 503 with structured body. Increment a new
  `queue_full_drops` counter in `/stats/ingest`.
- On success: return `mode: "queued"` (new mode string) with timings
  that include the queue-put duration as a new stage.
- Acceptance: POST frames, watch queue depth rise and fall in
  `/stats/ingest`, confirm objects appear in `/objects`.

### Commit 3 — the integration test

- One test in `tests/test_ingest_pipeline.py` (new file).
- Posts ~10 frames from the curated recording, waits for consumer to
  drain queue, asserts:
  - `/stats/ingest` shows `frames_received == 10`, `queue_full_drops == 0`
  - `/objects` returns at least one object
  - pipeline thread is still alive
- Module-skips if the pipeline dependencies (SAM weights, SigLIP
  weights) aren't available in the test environment — mirrors the
  pattern in `test_ingest_keyframe.py`.
- Acceptance: test green on Orin, passes with and without
  `--synthetic-pose`.

## What "2.f.2 is done" looks like

All three commits land. The integration test is green. Manual smoke
test: run `rtsm.tools.replay` against an `--ingest` server for 200
frames, watch `/objects` grow, observe no queue drops at 15 Hz. The
replay summary shows a new latency component (queue-put) but total
client latency remains well under 66 ms/frame.

When all of the above is true, `git rm GATE_2F2_scope.md` in the same
commit as the integration test.

## What to read first when starting implementation

In order, as context for writing Commit 1:

1. `rtsm/run.py` — how `--serve` mode is constructed today. The
   `--ingest` mode parallels this.
2. `rtsm/io/replayer.py` — the closest existing analog to "something
   feeds the pipeline from a source." The threading model for
   `pipeline.run_forever(source=...)` lives here, if it lives anywhere.
3. `rtsm/core/pipeline.py` — specifically `run_forever`, `run_one_step`,
   and whatever the `source` interface expects. The queue needs to
   match that interface (probably has a `.get(timeout=...)` method).
   **If `run_forever` is hardcoded to one source type, Commit 1 also
   needs a small refactor to accept any queue-like source.**
4. `rtsm/api/server.py` — the handler we're modifying, and the existing
   `/stats/ingest` counter pattern we extend for queue metrics.
5. `tests/test_ingest_keyframe.py` — the test pattern to copy for
   Commit 3 (live HTTP, skip-if-container-down, uses real recording).

## Non-goals

- Performance optimization. First make it work, then measure.
- Real-pose replay. Blocked on `/tf` capture in the recorder; that's
  a separate follow-up.
- Anything in `rtsm/mcp/` or `rtsm/analytics/`. Out of scope.
- Changes to model inference, embedding dimensions, association
  thresholds, or working memory schema. None of these should need to
  move for 2.f.2.
