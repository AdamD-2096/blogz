from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


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

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.likes = 0



@app.route('/')
def index():
    return redirect('/blog')

@app.route("/blog")
def blog():
    num = request.args.get('id')
    if num:
        post = Post.query.get(num)
        return render_template('postit.html', post=post)
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