# Example task — Implementation plan for parallel workers (shared client lifecycle)

Date: 2026-04-02

## Goal

Remove the risky shared client lifecycle from `app/workflows/search_tool.py` without changing unrelated areas.

## Explicit non-goals

- Do **not** refactor the separate LLM client path in this task.
- Do **not** redesign all global caches in the service.
- Do **not** broaden the task into general agent/tool architecture cleanup.
- Do **not** optimize for connection reuse in this task unless correctness forces it.

## Desired end state

After the change:
- search operations do **not** rely on a process-global `_search_client`
- token refresh does **not** close a shared client at runtime
- each search operation has clear ownership of the client it uses
- `search_documents()` preserves its current external behavior
- tests assert the new ownership model directly

## High-level execution model

This task can be split into **3 parallel workers plus 1 final integrator pass**.

### Recommended worker split

- **Worker 1 — Core refactor**
  - Owns `app/workflows/search_tool.py`
  - Main responsibility: remove singleton lifecycle and introduce operation-scoped client ownership

- **Worker 2 — Cleanup / call-site alignment**
  - Owns `app/service_definition.py`
  - Optionally also updates any imports/usages affected by Worker 1 if needed, but should avoid editing `search_tool.py`
  - Main responsibility: remove or adapt shutdown cleanup assumptions about a global client

- **Worker 3 — Tests**
  - Owns:
    - `tests/tools/test_search_tool.py`
    - any narrow token-provider tests if needed
  - Main responsibility: update tests to validate the new lifecycle model

- **Integrator (main thread)**
  - Resolves final shape across workers
  - Runs validation
  - Handles any small glue edits not cleanly owned elsewhere

## Dependency graph

### Can run immediately in parallel
- Worker 1 and Worker 3 can start immediately.
- Worker 2 can also start immediately because cleanup assumptions are easy to inspect independently.

### Likely merge dependency
- Worker 3 will probably need to adapt to the exact API shape chosen by Worker 1.
- So Worker 3 should aim for:
  - test scaffolding first
  - then a final adjustment after Worker 1 lands its refactor shape

### Critical path
1. Worker 1 finalizes the lifecycle design in `search_tool.py`
2. Worker 2 confirms cleanup changes are consistent
3. Worker 3 aligns tests to the final API
4. Integrator runs validation and resolves leftovers

## Detailed worker plans

---

## Worker 1 — Core refactor

### Ownership
- `app/workflows/search_tool.py`

### Objective
Replace the shared client singleton with operation-scoped client ownership.

### Required changes
1. Remove process-global shared client state:
   - `_search_client`
   - `get_search_client()` in its current singleton form
   - `_invalidate_search_client()` if no longer needed
   - `register_token_update_callback(...)` usage for this client

2. Introduce a creation path for a fresh client per operation.

3. Refactor internal helper flow so helpers accept an explicit client instead of fetching a hidden singleton.
   - especially `_resolve_collection_from_metadata()`
   - and any helper that indirectly depends on global client state

4. Update `search_documents()` so it:
   - creates a client
   - passes that client down explicitly
   - closes the client deterministically

### Constraints
- Preserve the current external `search_documents()` contract.
- Preserve collection selection behavior.
- Avoid changing embedding behavior in this task unless absolutely necessary.

### Expected output
A self-contained refactor in `search_tool.py` that removes shared runtime client ownership.

### Handoff notes for integrator
Please document in the summary:
- exact helper(s) introduced/renamed
- whether `close_search_client()` still exists
- whether any temporary compatibility shim remains

---

## Worker 2 — Cleanup / service-definition alignment

### Ownership
- `app/service_definition.py`
- optionally tiny follow-up imports/usages outside tests if strictly required

### Objective
Remove assumptions that the service owns a process-global client that must be shut down at service cleanup.

### Required changes
1. Re-evaluate `_cleanup()` in `app/service_definition.py`.
2. If the client singleton is fully removed, update cleanup accordingly.
3. If Worker 1 leaves a compatibility function, decide whether to:
   - keep cleanup calling it temporarily, or
   - remove the cleanup hook entirely if it becomes dead logic

### Constraints
- Do not modify `search_tool.py` unless the integrator explicitly asks for a tiny compatibility follow-up.
- Keep the change small and cleanup-focused.

### Expected output
A minimal cleanup path consistent with operation-scoped client ownership.

### Handoff notes for integrator
Please note whether:
- cleanup becomes unnecessary
- cleanup remains as a no-op compatibility layer
- any service lifecycle comments/docstrings should be adjusted

