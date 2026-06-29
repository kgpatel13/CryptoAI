# CryptoAI v4.0.1 — Windows SQLite Test Cleanup Hotfix

## Objective

Fix a Windows-specific SQLite file-lock issue in the v4.0 feature store test suite.

## Fixed

- `PermissionError: [WinError 32]` during `TemporaryDirectory()` cleanup.
- SQLite database file handle remaining open after context-managed DB operations.

## Technical Change

`app/database/db.py` now uses a managed SQLite connection class that closes the database connection when exiting a `with get_connection() as conn:` block. Python's default `sqlite3.Connection` context manager commits or rolls back but does not close the file handle, which can leave temporary test databases locked on Windows.

## Validation

```bash
python -m compileall -q app tests
python -m unittest discover -s tests -v
python -m app.research.research_report
```

Expected result:

```text
Ran 25 tests
OK
```

## Rollback

```bash
git revert <v4.0.1_commit_hash>
git push
```
