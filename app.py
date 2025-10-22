from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    recipes = conn.execute('SELECT * FROM recipes ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', recipes=recipes)

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        
        filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        conn = get_db_connection()
        conn.execute('INSERT INTO recipes (title, category, ingredients, instructions, image) VALUES (?, ?, ?, ?, ?)',
                     (title, category, ingredients, instructions, filename))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_recipe.html')

@app.route('/recipe/<int:id>')
def view_recipe(id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if recipe is None:
        return redirect(url_for('index'))
    
    return render_template('view_recipe.html', recipe=recipe)

@app.route('/delete/<int:id>', methods=('POST',))
def delete_recipe(id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    
    if recipe and recipe['image']:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], recipe['image'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    conn.execute('DELETE FROM recipes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
