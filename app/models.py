from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.Text, default='')
    role_title = db.Column(db.String(100), default='Developer')
    github_url = db.Column(db.String(200), default='')
    avatar_url = db.Column(db.String(300), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='author', lazy='dynamic',
                               foreign_keys='Project.user_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    hand_raises = db.relationship('HandRaise', backref='requester', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    __tablename__ = 'projects'

    STAGES = [
        ('planning', 'Planning'),
        ('building', 'Building'),
        ('testing', 'Testing'),
        ('done', 'Done'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    stage = db.Column(db.String(20), nullable=False, default='planning')
    support_needed = db.Column(db.Text, default='')
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    milestones = db.relationship('Milestone', backref='project', lazy='dynamic',
                                 cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='project', lazy='dynamic',
                               cascade='all, delete-orphan')
    hand_raises = db.relationship('HandRaise', backref='project', lazy='dynamic',
                                  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.title}>'


class Milestone(db.Model):
    __tablename__ = 'milestones'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default='')
    achieved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    def __repr__(self):
        return f'<Milestone {self.title}>'


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'


class HandRaise(db.Model):
    __tablename__ = 'hand_raises'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='pending')  # pending / accepted / declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    def __repr__(self):
        return f'<HandRaise {self.id}>'


class CollabMessage(db.Model):
    __tablename__ = 'collab_messages'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    author = db.relationship('User', backref='collab_messages')
    project = db.relationship('Project', backref=db.backref('collab_messages', lazy='dynamic',
                              cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<CollabMessage {self.id}>'
