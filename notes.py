import datetime as dt
import sqlite3 as sql

import time
import asyncio

db_conn = sql.connect('data.db')
db = db_conn.cursor()
note_list = []
last_id = 0


class Notify:
    """Notification of Note"""

    def __init__(self, text, call_time):
        super().__init__()
        self.text = text
        self.call_time = call_time


class Note:
    """Note"""

    def __init__(self, title, text, note_id=-1, timestamp=time.time()):
        super().__init__()
        global last_id

        self.title = title
        self.text = text
        self.timestamp = timestamp

        self.notify = False

        if note_id == -1:
            self.id = last_id
            last_id += 1
        else:
            self.id = note_id
            last_id = note_id + 1


def create_notify(note, text, call_time):
    """Create notification for note"""
    note.notify = Notify(text, call_time)


def create_note(title="New note", text=""):
    """Creating note and save to DB"""
    note = Note(title=title, text=text)
    note_list.append(note)
    save_note(note)


def edit_note(note, title=None, text=None, notify=False):
    """Editing note and save to DB"""
    if title is not None:
        note.title = title
    if text is not None:
        note.text = text

    note.notify = notify
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
            note = Note(title=db_note_title, text=db_note_text, note_id=db_note_id, timestamp=db_note_timestamp)
            note_list.append(note)


async def check_notify_time():
    """Check time in notifications and send alert"""
    while True:
        for note in note_list:
            if note.notify is not False:
                if note.notify.call_time <= time.time():
                    print(note.notify.text, note.notify.call_time, time.time())
                    note.notify = False  # Проблема пропавшего уведомления лучше будет сделать отделбную пременную для определения что уведомление получено и даже сейчас я нарушил PEP8
        await asyncio.sleep(1)


if __name__ == '__main__':
    # Creating data base
    db.execute("""CREATE TABLE IF NOT EXISTS notes(
        note_id INT PRIMARY KEY,
        note_title TEXT,
        note_text TEXT,
        note_timestamp TIMESTAMP); """)
    db_conn.commit()

    load_notes()

    create_notify(note_list[0], "Test notification", time.time() + 10)
    print(f"Note created in {time.time()}")

    ioloop = asyncio.get_event_loop()
    tasks = [
        ioloop.create_task(check_notify_time())
    ]
    ioloop.run_until_complete(asyncio.wait(tasks))
    # ioloop.close()
