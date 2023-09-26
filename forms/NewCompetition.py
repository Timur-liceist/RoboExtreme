from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateTimeField
from wtforms.validators import DataRequired


class NewCompetition(FlaskForm):
    date_of_start_competition = StringField('Дата проведения соревнования', validators=[DataRequired()])
    header_for_competition = TextAreaField('Заголовок', validators=[DataRequired()])
    commentary_for_competition = TextAreaField('Комментарии', validators=[DataRequired()])
    date_of_ending_registration_members = DateTimeField('Дата и время окончания регистрации на соревнование', validators=[DataRequired()])
    date_of_starting_registration_members = DateTimeField('Дата и время начала регистрации на соревнование', validators=[DataRequired()])
    submit = SubmitField('Добавить соревнование')