---

## Worker 3 — Tests

### Ownership
- `tests/tools/test_search_tool.py`
- optionally narrow token-provider tests only if needed

### Objective
Shift test coverage from “singleton exists and works” to “operation-scoped ownership is correct”.

### Required changes
Add or adapt tests so they prove the new lifecycle.

Minimum target coverage:
1. `search_documents()` creates and closes a client per operation.
2. Collection metadata helpers operate on an explicitly supplied client.
3. The client is no longer tied to token-update invalidation callback behavior.
4. Tests no longer rely on `_search_client` global state.

### Good candidates for test updates
- remove/reset logic around `_search_client`
- stop asserting singleton reuse behavior
- add mocking around fresh client creation and close calls

### Constraints
- Prefer unit tests over broad integration changes.
- Keep integration tests only where they still add value.
- Avoid guessing Worker 1’s exact helper names too early; finalize after sync.

### Expected output
Tests that clearly encode the new lifecycle contract.

### Handoff notes for integrator
Flag any tests that had to change because of:
- removed helper names
- changed internal call boundaries
- changed cleanup behavior

---

## Integrator pass

### Responsibilities
1. Merge Worker 1, 2, and 3 outputs.
2. Resolve final naming/shape disagreements.
3. Remove any temporary compatibility code that is no longer needed.
4. Run narrow validation.
5. Confirm acceptance criteria.

### Integration checklist
- [ ] No process-global `_search_client` remains
- [ ] No token-refresh invalidation callback remains for this client
- [ ] `search_documents()` explicitly owns client creation and close
- [ ] Service cleanup is consistent with the new lifecycle
- [ ] Tests no longer encode singleton assumptions

## Suggested sequence for actual parallel execution

### Round 1 — parallel start
- Start Worker 1 on `search_tool.py`
- Start Worker 2 on `service_definition.py`
- Start Worker 3 on test preparation and obvious singleton-dependent assertions

### Round 2 — sync point
After Worker 1 finishes its first pass:
- share the final helper/API shape with Worker 3
- confirm whether `close_search_client()` survives in any form with Worker 2

### Round 3 — finalize
- Worker 3 finishes test alignment
- Integrator resolves leftovers and runs validation

## File write boundaries

To reduce merge conflicts, keep ownership strict:

- **Worker 1 writes only:**
  - `app/workflows/search_tool.py`

- **Worker 2 writes only:**
  - `app/service_definition.py`

- **Worker 3 writes only:**
  - `tests/tools/test_search_tool.py`
  - plus any explicitly approved narrow test file

If a worker needs another file changed, hand it back to the integrator unless it is trivial and clearly assigned.

## Acceptance criteria

The task is complete when all of the following are true:

1. `app/workflows/search_tool.py` no longer stores a process-global shared client.
2. The client is no longer registered as a token-update invalidation callback.
3. `search_documents()` owns the client lifecycle used for its operation.
4. Internal helper functions no longer fetch the client implicitly from module-global state.
5. `app/service_definition.py` no longer assumes a global client must be shut down.
6. Relevant tests cover the new lifecycle expectations.
7. No unrelated client or provider changes were introduced.

## Validation plan

### Minimum validation
Run the smallest relevant set first:
- targeted search-tool tests
- any narrow tests affected by cleanup changes
- any narrow token-provider tests only if touched

### Expand only if needed
Broaden validation only if:
- test failures indicate wider coupling
- the final refactor changes public/internal interfaces used by more than the targeted tests

## Risks during parallel execution

### Risk 1 — Worker 3 guesses the wrong final helper shape
Mitigation:
- let Worker 3 prepare lifecycle-focused assertions first
- do one quick sync after Worker 1 settles helper names

### Risk 2 — cleanup logic drifts from the actual refactor
Mitigation:
- Worker 2 should keep changes minimal and only reflect Worker 1’s final ownership model

### Risk 3 — hidden singleton assumptions survive in tests or comments
Mitigation:
- integrator should grep for `_search_client`, `close_search_client`, and `register_token_update_callback` on the target path before finalizing

### Risk 4 — unnecessary broadening into unrelated client or provider refactors
Mitigation:
- reject any change that touches unrelated subsystems unless it is required for build/test reasons

## Optional follow-up

If performance later shows per-operation connection creation is too expensive, a separate follow-up task could evaluate a safer reuse model such as:
- request-scoped reuse
- a dedicated manager abstraction with explicit ownership
- synchronized invalidation semantics

That optimization should be a separate task, not part of this correctness fix.
