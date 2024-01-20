import datetime
from flask import Flask, make_response, redirect, render_template, request, session, url_for
from requests import Session
"""flask app that uses the user_app for authorization and authentication and loads blueprints for the unique apps"""

SESSION_COOKIE_NAME = "sample_app_session"

client_id = "client_id"
client_secret = "client_secret"
redirect_uri = "http://localhost:5001/login"
scope = "test-scope"

auth_session = Session()
session_storage = {}


def random_string_generator(length):
    import random
    import string
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for i in range(length))


def get_session_data():
    test_cookie = request.cookies.get(SESSION_COOKIE_NAME, None)
    if not test_cookie:
        return None, None
    elif test_cookie == "":
        return None, None
    elif test_cookie in session_storage:
        return session_storage[test_cookie], test_cookie
    else:
        return None, None


def make_session_cookie(data: dict = {}):
    while (key := random_string_generator(64)) in session_storage:
        pass
    session_storage[key] = data
    return key


def response_with_cookie(response, cookie_key=None):
    if not cookie_key or cookie_key not in session_storage:
        cookie_key = make_session_cookie()
    resp = make_response(response)
    resp.set_cookie(SESSION_COOKIE_NAME, cookie_key, expires=datetime.datetime.now() +
                    datetime.timedelta(hours=1), httponly=True, samesite="Strict", secure=False)
    return resp


def response_with_logout_cookie(response):
    resp = make_response(response)
    resp.set_cookie(SESSION_COOKIE_NAME, "", expires=datetime.datetime.now(),
                    httponly=True, samesite="Strict", secure=False)
    return resp


app = Flask(__name__)
app.secret_key = random_string_generator(64)


@app.route("/")
def index():
    session_data, session_cookie = get_session_data()
    if session_data and "name" in session_data:
        return response_with_cookie(render_template("index.html", username=session_data["name"]), session_cookie)
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def login():
    session_data, session_cookie = get_session_data()
    if not session_data:
        session_cookie = make_session_cookie()
        session_data = session_storage[session_cookie]
    # already logged in
    if session_data and "id" in session_data:
        return response_with_cookie(redirect(url_for("index")), session_cookie)
    code = request.args.get("code")
    state = request.args.get("state")
    if code == None or state == None:
        state = random_string_generator(16)
        session_data["state"] = state
        return redirect(f"http://localhost:5000/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}")
    if code and state:
        if session_data and session_data["state"] != state:
            return "invalid state"
    del session_data["state"]
    r = auth_session.post("http://localhost:5000/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    })
    if r.status_code != 200:
        print(r.text)
        return r.text
    session_data["token"] = r.json()["access_token"]

    user_r = auth_session.get("http://localhost:5000/api/user",
                              headers={"Authorization": f"Bearer {session_data["token"]}"})
    session_data["name"] = user_r.json()["name"]
    session_data["email"] = user_r.json()["email"]
    session_data["id"] = user_r.json()["id"]
    return response_with_cookie(redirect(url_for("index")), session_cookie)


@app.route("/logout")
def logout():
    """logout route which should clear the session and redirect to the index page"""
    session_data, session_cookie = get_session_data()
    if session_data and "id" in session_data:
        del session_storage[session_cookie]
    return response_with_logout_cookie(redirect(url_for("index")))


@app.route("/user")
def user():
    """user page which should return the name and email of the user if logged in"""
    session_data, session_cookie = get_session_data()
    if session_data and "id" in session_data:
        return response_with_cookie(render_template("user.html", username=session_data["name"], email=session_data["email"]), session_cookie)

    return redirect(url_for("login"))


@app.teardown_appcontext
def shutdown_session(exception=None):
    pass


if __name__ == "__main__":
    app.run(port=5001)
