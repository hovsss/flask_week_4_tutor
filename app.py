import json
import secrets

from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.sql.expression import func
from wtforms import StringField, HiddenField, RadioField, SelectField, SubmitField, validators

from data import goals, teachers

WEEKDAYS = (("mon", "Понедельник"), ("tue", "Вторник"), ("wed", "Среда"), ("thu", "Четверг"), ("fri", "Пятница"),
            ("sat", "Суббота"), ("sun", "Воскресенье"))
ALL_DATA = 'data.json'
BOOKING_DATA = 'booking.json'
REQUEST_DATA = 'request.json'


#### Создание форм ####
class BookingForm(FlaskForm):
    clientName = StringField("Вас зовут", [validators.InputRequired(message="Необходимо ввести имя")])
    clientPhone = StringField("Ваш телефон", [validators.InputRequired(message="Необходимо ввести телефон")])
    clientTeacher = HiddenField()
    clientWeekday = HiddenField("")
    clientTime = HiddenField("")


class RequestForm(FlaskForm):
    clientName = StringField("Вас зовут", [validators.InputRequired(message="Необходимо ввести имя")])
    clientPhone = StringField("Ваш телефон",
                              [validators.InputRequired(message="Необходимо ввести телефон")])
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


app = Flask(__name__)
csrf = CSRFProtect(app)
SECRET_KEY = secrets.token_urlsafe()
app.config['SECRET_KEY'] = SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data//base.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Инструкция по работе
# set FLASK_APP=app.py
# flask db init
# flask db migrate
# flask db upgrade

# export FLASK_RUN_PORT=8000
# set FLASK_RUN_PORT=8000
# flask run

#### MODELS ####

teachers_goals_association = db.Table('teachers_goals',
                                      db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
                                      db.Column('goal_id', db.Integer, db.ForeignKey('goals.id'))
                                      )


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    about = db.Column(db.Text)
    rating = db.Column(db.Float)
    picture = db.Column(db.String(100))
    price = db.Column(db.Integer)
    # goals = db.Column(db.String(100))
    free = db.Column(db.UnicodeText)
    #
    booking = db.relationship("Booking", back_populates='teacher')
    goals = db.relationship("Goal", secondary=teachers_goals_association, back_populates="teachers")


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(14))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    weekday = db.Column(db.String(10))
    time = db.Column(db.String(10))
    #
    teacher = db.relationship("Teacher", back_populates="booking")


# "clientName": "Сергей",
# "clientPhone": "16161616",
# "clientTeacher": 4,
# "clientWeekday": "mon",
# "clientTime": "16:00"


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    goal = db.Column(db.String(10))
    # goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
    time = db.Column(db.String(100))
    # goal = db.relationship("Goal", back_populates="requests")


# "clientName": "яяя з",
# "clientPhone": "999",
# "clientGoal": "Для путешествий",
# "clientTime": "7-10 часов в неделю"


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    goal = db.Column(db.String(100))
    teachers = db.relationship("Teacher", secondary=teachers_goals_association, back_populates="goals")


# "travel": "Для путешествий",
# "study": "Для учебы",
# "work": "Для работы",
# "relocate": "Для переезда"

# db.drop_all()
# db.create_all() # создает таблицу, если она отсутсвует
####


#### MODELS ####

def write_data(data_to_write, data_source):
    with open(data_source, "w", encoding='utf-8') as f:
        json.dump(data_to_write, f, indent=4, ensure_ascii=False)


def load_data(data_source):
    try:
        with open(data_source, 'r', encoding='utf-8') as f:
            result = (json.load(f)).values()
    except FileNotFoundError:
        result = None

    return result


def add_list_data(data_to_add, data_source):
    try:
        with open(data_source, 'r', encoding='utf-8') as f:
            records = json.load(f)
    except FileNotFoundError:
        records = []

    records.append(data_to_add)
    write_data(records, data_source)


def load_all_data():
    result = load_data(ALL_DATA)
    if result is None:
        result = {'goals': goals, 'teachers': teachers}
        write_data(result, ALL_DATA)
        result = result.values()

    return result


#### Маршруты ####
@app.route('/')
def render_main():
    # goals, teachers = load_all_data()
    #
    # if len(teachers) > 6:
    #     random.seed()
    #     teachers = random.sample(teachers, 6)

    goals = Goal.query.all()
    teachers = Teacher.query.order_by(func.random()).limit(6)

    # Закончил здесь с сортировкой списка  #TODO
    # select.order_by(func.random()) # for PostgreSQL, SQLite
    # select.order_by(func.rand()) # for MySQL
    # db.session.query(Teacher.id).all()

    return render_template('index.html', goals=goals, teachers=teachers)


@app.route('/all/', methods=['GET', 'POST'])
@csrf.exempt
def all():
    goals = Goal.query.all()

    form = SortForm()

    if request.method == "POST":

        if request.form["sort_order"] == "best":
            teachers = Teacher.query.order_by(Teacher.rating.desc()).all()
        elif request.form["sort_order"] == "expensive":
            teachers = Teacher.query.order_by(Teacher.price.desc()).all()
        elif request.form["sort_order"] == "cheap":
            teachers = Teacher.query.order_by(Teacher.price).all()
        else:
            teachers = Teacher.query.order_by(func.random()).all()

        return render_template('all.html', goals=goals, teachers=teachers, form=form)

    # Заполненная форма выбора не передана
    else:
        teachers = Teacher.query.order_by(func.random()).all()
        return render_template('all.html', goals=goals, teachers=teachers, form=form)


