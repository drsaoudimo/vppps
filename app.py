

from flask import Flask, request, redirect, render_template, url_for
import random
import string
import sqlite3
import os

app = Flask(name)

Create database if it doesn't exist

DB_NAME = 'urls.db'
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS urls (
id INTEGER PRIMARY KEY AUTOINCREMENT,
short_code TEXT UNIQUE,
long_url TEXT
)
''')
conn.commit()

Function to generate short code

def generate_short_code(length=6):
return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

Home page to submit URL

@app.route('/', methods=['GET', 'POST'])
def home():
if request.method == 'POST':
long_url = request.form['long_url'].strip()

# Validate URL  
    if not (long_url.startswith("http://") or long_url.startswith("https://")):  
        long_url = "http://" + long_url  

    short_code = generate_short_code()  

    # Save to DB  
    try:  
        c.execute('INSERT INTO urls (short_code, long_url) VALUES (?, ?)', (short_code, long_url))  
        conn.commit()  
    except sqlite3.IntegrityError:  
        # In rare case code already exists  
        short_code = generate_short_code()  
        c.execute('INSERT INTO urls (short_code, long_url) VALUES (?, ?)', (short_code, long_url))  
        conn.commit()  

    short_url = request.host_url + short_code  
    return render_template('index.html', short_url=short_url)  

return render_template('index.html', short_url=None)

Redirect route

@app.route('/<short_code>')
def redirect_short_url(short_code):
c.execute('SELECT long_url FROM urls WHERE short_code = ?', (short_code,))
result = c.fetchone()
if result:
return redirect(result[0])
return 'URL not found', 404

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8888))
    app.run(host="0.0.0.0", port=port)
