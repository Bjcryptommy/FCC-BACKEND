from flask import Blueprint, request, jsonify
import sqlite3

# Set prefix here so endpoints become: /comments/...
comment_bp = Blueprint('comments', __name__, url_prefix='/comments')

def get_db():
    return sqlite3.connect('backend/database.db')

# 🔧 Create Comments Table
def create_comment_table():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER,
            username TEXT,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        )
    ''')
    conn.commit()
    conn.close()

create_comment_table()

# 📥 POST a Comment - POST /comments
@comment_bp.route('', methods=['POST'])
def post_comment():
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    username = data.get('username')
    text = data.get('text')  # 🟢 Must match frontend key

    if not lesson_id or not username or not text:
        return jsonify({"error": "Missing lesson_id, username, or text"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comments (lesson_id, username, text) VALUES (?, ?, ?)",
        (lesson_id, username, text)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Comment added successfully"}), 201

# 📤 GET Comments for a Lesson - GET /comments/<lesson_id>
@comment_bp.route('/<int:lesson_id>', methods=['GET'])
def get_comments(lesson_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, text, timestamp FROM comments WHERE lesson_id = ? ORDER BY timestamp DESC",
        (lesson_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    comments = [{
        "username": row[0],
        "text": row[1],
        "timestamp": row[2]
    } for row in rows]

    return jsonify(comments)
