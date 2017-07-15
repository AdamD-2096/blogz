from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
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
    password = db.Column(db.String(40))
    posts = db.relationship('Post', backref='owner')

    def __init__(self, username, email, password):
        self.email = email
        self.password = password
        self.username = username

def validate(un, em, p, p2):
    error = {0:"", 1:"", 2:"", 3:"", 5:em, 6:un}
    if len(un) < 6:
        error[0] = "username must be 6 or more characters"

    if len(p) < 6:
        error[1] = "password must be 6 or more characters"
    elif " " in p:
        error[1] = "no spaces please"
    
    if p2 == "":
        error[2] = "please re-enter your password"
    elif p2 != p:
        error[2] = "password must match"

    emat = re.search("\w+@\w+.\w+", em)
    if not emat:
        error[3] = "please enter a valid email"
        error[5] = ""

    return error


@app.route('/login/signup')
def signup():

    return render_template("signup.html")

@app.route("/login")
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("logged in", 'success')
            return redirect('/blog')
        else:
            flash('email or password inccorect', 'error')
            
    return render_template('login.html')

@app.route('/')
def index():

    return render_template('index.html')

@app.route("/blog")
def blog():
    postid = request.args.get('id')
    userid = request.args.get('uid')
    if postid:
        post = Post.query.get(num)
        return render_template('postit.html', post=post)
    if userid:
        #userposts = Post.query.filter_by(userid=userid)
        return render_template('author.html')#, posts=userposts)
    else:
        posts = Post.query.all()
        return render_template('blog.html', title="Blog", posts=posts)  
 
@app.route('/post_form', methods=["POST", "GET"])   
def post_form():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        if body == "" or title == "":
            flash("please have content in both fields", "error")
            return redirect("/post_form")
        new_post = Post(title, body)
        db.session.add(new_post)
        db.session.commit()
        return redirect("/post?id=" + str(new_post.id))

    return render_template("post_form.html", title="New Post")


@app.route("/delete_post", methods=['POST', 'GET'])
def delete():
    if request.method == "POST":
        post_id = int(request.form["post-id"])
        post = Post.query.get(post_id)
        db.session.delete(post)
        db.session.commit()
    return redirect('/blog')


if __name__ == '__main__':
    app.run()