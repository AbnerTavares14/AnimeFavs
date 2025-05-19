from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired



class AnimeForm(FlaskForm):
    title = StringField('Anime Title', validators=[DataRequired()])
    submit = SubmitField('Search')