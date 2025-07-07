from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.Text(), nullable=False)
    comment = db.Column(db.Text(), nullable=False)

class CommentForm(FlaskForm):
    name = StringField('名前', validators=[DataRequired(), Length(max=50)])
    comment_data = TextAreaField('コメント', validators=[DataRequired(), Length(max=500)])


with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    form = CommentForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        comment = form.comment_data.data.strip()
        new_comment = Comment(pub_date=datetime.now(), name=name, comment=comment)
        db.session.add(new_comment)
        db.session.commit()
        flash("投稿が完了しました。", "success")
        return redirect(url_for("index"))
    comments = Comment.query.order_by(Comment.pub_date.desc()).all()
    return render_template("index.html", form=form, lines=comments)

@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", message="不正なリクエストです。"), 400

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", message="サーバーエラーが発生しました。"), 500

if __name__ == "__main__":
    app.run(host="localhost", debug=True)
