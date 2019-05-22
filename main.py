from flask import Flask, request, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from hash import pwd_hash, check_pwd_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'lkjkjhjgljgklh'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, email, password):
        self.email = email
        self.pw_hash = pwd_hash(password)

    def __repr__(self):
        return '<User %r>' % self.email

class Blog(db.Model):

    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.name

@app.route('/', methods=['GET'])
def index():
    owner = User.query.all()
    return render_template('index.html',title="Home!", 
        users=owner)

@app.route('/user?id=<id>', methods=['GET'])
def user_posts(id):
    
    owner= User.query.filter_by(id=int(id)).first()
    tasks = Blog.query.filter_by(owner_id=int(id)).all()
    return render_template('singleUser.html',title="Build a Blog!", 
        tasks=tasks, user=owner)

@app.route('/blog', methods=['GET'])
def show_all_entries():
    
    tasks = Blog.query.all()
    
    return render_template('blog.html',title="Blogz!", 
        tasks=tasks)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
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
        owner = User.query.filter_by(email=session['email']).first()
        new_post = Blog(blog_title, blog_body, owner)
        db.session.add(new_post)
        db.session.commit()
        id = db.engine.execute('select count(id) from blog').scalar()
        return redirect(url_for('.blog_posts', id = id))

    return render_template('newpost.html', title = "Add a new blog entry", entry_title = "", body = "")

@app.route('/blog?id=<id>', methods=['GET'])
def blog_post(id):
    
    post = Blog.query.filter_by(id=int(id))
    
    return render_template('entry.html', tasks=post)


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'show_all_entries']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


logged_in = False
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not email:
            flash("An email is required", 'error')
        if email:
            if len(email) < 3 or len(email) > 20:
                flash("Email must be at least 3 and less than 20 characters long", 'error')
            count1 = 0
            count2 = 0
            for char in email:
                if char is '@':
                    count1 = count1 + 1
                elif char is '.':
                    count2 = count2 + 1
            if count1 >  1 or count1 == 0 or count2 == 0:
                flash("That is not a valid email", 'error')
            else:
                has_space = False
                for char in email:
                    if char.isspace():
                        has_space = True
                    if  has_space:       
                        flash("Email cannot contain any spaces", 'error')
        if not password:
            flash("A password is required", 'error')
        elif len(password) < 3 or len(password) > 20:
            flash("Password must be at least 3 and less than 20 characters long", 'error')
        else:
            has_space = False
            for char in password:
                if char.isspace():
                    has_space = True
                if  has_space:       
                    flash("Password cannot contain any spaces", 'error')
        if user and check_pwd_hash(password, user.pw_hash):
            session['email'] = email
            flash("You have logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')


    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if not email:
            flash("An email is required", 'error')
        if email:
            if len(email) < 3 or len(email) > 20:
                flash("Email must be at least 3 and less than 20 characters long", 'error')
            count1 = 0
            count2 = 0
            for char in email:
                if char is '@':
                    count1 = count1 + 1
                elif char is '.':
                    count2 = count2 + 1
            if count1 >  1 or count1 == 0 or count2 == 0:
                flash("That is not a valid email", 'error')
            else:
                has_space = False
                for char in email:
                    if char.isspace():
                        has_space = True
                    if  has_space:       
                        flash("Email cannot contain any spaces", 'error')
        if not password:
            flash("A password is required", 'error')
        elif len(password) < 3 or len(password) > 20:
            flash("Password must be at least 3 and less than 20 characters long", 'error')
        else:
            has_space = False
            for char in password:
                if char.isspace():
                    has_space = True
                if  has_space:       
                    flash("Password cannot contain any spaces", 'error')
        if password != verify:
            flash("Passwords must match", 'error')


        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')
        else:
            flash('User already exists', 'error')


    return render_template('signup.html')

@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['email']
    return redirect('/blog')


if __name__ == '__main__':    
    app.run()
