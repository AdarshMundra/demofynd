from flask import Flask, render_template, request, redirect, url_for, session
from models import db, SuperAdmin, User, ToDoList
import logging

# Set up logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
app = Flask(__name__, static_folder='static')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/fynd'
# app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI']= "mysql://admin:IvkDQNtk80HUW5l40v6A@databasetest.cl4pduwjhwak.us-east-1.rds.amazonaws.com:3306/fynd"
# app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#
app.secret_key = 'your_secret_key'  # Change this to a random and secure secret key



db.init_app(app)


@app.route('/')
def index():
    # Implement the index page
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        print(email)
        print(password)
        # Check if a superadmin with the provided email exists
        superadmin = SuperAdmin.query.filter_by(Email=email).first()
        print(superadmin)
        if superadmin and superadmin.Password == password:
            # Set the session to store the logged-in user's email and role
            session['email'] = superadmin.Email
            session['role'] = 'superadmin'
            session['name'] = superadmin.FirstName
            logging.info(f"Superadmin login: {superadmin.FirstName}")

            return redirect(url_for('superadmin_dashboard'))

        # Check if a user with the provided email exists
        user = User.query.filter_by(email=email).first()

        if user and user.Password == password:
            # Set the session to store the logged-in user's email and role
            session['email'] = user.email
            session['role'] = 'user'
            session['name'] = user.FirstName
            logging.info(f"Superadmin login: {user.FirstName}")
            return redirect(url_for('user_dashboard'))

        # If no valid user or superadmin found, show an error message
        error_msg = "Invalid email or password. Please try again."
        return render_template('login.html', error_msg=error_msg)

    return render_template('login.html')


@app.route('/user_management')
def user_management():
    if 'email' in session and session['role'] == 'superadmin':
        users = User.query.all()
        logging.info(f"Superadmin click: user management")
        return render_template('user_management.html', users=users)
    else:
        return redirect(url_for('login'))


@app.route('/task_management')
def task_management():
    if 'email' in session and session['role'] == 'superadmin':
        tasks = ToDoList.query.all()
        logging.info(f"Superadmin click: task management")
        return render_template('task_management.html', tasks=tasks)  # , tasks=tasks)
    elif 'email' in session and session['role'] == 'user':
        tasks = ToDoList.query.filter_by(user_email=session['email']).all()
        logging.info(f"User click: task management")
        return render_template('task_management.html', tasks=tasks)

    else:
        return redirect(url_for('login'))


@app.route('/superadmin_dashboard')
def superadmin_dashboard():
    if 'email' in session and session['role'] == 'superadmin':
        logging.info(f"Superadmin login ")
        log_entries = []
        with open('app.log', 'r') as log_file:
            log_entries = log_file.readlines()

        return render_template('superadmin_dashboard.html', log_entries=log_entries, username=session['name'])
    else:
        return redirect(url_for('login'))


@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'email' in session and session['role'] == 'user':
        # Fetch tasks assigned to the logged-in user from the database
        log_entries = []
        with open('app.log', 'r') as log_file:
            log_entries = log_file.readlines()

        return render_template('user_dashboard.html', log_entries=log_entries, username=session['name'])
    else:
        return redirect(url_for('login'))


@app.route('/user_task_list/<string:user_email>')
def user_task_list(user_email):
    print(user_email)
    if 'email' in session and session['role'] == 'superadmin':
        user_tasks = ToDoList.query.filter_by(user_email=user_email).all()
        logging.info(f"user click: on task list")
        return render_template('task_management.html', tasks=user_tasks)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    # Clear the session to log out the user
    logging.info(f"logout")
    session.clear()
    return redirect(url_for('login'))




@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        # Handle form data to create a new user
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        super_email = session['email']
        # Create a new user and save it to the database
        new_user = User(email=email, FirstName=firstname, LastName=lastname, Password=password,
                        super_email= super_email, role = 'user')
        db.session.add(new_user)
        db.session.commit()
        logging.info(f"SuperAdmin create a new user")
        return redirect(url_for('superadmin_dashboard'))  # Redirect to superadmin dashboard after user creation

    return render_template('create_user.html')


@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if 'email' in session and session['role'] == 'user':
        if request.method == 'POST':
            # Handle form data to create a new task
            user_email = session['email']
            task_name = request.form['task_name']
            description = request.form['description']
            start_time = request.form['start time']
            end_time = request.form['end time']

            # Create a new task and save it to the database
            new_task = ToDoList(user_email=user_email, Name=task_name, description=description, start_date=start_time,
                                end_date=end_time)
            logging.info(f"User create a new task")

            db.session.add(new_task)
            db.session.commit()

            return redirect(url_for('task_management'))
        else:
            logging.info(f"User create task")

            return render_template('create_task.html')
    elif 'email' in session and session['role'] == 'superadmin':
        if request.method == 'POST':
            # Handle form data to create a new task
            print(request.form)
            user_email = request.form['user_email']
            task_name = request.form['task_name']
            description = request.form['description']
            start_time = request.form['start time']
            end_time = request.form['end time']

            # Create a new task and save it to the database
            new_task = ToDoList(user_email=user_email, Name=task_name, description=description, start_date=start_time,
                                end_date=end_time)
            db.session.add(new_task)
            db.session.commit()
            logging.info(f"SuperAdmin create a new task")

            return redirect(url_for('task_management'))
        else:
            logging.info(f"User create a task")

            return render_template('create_task.html')


@app.route('/modify_task/<int:task_id>', methods=['GET', 'POST'])
def modify_task(task_id):
    task = ToDoList.query.get(task_id)

    if request.method == 'POST':
        # Handle form data to modify the task
        task.Name = request.form['task_name']
        task.description = request.form['description']
        task.status = request.form['status']
        task.start_date = request.form['start time']
        task.end_date = request.form['end time']

        # Update other task properties as needed

        db.session.commit()
        logging.info(f"modify the existing task")

        return redirect(url_for('task_management')) # Redirect to user dashboard after task modification

    return render_template('modify_task.html', task=task)


@app.route('/task_management/<int:task_id>')
def delete_task(task_id):
    print(task_id)
    task = ToDoList.query.filter_by(unique_id=task_id).first()
    print(task.user_email)
    if task:
        # print("Hello")
        # new_task = AchiveToDoList(user_email=task.user_email, Name=task.Name, description=task.description, start_date=task.start_date,
        #                     end_date=task.end_date)
        # db.session.add(new_task)
        # db.session.commit()
        db.session.delete(task)
        db.session.commit()
        logging.info(f"delete the task")

        return redirect(url_for('task_management'))
    else:
        logging.info(f"not delete the task")
        return redirect(url_for('task_management'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    # app.run(debug=True)