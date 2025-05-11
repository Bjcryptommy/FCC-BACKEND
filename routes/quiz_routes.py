from flask import Blueprint, request, jsonify
import sqlite3
import os

quiz_bp = Blueprint('quiz', __name__)

# ✅ Use absolute DB path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '../database.db')

def get_db():
    return sqlite3.connect(DB_PATH)

# Add a question
@quiz_bp.route('/questions', methods=['POST'])
def add_question():
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    question_text = data.get('question_text')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO questions (lesson_id, question_text) VALUES (?, ?)",
        (lesson_id, question_text)
    )

    question_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"message": "Question added", "question_id": question_id}), 201

# Add answers to a question
@quiz_bp.route('/answers', methods=['POST'])
def add_answers():
    data = request.get_json()
    question_id = data.get('question_id')
    answers = data.get('answers')  # list of {"text": "...", "is_correct": true/false}

    conn = get_db()
    cursor = conn.cursor()

    correct_answer_id = None

    for answer in answers:
        cursor.execute(
            "INSERT INTO answers (question_id, answer_text) VALUES (?, ?)",
            (question_id, answer['text'])
        )
        answer_id = cursor.lastrowid

        if answer.get('is_correct', False):
            correct_answer_id = answer_id

    if correct_answer_id:
        cursor.execute(
            "UPDATE questions SET correct_answer_id = ? WHERE id = ?",
            (correct_answer_id, question_id)
        )

    conn.commit()
    conn.close()

    return jsonify({"message": "Answers added"}), 201

# Submit Answer
@quiz_bp.route('/submit-answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    username = data.get('username')
    question_id = data.get('question_id')
    selected_answer_id = data.get('answer_id')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_row = cursor.fetchone()
    if not user_row:
        return jsonify({"error": "User not found"}), 404
    user_id = user_row[0]

    cursor.execute("SELECT correct_answer_id FROM questions WHERE id = ?", (question_id,))
    correct_row = cursor.fetchone()
    if not correct_row:
        return jsonify({"error": "Question not found"}), 404
    correct_answer_id = correct_row[0]

    cursor.execute("SELECT attempts, is_correct FROM user_attempts WHERE user_id = ? AND question_id = ?", (user_id, question_id))
    attempt = cursor.fetchone()

    if attempt and attempt[1]:
        return jsonify({"message": "Already answered correctly"}), 200

    if attempt:
        attempts = attempt[0] + 1
        cursor.execute("UPDATE user_attempts SET attempts = ? WHERE user_id = ? AND question_id = ?", (attempts, user_id, question_id))
    else:
        attempts = 1
        cursor.execute("INSERT INTO user_attempts (user_id, question_id, attempts) VALUES (?, ?, ?)", (user_id, question_id, attempts))

    if selected_answer_id == correct_answer_id:
        cursor.execute("UPDATE user_attempts SET is_correct = 1 WHERE user_id = ? AND question_id = ?", (user_id, question_id))

        if attempts == 1:
            points = 10
        elif attempts == 2:
            points = 7
        elif attempts == 3:
            points = 5
        else:
            points = 0

        cursor.execute("UPDATE users SET total_points = total_points + ? WHERE id = ?", (points, user_id))

        conn.commit()
        conn.close()
        return jsonify({"correct": True, "message": "Correct answer!", "points_awarded": points})

    conn.commit()
    conn.close()
    return jsonify({"correct": False, "message": "Incorrect. Try again.", "attempts": attempts})

# Get Answers by Question ID
@quiz_bp.route('/questions/<int:question_id>/answers', methods=['GET'])
def get_answers_for_question(question_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, answer_text FROM answers WHERE question_id = ?", (question_id,))
    rows = cursor.fetchall()
    conn.close()

    answers = [{"id": row[0], "text": row[1]} for row in rows]
    return jsonify(answers)

# ✅ Get Quiz by Lesson ID
@quiz_bp.route('/quiz/<int:lesson_id>', methods=['GET'])
def get_quiz_by_lesson(lesson_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, question_text FROM questions WHERE lesson_id = ?", (lesson_id,))
    questions = cursor.fetchall()

    if not questions:
        conn.close()
        return jsonify([])

    result = []
    for q in questions:
        qid, qtext = q
        cursor.execute("SELECT id, answer_text FROM answers WHERE question_id = ?", (qid,))
        answers = cursor.fetchall()

        result.append({
            "id": qid,
            "question": qtext,
            "answers": [{"id": a[0], "text": a[1]} for a in answers]
        })

    conn.close()
    return jsonify(result)

# Get full progress by username (with lesson titles)
@quiz_bp.route('/user-progress/<username>', methods=['GET'])
def get_user_progress(username):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify([])

    user_id = user[0]

    cursor.execute("""
        SELECT 
            ua.question_id,
            ua.attempts,
            ua.is_correct,
            l.title AS lesson_title
        FROM user_attempts ua
        JOIN questions q ON ua.question_id = q.id
        JOIN lessons l ON q.lesson_id = l.id
        WHERE ua.user_id = ?
    """, (user_id,))
    
    results = cursor.fetchall()
    conn.close()

    data = []
    for row in results:
        data.append({
            "question_id": row[0],
            "attempts": row[1],
            "is_correct": bool(row[2]),
            "lesson_title": row[3]
        })

    return jsonify(data)
