import re
import sqlite3
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

#База данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS pages
(id INTEGER PRIMARY KEY AUTOINCREMENT,
url TEXT NOT NULL,
count INTEGER NOT NULL DEFAULT 0)''')
conn.commit()

#Страницы
def add_page(url):
cursor.execute('INSERT INTO pages(url) VALUES (?)', (url,))
conn.commit()

# Поиск инфы
def search_page(url, query):
response = requests.get(url)
if response.status_code == 200:
content = response.text
count = len(re.findall(query, content))
cursor.execute('UPDATE pages SET count=? WHERE url=?', (count, url))
conn.commit()

# Результат
def get_results(query):
cursor.execute('SELECT url, count FROM pages WHERE url LIKE ?', ('%' + query + '%',))
results = cursor.fetchall()
return sorted(results, key=lambda x: x[1], reverse=True)

# Обработка
@app.route('/')
def index():
return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
url = request.form['url']
add_page(url)
return 'OK'

@app.route('/search', methods=['POST'])
def search():
query = request.form['query']
cursor.execute('SELECT * FROM pages')
pages = cursor.fetchall()
for page in pages:
search_page(page[1], query)
results = get_results(query)
return render_template('results.html', results=results)

@app.route('/clear')
def clear():
cursor.execute('DELETE FROM pages')
conn.commit()
return 'OK'

if __name__ == '__main__':
app.run(debug=True)