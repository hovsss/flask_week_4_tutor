from app import Teacher, db, Booking

teacher = Teacher()
teacher.name = "Ева"

booking = Booking()
booking.name = 'Сергей'
booking.teacher = teacher  # !!! ВОТ как важно писать без всяких id здесь, тогда работает !!!

db.session.add(teacher)
db.session.add(booking)
db.session.commit()

teacher = Teacher.query.filter(Teacher.id == 0).scalar()
print(teacher)
print(teacher.name)
for x in teacher.goals:
    print(x, x.code, x.goal)

a = 1
