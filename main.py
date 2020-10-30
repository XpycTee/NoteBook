import datetime as dt
import sqlite3 as sql

db_conn = sql.connect('data.db')
db = db_conn.cursor()
note_list = []
last_id = 0


class Note(object):
    """Object Note"""
    def __init__(self, title, text):
        super().__init__()
        global last_id
        self.title = title
        self.text = text
        date_time = dt.datetime.now()
        self.date = date_time.strftime('%d-%m-%Y')
        self.time = date_time.strftime('%H:%M')
        self.id = last_id
        last_id += 1


def create_note(title="New note", text=""):
    """Function of create note"""
    note = Note(title, text)
    note_list.append(note)

def print_notes():
    for note in note_list:
        if dt.datetime.now().strftime('%d-%m-%Y') == note.date:
            time_or_date = note.time
        else:
            time_or_date = note.date
        print(note.id, note.title, note.text, time_or_date)

def save_note(note):
    db.execute(f"""INSERT INTO notes(
        note_id, note_title, note_text, 
        note_date, note_time) 
        VALUES(
        `{note.id}`, `{note.title}`, `{note.text}`, 
        `{note.date}`, `{note.time}`)""")
    db.execute(f"SELECT EXISTS(SELECT note_id FROM notes WHERE note_id = {note.id})")
    print(db.fetchone())
    if True:
        pass

def load_notes():
    pass

db.execute("""CREATE TABLE IF NOT EXISTS notes(
    note_id INT PRIMARY KEY,
    note_title TEXT,
    note_text TEXT,
    note_date DATE,
    note_time TIME); """)
db_conn.commit()