@app.route('/goals/<goal>/')
def render_goals_item(goal):
    # goals, teachers = load_all_data()

    goals = Goal.query.all()
    current_goal = Goal.query.filter(Goal.code == goal).scalar()
    # почти магия с отбором по many to many, но заработало!
    teachers = Teacher.query.filter(Teacher.goals.contains(current_goal)).all()

    # # Проверка входных данных
    # if goal not in goals:
    #     return render_template('error.html', text="К сожалению, вы ввели неверную цель"), 404
    #
    # teachers = [t for t in teachers if goal in t["goals"]]

    return render_template('goal.html', goals=goals, teachers=teachers, current_goal=current_goal)


@app.route('/profiles/<int:teacher_id>/')
def render_profiles_item(teacher_id):
    # Переход на БД

    # TODO а какой из этих вариантов лучше?
    teacher = Teacher.query.get_or_404(teacher_id)
    # teacher = db.session.query(Teacher).get_or_404(id)

    return render_template('profile.html', t=teacher, weekdays=WEEKDAYS, timetable=json.loads(teacher.free))


@app.route('/request/', methods=['GET', 'POST'])
def render_request():
    form = RequestForm()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=['POST'])
def render_request_done():
    # Если данные не были отправлены
    if request.method != "POST":
        # Если пользователь попал на эту страницу не из формы ввода, выдаем 404 ошибку
        return render_template('error.html', text="К сожалению, данной страницы не существует"), 404

    # Если данные были отправлены
    form = RequestForm()
    if not form.validate_on_submit():
        # отправляем форму назад
        return render_template('request.html', form=form)

    # получаем данные
    client_name = form.clientName.data
    client_phone = form.clientPhone.data
    client_goal = form.clientGoal.data
    client_time = form.clientTime.data

    # goal = next((g[1] for g in form.clientGoal.choices if g[0] == client_goal), -1)

    time = next((t[1] for t in form.clientTime.choices if t[0] == client_time), -1)
    #
    # if goal == -1 or time == -1:
    #     return render_template('error.html', text="К сожалению, вы ввели неверные данные"), 404
    #
    # # сохраняем данные
    # add_list_data({'clientName': client_name, 'clientPhone': client_phone, 'clientGoal': goal,
    #                'clientTime': time}, REQUEST_DATA)

    # TODO Доделаю после глючит
    goal = Goal.query.filter(Goal.code == client_goal).scalar()
    request_t = Request(name=client_name, phone=client_phone, goal=goal.goal, time=time)
    db.session.add(request_t)
    db.session.commit()

    # TODO в форме подтверждения надо выводить полные имена, а не короткие коды...

    # переходим на request_done
    return render_template('request_done.html', clientName=client_name, clientPhone=client_phone,
                           # clientGoal=goal, clientTime=time)
                           clientGoal=request_t.goal, clientTime=request_t.time)


@app.route('/booking/<int:teacher_id>/<weekday>/<time>/', methods=['GET', 'POST'])
def render_booking_item(teacher_id, weekday, time):
    goals, teachers = load_all_data()

    goals = Goal.query.all()
    teachers = Teacher.query.all()

    form = BookingForm()
    if request.method == "POST":
        # если данные post и get отличаются, приводим их к одному виду
        time = form.clientTime.data
        teacher_id = int(form.clientTeacher.data)
        weekday = form.clientWeekday.data

    day = next((w for w in WEEKDAYS if w[0] == weekday), -1)  #
    teacher = next((t for t in teachers if t["id"] == teacher_id), -1)

    # Если данные были отправлены
    if request.method == "POST":
        if form.validate_on_submit():
            # получаем данные
            client_name = form.clientName.data
            client_phone = form.clientPhone.data

            if not teacher["free"][weekday][time]:
                return render_template('error.html', text="К сожалению, указанное время занято"), 200

            teacher["free"][weekday][time] = False

            # сохраняем данные
            # write_data({'goals': goals, 'teachers': teachers}, ALL_DATA)
            # add_list_data({'clientName': client_name, 'clientPhone': client_phone, 'clientTeacher': teacher_id,
            #                'clientWeekday': weekday, 'clientTime': time}, BOOKING_DATA)

            # Пытаемся перейти на БД
            # TODO Зачем нужен back_populates ведь в это случае все работало бы и без него
            booking = Booking(name=client_name, phone=client_phone, teacher_id=teacher_id, weekday=weekday, time=time)
            db.session.add(booking)
            db.session.commit()

            # переходим на booking_done
            return render_template('booking_done.html', clientName=client_name, clientPhone=client_phone,
                                   clientWeekday=day, clientTime=time)

    # Если данные еще НЕ были отправлены или неверны
    # выводим форму
    form.clientTime.data = time
    form.clientTeacher.data = teacher_id
    form.clientWeekday.data = weekday

    return render_template('booking.html', form=form, t=teacher, weekday=day, time=time)


@app.errorhandler(404)
def render_not_found(error):
    return render_template('error.html', text="К сожалению, запрашиваемая Вами страница не найдена..."), 404


@app.errorhandler(500)
def render_server_error(error):
    return render_template('error.html',
                           text="Что-то пошло не так, но мы все исправим:\n{}".format(error.original_exception)), 500


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
