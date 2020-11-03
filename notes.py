import datetime as dt
import sqlite3 as sql

import time

db_conn = sql.connect('data.db')
db = db_conn.cursor()
note_list = []
last_id = 0

#Creating data base
db.execute("""CREATE TABLE IF NOT EXISTS notes(
    note_id INT PRIMARY KEY,
    note_title TEXT,
    note_text TEXT,
    note_timestamp TIMESTAMP); """)
db_conn.commit()

class Note(object):
    """Object Note"""

    def __init__(self, title, text, note_id = -1, timestamp = time.time()):
        super().__init__()
        global last_id

        self.title = title
        self.text = text
        self.timestamp = timestamp

        if note_id == -1:
            self.id = last_id
            last_id += 1
        else:
            self.id = note_id
            last_id = note_id + 1


def create_note(title="New note", text=""):
    """Creating note and save to DB"""
    note = Note(title = title, text = text)
    note_list.append(note)
    save_note(note)

def edit_note(note, title = -1, text = -1):
    """Editing note and save to DB"""
    if title != -1:
        note.title = title
    if text != -1:
        note.text = text
    note.timestamp = time.time()
    save_note(note)

def delete_note(note):
    """Deleting note from everywhere"""
    db.execute(f"DELETE FROM notes WHERE note_id = {note.id}")
    db_conn.commit()
    note_list.remove(note)

def print_notes():
    """Output all notes"""
    for note in note_list:
        if time.time() <= note.timestamp + 86400:
            time_or_date = dt.datetime.fromtimestamp(note.timestamp).strftime('%H:%M')
        else:
            time_or_date = dt.datetime.fromtimestamp(note.timestamp).strftime('%d.%m.%Y')
        print(note.id, note.title, note.text, time_or_date)

def save_note(note):
    """Saving note to DB"""
    db.execute(f"SELECT EXISTS(SELECT note_id FROM notes WHERE note_id = {note.id})")
    note_check, = db.fetchone()
    if note_check == 1:
        db.execute(f"""UPDATE notes SET 
            note_title = '{note.title}', 
            note_text = '{note.text}', 
            note_timestamp = '{note.timestamp}'
            WHERE note_id = '{note.id}'
            """)
    else:
        db.execute(f"""INSERT INTO notes(note_id, note_title, note_text, note_timestamp) 
            VALUES('{note.id}', '{note.title}', '{note.text}', '{note.timestamp}')""")
    db_conn.commit()

def load_notes():
    """Loading notes from DB"""
    global last_id
    if len(note_list) == 0:
        db.execute("SELECT * FROM notes")
        db_note_list = db.fetchall()
        for db_note in db_note_list:
            db_note_id, db_note_title, db_note_text, db_note_timestamp = db_note
            note = Note(title = db_note_title, text = db_note_text, note_id = db_note_id, timestamp = db_note_timestamp)
            note_list.append(note)