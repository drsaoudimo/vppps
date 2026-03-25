from flask import Flask, request, redirect, render_template_string
import random
import string
import sqlite3
import os

app = Flask(__name__)

# ------------------ Database ------------------
DB_NAME = "urls.db"
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT UNIQUE,
    long_url TEXT
)
""")
conn.commit()

# ------------------ Short code ------------------
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ------------------ HTML (no external files) ------------------
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

# ------------------ Routes ------------------
@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None

    if request.method == "POST":
        long_url = request.form["long_url"].strip()

        if not long_url.startswith(("http://", "https://")):
            long_url = "http://" + long_url

        short_code = generate_short_code()

        try:
            c.execute(
                "INSERT INTO urls (short_code, long_url) VALUES (?, ?)",
                (short_code, long_url),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass

        short_url = request.host_url + short_code

    return render_template_string(HTML, short_url=short_url)


@app.route("/<short_code>")
def redirect_short(short_code):
    c.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()

    if result:
        return redirect(result[0])

    return "URL not found", 404


# ------------------ IMPORTANT FOR BINDER ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8888))
    app.run(host="0.0.0.0", port=port)
