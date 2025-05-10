# backend/models.py

import sqlite3

def create_tables():
    conn = sqlite3.connect('backend/database.db')
    c = conn.cursor()

    # ✅ USERS table with full_name included
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        full_name TEXT,
        password TEXT,
        role TEXT DEFAULT 'student',
        total_points INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        language TEXT DEFAULT 'General'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT,
        video_url TEXT,
        lesson_text TEXT,
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_id INTEGER,
        question_text TEXT,
        correct_answer_id INTEGER,
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        answer_text TEXT,
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_progress (
        user_id INTEGER,
        lesson_id INTEGER,
        is_completed BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_points (
        user_id INTEGER,
        lesson_id INTEGER,
        points INTEGER,
        badge TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_attempts (
        user_id INTEGER,
        question_id INTEGER,
        attempts INTEGER DEFAULT 0,
        is_correct BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )''')

    conn.commit()
    conn.close()

create_tables()
