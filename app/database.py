import sqlite3
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'], timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    get_db().execute('''CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        name TEXT NOT NULL, contact TEXT NOT NULL, car_model TEXT NOT NULL,
        message TEXT NOT NULL, configuration TEXT NOT NULL, cart TEXT NOT NULL, total INTEGER NOT NULL)''')
    get_db().commit()

def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
