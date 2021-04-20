import json
import secrets

from flask import Flask, render_template, request, abort
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.sql.expression import func

from forms import BookingForm, RequestForm, SortForm
from models import db, Teacher, Booking, Request, Goal

WEEKDAYS = (("mon", "Понедельник"), ("tue", "Вторник"), ("wed", "Среда"), ("thu", "Четверг"), ("fri", "Пятница"),
            ("sat", "Суббота"), ("sun", "Воскресенье"))

app = Flask(__name__)
csrf = CSRFProtect(app)
SECRET_KEY = secrets.token_urlsafe()
app.config['SECRET_KEY'] = SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data//base.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_ECHO"] = True

# TODO не понимаю как работает эта магия при создании модуля models.py, что теперь вместо db= пишем db.init ???
# db = SQLAlchemy(app)
db.init_app(app)

# Команды для миграций
# set FLASK_APP=app.py
# flask db init
# flask db migrate
# flask db upgrade
migrate = Migrate(app, db)


#### Маршруты ####
@app.route('/')
def render_main():
    goals = Goal.query.all()
    teachers = Teacher.query.order_by(func.random()).limit(6)
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
    goals = Goal.query.all()
    current_goal = Goal.query.filter(Goal.code == goal).scalar()
    teachers = Teacher.query.filter(Teacher.goals.contains(current_goal)).all()
    return render_template('goal.html', goals=goals, teachers=teachers, current_goal=current_goal)


@app.route('/profiles/<int:teacher_id>/')
def render_profiles_item(teacher_id):
    # TODO а какой из этих вариантов лучше?
    teacher = Teacher.query.get_or_404(teacher_id)
    # teacher = db.session.query(Teacher).get_or_404(id)

    return render_template('profile.html', t=teacher, weekdays=WEEKDAYS, timetable=json.loads(teacher.free))


@app.route('/request/', methods=['GET', 'POST'])
def render_request():
    form = RequestForm()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=['POST', 'GET'])
def render_request_done():
    # Если данные не были отправлены
    if request.method != "POST":
        abort(404)

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

    time = next((t[1] for t in form.clientTime.choices if t[0] == client_time), -1)

    goal = Goal.query.filter(Goal.code == client_goal).scalar()
    request_t = Request(name=client_name, phone=client_phone, goal=goal.goal, time=time)
    db.session.add(request_t)
    db.session.commit()

    # переходим на request_done
    return render_template('request_done.html', clientName=client_name, clientPhone=client_phone,
                           clientGoal=request_t.goal, clientTime=request_t.time)


@app.route('/booking/<int:teacher_id>/<weekday>/<time>/', methods=['GET', 'POST'])
def render_booking_item(teacher_id, weekday, time):
    teacher = Teacher.query.get(teacher_id)

    form = BookingForm()
    if request.method == "POST":
        # если данные post и get отличаются, приводим их к одному виду
        time = form.clientTime.data
        teacher_id = int(form.clientTeacher.data)
        weekday = form.clientWeekday.data

    day = next((w for w in WEEKDAYS if w[0] == weekday), -1)  #

    # Если данные были отправлены
    if request.method == "POST":
        if form.validate_on_submit():
            # получаем данные
            client_name = form.clientName.data
            client_phone = form.clientPhone.data

            # TODO Зачем нужен back_populates ведь в этом случае все работало бы и без него
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
