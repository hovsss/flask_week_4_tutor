from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, RadioField, SelectField, SubmitField
from wtforms.validators import InputRequired


class BookingForm(FlaskForm):
    clientName = StringField("Вас зовут", [InputRequired(message="Необходимо ввести имя")])
    clientPhone = StringField("Ваш телефон", [InputRequired(message="Необходимо ввести телефон")])
    clientTeacher = HiddenField()
    clientWeekday = HiddenField("")
    clientTime = HiddenField("")


class RequestForm(FlaskForm):
    clientName = StringField("Вас зовут", [InputRequired(message="Необходимо ввести имя")])
    clientPhone = StringField("Ваш телефон",
                              [InputRequired(message="Необходимо ввести телефон")])
    clientGoal = RadioField('Какая цель занятий?', default="travel",
                            choices=[("travel", "Для путешествий"), ("study", "Для учебы"),
                                     ("work", "Для работы"), ("relocate", "Для переезда"),
                                     ("coding", "Для программирования")])
    clientTime = RadioField('Сколько времени есть?', default="1-2",
                            choices=[("1-2", "1-2 часа в неделю"), ("3-5", "3-5 часов в неделю"),
                                     ("5-7", "5-7 часов в неделю"), ("7-10", "7-10 часов в неделю")])


class SortForm(FlaskForm):
    sort_order = SelectField(choices=[("randomly", "В случайном порядке"), ("best", "Сначала лучшие по рейтингу"),
                                      ("expensive", "Сначала дорогие"), ("cheap", "Сначала недорогие")])
    submit = SubmitField("Сортировать")
