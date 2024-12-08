# Program to implement Top Movies Project:
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float,func
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import movies_api



class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies_data.db"
db.init_app(app)

# CREATE TABLE
class Movies(db.Model):
    id:Mapped[int] = mapped_column(Integer,primary_key = True,autoincrement = True)
    title:Mapped[str] = mapped_column(String,unique = True)
    year:Mapped[int] = mapped_column(Integer)
    description:Mapped[str] = mapped_column(String)
    rating:Mapped[float] = mapped_column(Float)
    ranking: Mapped[int] = mapped_column(Integer)
    review: Mapped[float] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)

# Flask Form-1:
class MyForm(FlaskForm):
    rating = StringField(label = "Your rating out of 10 e.g 7.5",validators=[DataRequired()])
    review = StringField(label = "Your review",validators = [DataRequired()])
    submit = SubmitField()

# Flask Form-2:
class AddForm(FlaskForm):
    movie_name = StringField(label = "Movie Title",validators = [DataRequired()])
    submit = SubmitField(label = "Add Movie")

@app.route("/")
def home():
    movie_list = []
    with app.app_context():
        result = db.session.execute(db.select(Movies).order_by(Movies.rating.desc())).scalars()
        total = db.session.execute(db.select(func.count()).select_from(Movies)).scalar_one()
        for cnt,data in zip(range(total,0,-1),result):
                movie_list.append({
                    "id":data.id,
                    "title":data.title,
                    "year":data.year,
                    "desc":data.description,
                    "rating":data.rating,
                    "ranking":cnt,
                    "review":data.review,
                    "imgurl":data.image_url})
    return render_template("index.html",data = movie_list)

@app.route("/update/<int:num>",methods = ["GET","POST"])
def update(num):
    form = MyForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            with app.app_context():
                fetch_record = db.session.execute(db.select(Movies).where(Movies.id == num)).scalar()
                fetch_record.rating = request.form['rating']
                fetch_record.review = request.form['review']
                db.session.commit()
                return redirect(url_for('home'))

    return render_template("edit.html",form = form)

@app.route("/delete/<int:num>")
def delete_movie(num):
    with app.app_context():
        fetch_record = db.session.execute(db.select(Movies).where(Movies.id == num)).scalar()
        db.session.delete(fetch_record)
        db.session.commit()
    return redirect(url_for('home'))

@app.route("/add",methods = ["GET","POST"])
def add_movie():
    form = AddForm()
    global rank_count
    if request.method == "POST":
        if form.validate_on_submit():
            info = movies_api.movie_details(request.form["movie_name"])
            with app.app_context():
                try:
                    new_movie = Movies(
                        title=info["Title"],
                        year=info["Year"],
                        description=info["Plot"],
                        rating=info["imdbRating"],
                        ranking=0,
                        review=info["Genre"],
                        image_url=info["Poster"],
                    )
                    db.session.add(new_movie)
                    db.session.commit()
                    return redirect(url_for('home'))
                except:
                    pass

    return render_template("add.html",form = form)

if __name__ == '__main__':
    app.run(debug=True)
