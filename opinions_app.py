from datetime import datetime
import os
from random import randrange

from flask import Flask, flash, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)

REQUIRED_FIELD_MESSAGE = 'Обязательное поле'


class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    source = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class OpinionForm(FlaskForm):
    title = StringField(
        'Введите название фильма',
        validators=[
            DataRequired(message=REQUIRED_FIELD_MESSAGE),
            Length(1, 128),
        ],
    )
    text = TextAreaField(
        'Напиши мнение',
        validators=[DataRequired(message=REQUIRED_FIELD_MESSAGE)],
    )
    source = URLField(
        'Добавьте ссылку на подробный образ фильма',
        validators=[Length(1, 256), Optional()],
    )
    submit = SubmitField('Добавить')


@app.route('/')
def index_view():
    quantity = Opinion.query.count()
    if not quantity:
        return 'В базе данных мнений о фильмах нет.'
    offset_value = randrange(quantity)
    opinion: Opinion | None = Opinion.query.offset(offset_value).first()
    return render_template('opinion.html', opinion=opinion)


@app.route('/add', methods=['GET', 'POST'])
def add_opinion_view():
    form: OpinionForm = OpinionForm()
    if form.validate_on_submit():
        text = form.text.data
        if Opinion.query.filter_by(text=text).first() is not None:
            flash('Такое мнение уже было оставлено ранее!', 'existing-message')
            return render_template('add_opinion.html', form=form)
        opinion: Opinion = Opinion(
            title=form.title.data,
            text=form.text.data,
            source=form.source.data,
        )
        db.session.add(opinion)
        db.session.commit()
        return redirect(url_for('opinion_view', id=opinion.id))
    return render_template('add_opinion.html', form=form)


@app.route('/opinions/<int:id>')
def opinion_view(id: int):
    opinion = Opinion.query.get_or_404(id)
    return render_template('opinion.html', opinion=opinion)


if __name__ == '__main__':
    app.run()
