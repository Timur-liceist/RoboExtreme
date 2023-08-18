from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateTimeField
from wtforms.validators import DataRequired


class NewCompetition(FlaskForm):
    date_of_start_competition = StringField('Дата начала соревнования', validators=[DataRequired()])
    commentary_for_competition = TextAreaField('Комментарии', validators=[DataRequired()])
    date_of_ending_registration_members = DateTimeField('Дата и время окончания соревнования', validators=[DataRequired()])
    submit = SubmitField('Создать соревнование')