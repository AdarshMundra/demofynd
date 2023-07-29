from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SuperAdmin(db.Model):
    __tablename__ = 'superadmin'
    Email = db.Column(db.String(255), primary_key=True)
    LastName = db.Column(db.String(255))
    FirstName = db.Column(db.String(255))
    Password = db.Column(db.String(255))
    role = db.Column(db.String(50), default='superadmin')
    # Add any other SuperAdmin-specific columns if needed

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True)
    super_email = db.Column(db.String(255), db.ForeignKey('superadmin.Email'))
    LastName = db.Column(db.String(255))
    FirstName = db.Column(db.String(255))
    Password = db.Column(db.String(255))
    role = db.Column(db.String(50), default='user')
    # Add any other User-specific columns if needed

class ToDoList(db.Model):
    __tablename__ = 'todolist'
    unique_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(255), db.ForeignKey('user.email'))
    Name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    description = db.Column(db.Text)
    update_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
