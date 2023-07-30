from wtforms import StringField, SubmitField, BooleanField, EmailField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class TeamForm(FlaskForm):
    name_command = StringField('Название команды', validators=[DataRequired()])
    name_of_organization = StringField('Название организации', validators=[DataRequired()])
    manager = StringField('ФИО Руководителя', validators=[DataRequired()])
    number_phone_of_manager = StringField('Номер телефона руководителя', validators=[DataRequired()])
    email_of_manager = EmailField('Email руководителя', validators=[DataRequired()])
    name_first_member = StringField('Имя первого участника', validators=[DataRequired()])
    last_name_first_member = StringField('Фамилия первого учатсника', validators=[DataRequired()])
    middle_name_first_member = StringField('Отчество первого участника(Если есть)', default="-")
    date_birthday_first_member = StringField('Дата рождения первого участника', validators=[DataRequired()])
    # date_birthday_first_member = DateField('Дата (ГГГГ-ММ-ДД)', format='%Y-%m-%d', validators=[DataRequired()])
    certificate_PFDO_first_member = StringField('Свидетельство ПФДО первого участника(Необязательно)', default="-")
    number_phone_second_member = StringField('Номер телефона второго участника', validators=[DataRequired()])
    name_second_member = StringField('Имя второго участника', validators=[DataRequired()], default="-")
    middle_name_second_member = StringField('Отчество второго участника(Если есть)', default="-")
    last_name_second_member = StringField('Фамилия второго участника', validators=[DataRequired()], default="-")
    date_birthday_second_member = StringField('Дата рождения второго участника', validators=[DataRequired()], default="-")
    certificate_PFDO_second_member = StringField('Свидетельство ПФДО второго участника(Необязательно)', default="-")
    submit = SubmitField('Зарегистрировать команду')