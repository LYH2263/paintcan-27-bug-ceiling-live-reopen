import sqlite3

WALL_COVERAGE_KEY = "coverage"
WALL_COATS_KEY = "coats"
CEILING_COVERAGE_KEY = "ceiling_coverage"
CEILING_COATS_KEY = "ceiling_coats"

# Fallbacks used when a setting row is missing (e.g. a database seeded before
# the ceiling module existed).
DEFAULT_WALL_COVERAGE = 8.0
DEFAULT_WALL_COATS = 2
DEFAULT_CEILING_COVERAGE = 8.0
DEFAULT_CEILING_COATS = 2


def get_map(conn):
    return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}


def coverage_coats(conn):
    m = get_map(conn)
    return (
        float(m.get(WALL_COVERAGE_KEY, DEFAULT_WALL_COVERAGE)),
        int(m.get(WALL_COATS_KEY, DEFAULT_WALL_COATS)),
    )


def ceiling_coverage_coats(conn):
    m = get_map(conn)
    return (
        float(m.get(CEILING_COVERAGE_KEY, DEFAULT_CEILING_COVERAGE)),
        int(m.get(CEILING_COATS_KEY, DEFAULT_CEILING_COATS)),
    )


def upsert(conn, key, value):
    conn.execute(
        "INSERT INTO settings(key,value) VALUES (?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )
    conn.commit()
