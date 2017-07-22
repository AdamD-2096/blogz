from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashfun import make_pw_hash, check_pw_hash
from now import get_time
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://blogz:@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "C6"

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    liked =  db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, owner, owned, liked=False):
        self.owner = owner
        self.owned = owned
        self.liked = liked


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    time = db.Column(db.String(20))
    likes = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likez = db.relationship('Like', backref='owned')

    def __init__(self, title, body, owner, time):
        self.title = title
        self.body = body
        self.owner = owner
        self.time = time


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(200))
    posts = db.relationship('Post', backref='owner')
    likes = db.relationship('Like', backref='owner')

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

@app.route('/like_post', methods=['POST'])
def like_post():
    post_id = int(request.form["post-id"])
    user_id = int(request.form["user-id"])
    owner = User.query.get(user_id)
    owned = Post.query.get(post_id)
    like = Like.query.filter_by(owned=owned, owner=owner).first()
    if like:
        if not like.liked:
            like.liked = True
            owned.likes += 1
            db.session.commit()
            
        else:
            like.liked = False
            owned.likes = (Post.likes - 1)
            db.session.commit()
    else:
        new_like = Like(owner, owned, True)
        db.session.add(new_like)
        Post.likes = Post.likes + 1
        db.session.commit()
    return redirect("/blog?id=" + str(post_id))

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
                if not user or email == "":
                    new_user = User(username, email, password)
                    db.session.add(new_user)
                    db.session.commit()
                    session['user'] = new_user.username
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
            session['user'] = user.username
            flash("logged in", 'success')
            return redirect('/blog')
        else:
            user = User.query.filter_by(username=ename).first()
            if user and check_pw_hash(password, user.password):
                session['user'] = user.username
                flash("logged in", 'success')
                return redirect('/blog')
            else:
                flash('Email/Username or Password inccorect', 'error')
            
    return render_template('login.html')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users = users)

@app.route("/blog")
def blog():
    postid = request.args.get('id')
    userid = request.args.get('uid')
    if postid:
        post = Post.query.get(postid)
        if 'user' not in session:
            return render_template('postitbare.html', post=post)
        user = User.query.filter_by(username=session['user']).first()
        like = Like.query.filter_by(owned=post).all()
        liked = Like.query.filter_by(owned=post, owner=user).first()
        return render_template('postit.html', post=post, user=user, like=like, liked=liked)
    if userid:
        userposts = Post.query.filter_by(owner_id=userid).all()
        return render_template('author.html', posts=userposts)

    posts = Post.query.all()
    return render_template('blog.html', title="Blog", posts=posts)  
 
@app.route('/post_form', methods=["POST", "GET"])   
def post_form():
    if 'user' not in session:
        flash("log in to create posts", 'error')
        return redirect('/blog')
    if request.method == "POST":
        owner = User.query.filter_by(username=session['user']).first()
        title = request.form["title"]
        body = request.form["body"]
        if body == "" or title == "":
            flash("please have content in both fields", "error")
            return redirect("/post_form")
        time = get_time()
        new_post = Post(title, body, owner, time)
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
    return redirect('/')

@app.route('/drop_create')
def drop_create():
    db.drop_all()
    db.create_all()
    return redirect('/')
if __name__ == '__main__':
    app.run()