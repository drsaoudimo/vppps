# Install required packages
!pip install flask flask-ngrok

from flask import Flask, request, redirect, render_template_string
from flask_ngrok import run_with_ngrok
import random, string, sqlite3

app = Flask(__name__)
run_with_ngrok(app)  # Important for Binder

# Create database
conn = sqlite3.connect("urls.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT UNIQUE,
    long_url TEXT
)
""")
conn.commit()

# Generate short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Simple HTML template (no external file needed)
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>URL Shortener</title>
</head>
<body>
    <h2>URL Shortener</h2>
    <form method="POST">
        <input type="text" name="long_url" placeholder="Enter URL" required>
        <button type="submit">Shorten</button>
    </form>

    {% if short_url %}
        <p>Short URL: <a href="{{ short_url }}">{{ short_url }}</a></p>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET','POST'])
def home():
    short_url = None

    if request.method == 'POST':
        long_url = request.form['long_url']

        if not long_url.startswith(("http://","https://")):
            long_url = "http://" + long_url

        short_code = generate_short_code()

        c.execute("INSERT INTO urls (short_code,long_url) VALUES (?,?)",
                  (short_code,long_url))
        conn.commit()

        short_url = request.host_url + short_code

    return render_template_string(HTML, short_url=short_url)

@app.route('/<code>')
def redirect_code(code):
    c.execute("SELECT long_url FROM urls WHERE short_code=?",(code,))
    r = c.fetchone()
    if r:
        return redirect(r[0])
    return "Not found",404


app.run()
