from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, name, body):
        self.name = name
        self.body = body

@app.route('/', methods=['GET'])
def index():

    tasks = Blog.query.all()
    return render_template('blog.html',title="Build a Blog!", 
        tasks=tasks)

@app.route('/blog', methods=['GET'])
def index2():
    tasks = Blog.query.all()
    return render_template('blog.html',title="Build a Blog!", 
        tasks=tasks)



@app.route('/newpost', methods=['POST', 'GET'])
def index3():
    if request.method == 'POST':
        blog_title = request.form['entry_title']
        blog_body = request.form['body']

        title_error = ""
        body_error = ""
        
        if not blog_title:
            title_error = "A title is required"
        if not blog_body:
            body_error = "Blog content is required"
        if title_error or body_error:
            return render_template('newpost.html', entry_title = blog_title, title_error_render = title_error,
            body = blog_body, body_error_render = body_error)

        new_post = Blog(blog_title, blog_body)
        db.session.add(new_post)
        db.session.commit()
        id = db.engine.execute('select count(id) from blog').scalar()
        return redirect(url_for('.index4', id = id))

    return render_template('newpost.html', title = "Add a new blog entry", entry_title = "", body = "")

@app.route('/blog?id=<id>', methods=['GET'])
def index4(id):
    
    post = Blog.query.filter_by(id=int(id))
    
    return render_template('entry.html', tasks=post)

if __name__ == '__main__':    
    app.run()
