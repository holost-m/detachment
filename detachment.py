from flask import Flask, render_template, url_for, request
import os
from jinja2 import Template
import class1

app1 = Flask(__name__)
db = class1.sfgo_db()




#  Главная
@app1.route("/main", methods = ["POST", "GET"])
def main():
    return render_template('main.html')

#  Добавить (общий вид)
@app1.route("/add", methods = ["POST", "GET"])
def add():
    message1 = 'Заполните форму'
    db.update_free_position() # обновляем свободные места
    return render_template('add.html', message = message1, free_pos = db.free_position, eq = db.get_eq())


#  Добавить сотрудника в базу
@app1.route("/person_add", methods = ["POST", "GET"])
def person_add():
    db.update_free_position() # обновляем свободные места
    if request.method == 'POST':
        d_person_inf = dict(request.form)
        person_info = list(d_person_inf.values())
        print("/person_add Запрос работает")
        print(person_info)
        message1 = db.add_person(person_info)

    return render_template('add.html', message = message1, free_pos = db.free_position, eq = db.get_eq()) # ch = "/person_add", 


#  Добавить технику в базу
@app1.route("/equipment_add", methods = ["POST", "GET"])
def equipment_add():
    db.update_free_position() # обновляем свободные места
    if request.method == 'POST':
        d_equipment_inf = dict(request.form)
        equipment_info = list(d_equipment_inf.values())
        message1 = db.add_equipment(equipment_info)

    return render_template('add.html', message = message1, ch = "/equipment_add", free_pos = db.free_position, eq = db.get_eq())


#  Показать базу общая
@app1.route("/show", methods = ["POST", "GET"])
def show():
    return render_template('show.html', info = db.show_db())

#  Удалить сотрудника
@app1.route("/delete", methods = ["POST", "GET"])
def delete():
    return render_template('delete.html')

#  Изменить данные
@app1.route("/change", methods = ["POST", "GET"])
def change():
    return render_template('change.html')

#  Анализ данных
@app1.route("/analysis", methods = ["POST", "GET"])
def analysis():
    return render_template('analysis.html', info = db.analysis_db())



if __name__ == "__main__":
    app1.run(debug=True)





