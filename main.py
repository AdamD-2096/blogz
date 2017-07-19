from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashfun import make_pw_hash, check_pw_hash
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://blogz:@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "C6"


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    likes = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.likes = 0
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    posts = db.relationship('Post', backref='owner')

    def __init__(self, username, email, password):
        self.email = email
        self.password = make_pw_hash(password)
        self.username = username

def validate(un, em, p, p2):
    error = {0:"", 1:"", 2:"", 3:"", 5:em, 6:un}
    if len(un) < 6:
        error[0] = "username must be 6 or more characters"
    elif " " in un:
        error[0] = "no spaces please"
        error[6] = ""

    if len(p) < 6:
        error[1] = "password must be 6 or more characters"
    elif " " in p:
        error[1] = "no spaces please"
    
    if p2 == "":
        error[2] = "please re-enter your password"
    elif p2 != p:
        error[2] = "password must match"
    if em != "":
        emat = re.search("\w+@\w+.\w+", em)
        if not emat:
            error[3] = "please enter a valid email"
            error[5] = ""

    return error


@app.route('/login/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        error = validate(username, email, password, verify)
        if error[0] or error[1] or error[2] or error[3]:
            if error[0] != "":
                flash(error[0], 'error')
            if error[3] != "":
                flash(error[3], 'error')
            if error[1] != "":
                flash(error[1], 'error')
            if error[2] != "": 
                flash(error[2], 'error')
            return render_template("signup.html", username=error[6], email=error[5])
            
        
        else:
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User.query.filter_by(email=email).first()
                if not user:
                    new_user = User(username, email, password)
                    db.session.add(new_user)
                    db.session.commit()
                    session['user'] = username
                    return redirect('/')
                else:
                    flash('Cannot create (Email already in use)', 'error')
            else:
                flash('Cannot create (Username already in use)', 'error')

    return render_template("signup.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        ename = request.form['ename']
        password = request.form['password']
        user = User.query.filter_by(email=ename).first()
        if user and check_pw_hash(password, user.password):
            session['user'] = User.username
            session['email'] = User.email
            flash("logged in", 'success')
            return redirect('/blog')
        else:
            user = User.query.filter_by(username=ename).first()
            if user and check_pw_hash(password, user.password):
                session['user'] = User.username
                session['email'] = User.email
                flash("logged in", 'success')
                return redirect('/blog')
            else:
                flash('Email/Username or Password inccorect', 'error')
            
    return render_template('login.html')

@app.route('/')
def index():

    return render_template('index.html')

@app.route("/blog")
def blog():
    postid = request.args.get('id')
    userid = request.args.get('uid')
    if postid:
        post = Post.query.get(postid)
        return render_template('postit.html', post=post)
    if userid:
        userposts = Post.query.filter_by(owner_id=userid).all()
        return render_template('author.html', posts=userposts)

    posts = Post.query.all()
    return render_template('blog.html', title="Blog", posts=posts)  
 
@app.route('/post_form', methods=["POST", "GET"])   
def post_form():
    if 'user' not in session:
        return redirect('/login')
    if request.method == "POST":
        owner = User.query.filter_by(username=session['user']).first()
        title = request.form["title"]
        body = request.form["body"]
        if body == "" or title == "":
            flash("please have content in both fields", "error")
            return redirect("/post_form")
        new_post = Post(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect("/blog?id=" + str(new_post.id))

    return render_template("post_form.html", title="New Post")


@app.route("/delete_post", methods=['POST', 'GET'])
def delete():
    if request.method == "POST":
        post_id = int(request.form["post-id"])
        post = Post.query.get(post_id)
        db.session.delete(post)
        db.session.commit()
    return redirect('/blog')

@app.route('/logout')
def logout():
    if 'user' in session:
        del session['user']
    if 'email' in session:
        del session['email']
    return redirect('/')

if __name__ == '__main__':
    app.run()