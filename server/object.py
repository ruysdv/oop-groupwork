import sqlite3
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.abab")
FILES_DIR = os.path.join(BASE_DIR, "objects")
USER_PATH = os.path.join(BASE_DIR,"user.data")
#DATA_PATH = "data.abab"
#FILES_DIR = "objects"
#print(DATA_PATH)

def _connect():
    x=sqlite3.connect(DATA_PATH)
    x.row_factory=sqlite3.Row
    return x

def _cuser():
    x=sqlite3.connect(USER_PATH)
    x.row_factory=sqlite3.Row
    return x

def _data():
    x=_connect()
    os.makedirs(FILES_DIR, exist_ok=True)
    x.execute("""
        CREATE TABLE IF NOT EXISTS objects (
            id              INTEGER PRIMARY KEY,
            title           TEXT NOT NULL,
            zuozhe          TEXT NOT NULL,
            introduction    TEXT NOT NULL,
            download_sum    INTEGER DEFAULT 0,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    x.commit()
    x.close()

def _users():
    x=_cuser()
    x.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            password    TEXT NOT NULL,
            power       INTEGER DEFAULT 0
        )
    """)
    x.commit()
    x.close()

def _tokens():
    x=_cuser()
    x.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            token       TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            create_time INTEGER NOT NULL
        )
    """)
    x.commit()
    x.close()