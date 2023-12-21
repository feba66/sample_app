from flask import Flask, redirect, render_template, request, session, url_for

"""flask app that uses the userstore to register and login users, and stores the user id in the session"""

client_id = "client_id"
client_secret = "client_secret"
redirect_uri = "http://localhost:5001/"
scope = "test-scope"


def random_string_generator(length):
    import random
    import string
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


app = Flask(__name__)
app.secret_key = random_string_generator(64)

try:
    with open('pepper.txt', 'r') as f:
        pepper = f.read()
except FileNotFoundError:
    pepper = random_string_generator(64)
    with open('pepper.txt', 'w') as f:
        f.write(pepper)


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     """register page which should return a form to register"""
#     if request.method == 'POST':
#         name = request.form.get('username')
#         password = request.form.get('password')
#         email = request.form.get('email')
#         user = userstore.register_user(name, password, email)
#         if isinstance(user, str):
#             return render_template('register.html', error=user)
#         session['user_id'] = user.id
#         session['user_name'] = user.name
#         return redirect(url_for('index'))
#     else:
#         return render_template('register.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """login page which should return a form to login"""
#     if request.method == 'POST':
#         name = request.form.get('username')
#         password = request.form.get('password')

#         user = userstore.login_user(name, password)
#         if isinstance(user, str):
#             return render_template('login.html', error=user)
#         session['user_id'] = user.id
#         session['user_name'] = user.name
#         return redirect(url_for('index'))
#     else:
#         return render_template('login.html')


# @app.route('/logout')
# def logout():
#     """logout route which should clear the session and redirect to the index page"""
#     session.clear()
#     return redirect(url_for('index'))


# @app.route("/delete")
# def delete():
#     """ delete user route which should delete the user from the userstore and redirect to the index page"""
#     user_id = session['user_id']
#     if user_id is None:
#         return redirect(url_for('index'))
#     userstore.delete_user(user_id)
#     session.clear()
#     return redirect(url_for('index'))


# @app.route('/user')
# def user():
#     """user page which should return the name and email of the user if logged in"""
#     user_id = session.get('user_id')
#     user = userstore.get_user(user_id)

#     return render_template('user.html', username=user.name if user else None, email=user.email if user else None)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    state = random_string_generator(16)
    session['state'] = state
    return redirect(f"http://localhost:5000/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}")


@app.teardown_appcontext
def shutdown_session(exception=None):
    pass


if __name__ == '__main__':
    app.run(port=5001)
