import os
import tempfile

# Point the app at an isolated throwaway database before any app import so the
# real (seeded) development database is never touched by tests.
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="paintcan_test_"))
