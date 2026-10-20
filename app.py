# Flask API for Personal Notes App
# Auth: Session-based login/signup

from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api, Resource
from flask_migrate import Migrate

app = Flask(__name__)

# Configs
app.secret_key = "my_super_secret_key_123"  # change in production later!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# App initializations
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
api = Api(app)



# MODELS
# ----------------------------------------------

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)

    # User can have many notes
    notes = db.relationship('Note', backref='user')

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    category = db.Column(db.String, default="General")  # Added custom field for flavor!
    
    # FK linking note to its owner
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "user_id": self.user_id
        }


# ----------------------------------------------
# AUTH ROUTES
# ----------------------------------------------

class Signup(Resource):
    def post(self):
        req_data = request.get_json() or {}
        username = req_data.get('username')
        password = req_data.get('password')

        # Simple validation
        if not username or not password:
            return {"error": "Both username and password are required!"}, 400

        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {"error": "That username is already taken."}, 422

        # Hash password and create user
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_pw)
        
        db.session.add(new_user)
        db.session.commit()

        # Log in automatically after signup
        session['user_id'] = new_user.id
        return new_user.to_dict(), 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        user = User.query.filter_by(username=data.get('username')).first()

        # Check credentials
        if user and bcrypt.check_password_hash(user.password_hash, data.get('password', '')):
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id', None)
            return {}, 204
        return {"error": "Not logged in"}, 401


class CheckSession(Resource):
    def get(self):
        # Check active session cookie
        current_user_id = session.get('user_id')
        if current_user_id:
            user = User.query.get(current_user_id)
            if user:
                return user.to_dict(), 200
        
        return {"error": "Unauthorized access"}, 401



# NOTES CRUD ROUTES
# ----------------------------------------------

class NoteIndex(Resource):
    def get(self):
        current_user = session.get('user_id')
        if not current_user:
            return {"error identified": "Please log in first!"}, 401

        # Pagination setup (default to page 1, 5 notes per page)
        page_num = request.args.get('page', 1, type=int)
        per_page_num = request.args.get('per_page', 5, type=int)

        # Get only notes for current logged in user
        user_notes = Note.query.filter_by(user_id=current_user).paginate(
            page=page_num, 
            per_page=per_page_num, 
            error_out=False
        )

        return {
            "items": [n.to_dict() for n in user_notes.items],
            "total": user_notes.total,
            "page": user_notes.page,
            "pages": user_notes.pages
        }, 200

    def post(self):
        current_user = session.get('user_id')
        if not current_user:
            return {"error": "Please log in first!"}, 401

        body = request.get_json() or {}
        title = body.get('title')
        content = body.get('content')
        category = body.get('category', 'General')

        if not title or not content:
            return {"error": "Title and content are required fields!"}, 400

        created_note = Note(
            title=title,
            content=content,
            category=category,
            user_id=current_user
        )
        db.session.add(created_note)
        db.session.commit()

        return created_note.to_dict(), 201


class NoteByID(Resource):
    def patch(self, id):
        current_user = session.get('user_id')
        if not current_user:
            return {"error": "Unauthorized"}, 401

        note_item = Note.query.get(id)
        if not note_item:
            return {"error": "Note not found"}, 404

        # Route protection: make sure note belongs to logged in user
        if note_item.user_id != current_user:
            return {"error": "Forbidden: You cannot edit another user's note!"}, 403

        body = request.get_json() or {}
        if 'title' in body:
            note_item.title = body['title']
        if 'content' in body:
            note_item.content = body['content']
        if 'category' in body:
            note_item.category = body['category']

        db.session.commit()
        return note_item.to_dict(), 200

    def delete(self, id):
        current_user = session.get('user_id')
        if not current_user:
            return {"error": "Unauthorized"}, 401

        note_item = Note.query.get(id)
        if not note_item:
            return {"error": "Note not found"}, 404

        # Route protection check
        if note_item.user_id != current_user:
            return {"error": "Forbidden: You cannot delete another user's note!"}, 403

        db.session.delete(note_item)
        db.session.commit()
        return {}, 204


# API Route Registrations
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(NoteIndex, '/notes')
api.add_resource(NoteByID, '/notes/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)