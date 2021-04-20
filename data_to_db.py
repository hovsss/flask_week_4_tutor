import json

from data import goals, teachers
from models import Teacher, Goal, db, teachers_goals_association

# TODO без этого костыля не работает данный модуль заполнения таблиц со следующей ошибкой, можно сделать лучше?
# No application found. Either work inside a view function or push an application context.
# See http://flask-sqlalchemy.pocoo.org/contexts/.
from app import app
app.app_context().push()

# Удаляем данные из таблиц, чтобы исключить дубли
db.session.query(Goal).delete(synchronize_session=False)
db.session.query(Teacher).delete(synchronize_session=False)
db.session.query(teachers_goals_association).delete(synchronize_session=False)
db.session.commit()

for code, goal in goals.items():
    db.session.add(Goal(code=code, goal=goal))
db.session.commit()

## TODO При использвании many to many отношений с таблицей Goals не понял как применять этот вариант "быстрого" заполнения
# teachers_to_save = []
# for t in teachers:
#     teacher = Teacher(id=t['id'], name=t['name'], about=t['about'], rating=t['rating'], picture=t['picture'],
#                       price=t['price'],
#                       goals=json.dumps(t['goals']),
#                       free=json.dumps(t['free']))
#     teachers_to_save.append(teacher)
# db.session.bulk_save_objects(teachers_to_save)
# db.session.commit()

for t in teachers:
    teacher = Teacher(id=t['id'], name=t['name'], about=t['about'], rating=t['rating'], picture=t['picture'],
                      price=t['price'], free=json.dumps(t['free']))
    db.session.add(teacher)

    for code in t['goals']:
        goal_db = db.session.query(Goal).filter(Goal.code == code).scalar()  # = first()
        goal_db.teachers.append(teacher)
        db.session.add(goal_db)

db.session.commit()
