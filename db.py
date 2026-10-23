"""SQLite storage: user accounts and each owner's bills. 'u:<id>' = account, 'g:<token>' = guest."""
import json
import sqlite3
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL DEFAULT '',
  pw_hash TEXT NOT NULL, created_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS datasets(
  owner TEXT PRIMARY KEY, source TEXT NOT NULL, sample INTEGER NOT NULL DEFAULT 0, updated_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS bills(
  owner TEXT NOT NULL, month TEXT NOT NULL, units REAL NOT NULL, amount REAL NOT NULL, ap TEXT,
  PRIMARY KEY(owner, month));
"""


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(path):
    conn = connect(path)
    with conn:
        conn.executescript(SCHEMA)
    conn.close()


# ---- users -------------------------------------------------------------------------------------
def create_user(conn, email, name, pw_hash):
    with conn:
        cur = conn.execute("INSERT INTO users(email,name,pw_hash,created_at) VALUES(?,?,?,?)",
                           (email, name, pw_hash, int(time.time())))
    return cur.lastrowid


def find_user(conn, email):
    return conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()


def get_user(conn, user_id):
    return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()


# ---- bills -------------------------------------------------------------------------------------
def dataset(conn, owner):
    row = conn.execute("SELECT source, sample FROM datasets WHERE owner=?", (owner,)).fetchone()
    return {"source": row["source"], "sample": bool(row["sample"])} if row else None


def load_rows(conn, owner):
    out = []
    for r in conn.execute("SELECT month, units, amount, ap FROM bills WHERE owner=? ORDER BY month", (owner,)):
        out.append({"m": r["month"], "u": r["units"], "a": r["amount"], "ap": json.loads(r["ap"]) if r["ap"] else None})
    return out


def _touch(conn, owner, source, sample):
    conn.execute("INSERT INTO datasets(owner,source,sample,updated_at) VALUES(?,?,?,?) "
                 "ON CONFLICT(owner) DO UPDATE SET source=excluded.source, sample=excluded.sample, "
                 "updated_at=excluded.updated_at", (owner, source, int(sample), int(time.time())))


def replace_rows(conn, owner, rows, source, sample=False):
    with conn:
        conn.execute("DELETE FROM bills WHERE owner=?", (owner,))
        conn.executemany("INSERT INTO bills(owner,month,units,amount,ap) VALUES(?,?,?,?,?)",
                         [(owner, r["m"], r["u"], r["a"], json.dumps(r["ap"]) if r["ap"] else None) for r in rows])
        _touch(conn, owner, source, sample)


def upsert_row(conn, owner, row, source):
    """Add or update one month. Typing the first bill replaces the sample data. Returns the month count."""
    current = dataset(conn, owner)
    with conn:
        if current is None or current["sample"]:
            conn.execute("DELETE FROM bills WHERE owner=?", (owner,))
        conn.execute("INSERT INTO bills(owner,month,units,amount,ap) VALUES(?,?,?,?,?) "
                     "ON CONFLICT(owner,month) DO UPDATE SET units=excluded.units, amount=excluded.amount, ap=excluded.ap",
                     (owner, row["m"], row["u"], row["a"], json.dumps(row["ap"]) if row["ap"] else None))
        _touch(conn, owner, source, False)
    return conn.execute("SELECT COUNT(*) FROM bills WHERE owner=?", (owner,)).fetchone()[0]


def move_dataset(conn, src, dst):
    """Give a guest's data to the account they just logged into (only if the account has none yet)."""
    if dataset(conn, src) is None or dataset(conn, dst) is not None:
        return
    with conn:
        conn.execute("UPDATE bills SET owner=? WHERE owner=?", (dst, src))
        conn.execute("UPDATE datasets SET owner=? WHERE owner=?", (dst, src))


def purge_guests(conn, older_than_seconds):
    cutoff = int(time.time()) - older_than_seconds
    with conn:
        conn.execute("DELETE FROM datasets WHERE owner LIKE 'g:%' AND updated_at<?", (cutoff,))
        conn.execute("DELETE FROM bills WHERE owner LIKE 'g:%' AND owner NOT IN (SELECT owner FROM datasets)")
