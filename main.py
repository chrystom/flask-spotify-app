import os, requests
from flask import Flask, request, redirect, render_template, session
from flask_session import Session
from urllib.parse import quote

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.

# init flask app
app = Flask(__name__)

# config session
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

#  Client Keys
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Spotify URLS
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = f"{SPOTIFY_API_BASE_URL}/{API_VERSION}"

# Server-side Parameters
CLIENT_SIDE_URL = "https://test-spotify-app.chrystom.repl.co"
PORT = 8080
REDIRECT_URI = "{}/callback".format(CLIENT_SIDE_URL)
SCOPE = "user-read-currently-playing"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

# dict of query string for login route
auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login")
def login():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = f"https://accounts.spotify.com/authorize/?{url_args}"
    return redirect(auth_url)


@app.route("/callback")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    code = request.args.get('code')

    # make sure we get a code
    if not code:
        return 'no auth code'

    # request for auth tokens and stuff
    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": str(code),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    # Auth Step 5: Tokens are Returned to Application
    response_data = response.json()
    
    try:
        session['access_token'] = response_data["access_token"]
        session['refresh_token'] = response_data["refresh_token"]
        session['token_type'] = response_data["token_type"]
        expires_in = response_data["expires_in"]
    except KeyError:
        return 'Error while requesting tokens'

    # at this point, we have sucessfully got our tokens

    # go to index, this time since we have a token, it works
    return redirect('/')




@app.route("/profile")
def profile():
    # make sure we have a access_token
    if 'access_token' not in session:
        return redirect('/login')
    return render_template('profile.html')




    
@app.route("/current_song")
def current_song():
    # make sure we have a access_token
    if 'access_token' not in session:
        return redirect('/login')
    return render_template('current_song.html')

app.run('0.0.0.0', port=PORT)