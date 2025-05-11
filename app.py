from flask import Flask
from models import create_tables
from routes.auth_routes import auth_bp
from routes.course_routes import course_bp
from routes.quiz_routes import quiz_bp
from flask_cors import CORS
from routes.comment_routes import comment_bp



app = Flask(__name__)
app.secret_key = 'secret123'
CORS(app) 

create_tables()

app.register_blueprint(comment_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(course_bp)
app.register_blueprint(quiz_bp)

@app.route('/')
def home():
    return "FCC Clone Backend Running!"

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
