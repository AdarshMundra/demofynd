from flask import Flask, render_template, request, redirect, url_for, session
from models import db, SuperAdmin, User, ToDoList

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/fynd'
app.secret_key = 'your_secret_key'  # Change this to a random and secure secret key
db.init_app(app)

@app.route('/')
def index():
    # Implement the index page
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if a superadmin with the provided email exists
        superadmin = SuperAdmin.query.filter_by(Email=email).first()

        if superadmin and superadmin.Password == password:
            # Set the session to store the logged-in user's email and role
            session['email'] = superadmin.Email
            session['role'] = 'superadmin'
            return redirect(url_for('superadmin_dashboard'))

        # Check if a user with the provided email exists
        user = User.query.filter_by(email=email).first()

        if user and user.Password == password:
            # Set the session to store the logged-in user's email and role
            session['email'] = user.email
            session['role'] = 'user'
            return redirect(url_for('user_dashboard'))

        # If no valid user or superadmin found, show an error message
        error_msg = "Invalid email or password. Please try again."
        return render_template('login.html', error_msg=error_msg)

    return render_template('login.html')


@app.route('/superadmin_dashboard')
def superadmin_dashboard():
    if 'email' in session and session['role'] == 'superadmin':
        # Fetch all users and tasks from the database
        users = User.query.all()
        tasks = ToDoList.query.all()

        if request.method == 'POST':
            if 'create_user' in request.form:
                # Handle form data to create a new user
                email = request.form['email']
                firstname = request.form['firstname']
                lastname = request.form['lastname']
                password = request.form['password']

                # Create a new user and save it to the database
                new_user = User(email=email, FirstName=firstname, LastName=lastname, Password=password)
                db.session.add(new_user)
                db.session.commit()
            elif 'create_task' in request.form:
                # Handle form data to create a new task
                user_email = request.form['user_email']
                task_name = request.form['task_name']
                description = request.form['description']

                # Create a new task and save it to the database
                new_task = ToDoList(user_email=user_email, Name=task_name, description=description)
                db.session.add(new_task)
                db.session.commit()

        return render_template('superadmin_dashboard.html', users=users, tasks=tasks)
    else:
        return redirect(url_for('login'))

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'email' in session and session['role'] == 'user':
        # Fetch tasks assigned to the logged-in user from the database
        user_email = session['email']
        user_tasks = ToDoList.query.filter_by(user_email=user_email).all()
        return render_template('user_dashboard.html', tasks=user_tasks)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    return redirect(url_for('login'))
# Add other routes for creating users, tasks, modifying tasks, etc.


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        # Handle form data to create a new user
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']

        # Create a new user and save it to the database
        new_user = User(email=email, FirstName=firstname, LastName=lastname, Password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('superadmin_dashboard'))  # Redirect to superadmin dashboard after user creation

    return render_template('create_user.html')


@app.route('/add_task', methods=['POST'])
def add_task():
    if 'email' in session and session['role'] == 'user':
        if request.method == 'POST':
            # Handle form data to create a new task
            user_email = session['email']
            task_name = request.form['task_name']
            description = request.form['description']

            # Create a new task and save it to the database
            new_task = ToDoList(user_email=user_email, Name=task_name, description=description)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('user_dashboard'))
    elif 'email' in session and session['role'] == 'superadmin':
        if request.method == 'POST':
            # Handle form data to create a new task
            user_email = request.form['userEmail']
            task_name = request.form['task_name']
            description = request.form['description']

            # Create a new task and save it to the database
            new_task = ToDoList(user_email=user_email, Name=task_name, description=description)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('superadmin_dashboard'))




@app.route('/modify_task/<int:task_id>', methods=['GET', 'POST'])
def modify_task(task_id):
    task = ToDoList.query.get(task_id)

    if request.method == 'POST':
        # Handle form data to modify the task
        task.Name = request.form['task_name']
        task.description = request.form['description']
        task.status = request.form['status']
        # Update other task properties as needed

        db.session.commit()
        return redirect(url_for('user_dashboard'))  # Redirect to user dashboard after task modification

    return render_template('modify_task.html', task=task)


if __name__ == '__main__':
    app.run(debug=True)
