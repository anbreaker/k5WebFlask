from tasks import app
from flask import render_template, request, redirect, url_for
from tasks.forms import TaskForm

import csv

DATOS = './data/tareas.txt'
cabecera = ['title', 'description', 'date']

@app.route("/")
def index():
    fdatos = open(DATOS, 'r')
    csvreader = csv.reader(fdatos, delimiter=",", quotechar='"')

    registros = []
    for linea in csvreader:
        registros.append(linea)

    fdatos.close()
    return render_template("index.html", registros=registros) 


@app.route("/newtask", methods=['GET', 'POST'])
def newTask():
    form = TaskForm(request.form)

    if request.method == 'GET':
        return render_template("task.html", form=form)

    if form.validate():
        fdatos = open(DATOS, 'a')
        csvwriter = csv.writer(fdatos, delimiter=",", quotechar='"')

        title = request.values.get('title')
        desc = request.values.get('description')
        date = request.values.get('date')

        csvwriter.writerow([title, desc, date])

        fdatos.close()
        return redirect(url_for("index"))
    else:
        return render_template("task.html", form=form)