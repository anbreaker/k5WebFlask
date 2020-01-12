from tasks import app
from flask import render_template, request, redirect, url_for
from tasks.forms import TaskForm, ProccesTaskForm

import csv
import sqlite3
import os
from datetime import date

DATOS = './data/tareas.txt'
COPIA = './data/copia.txt'
BASE_DATOS = './data/tasks.db'

cabecera = ['title', 'description', 'date']


def openFiles(DATOS, COPIA):
    original = open(DATOS, 'r')
    copia = open(COPIA, 'w')
    return original, copia


def closeFiles(original, copia):
    original.close()
    copia.close()


def renameFiles(DATOS, COPIA):
    os.remove(DATOS)
    os.rename(COPIA, DATOS)


def todasTareasDB():
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = 'SELECT titulo, descripcion, fecha, id FROM tareas;'
    rows = cursor.execute(consulta)
    filas = []
    for row in rows:
        filas.append(row)
    
    print(filas)
    conn.close()
    return filas

def addTaskDB(title, description, fx):
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = '''
        INSERT INTO tareas (titulo, descripcion, fecha)
                    VALUES (?, ?, ?);
    '''
    cursor.execute(consulta, (title, description, fx))
    conn.commit()
    conn.close()
    
def borraTaskDB(id):
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = '''
        DELETE FROM tareas
            WHERE id = ?;
    '''
    #La base de datos espera una tupla en python las tuplas de unitarias precisas de 
    #la coma al final. (a,)
    '''
    >>> a = 'hola'
    >>> a
    'hola'
    >>> (a)
    'hola'
    >>> (a,)
    ('hola',)
    '''
    
    cursor.execute(consulta, (id,))
    conn.commit()
    conn.close()
    
def leeTaskDB(id):
    conn = sqlite3.connect(BASE_DATOS)
    cursor = conn.cursor()
    consulta = '''
        SELECT titulo, descripcion, fecha, id FROM tareas
            WHERE id = ?;
    '''
    rows = cursor.execute(consulta, (id)).fetchall()
    
    cursor.execute(consulta, (id,))
    conn.commit()
    conn.close()
    return rows

def todasTareas():
    fdatos = open(DATOS, 'r')
    csvreader = csv.reader(fdatos, delimiter=",", quotechar='"')

    registros = []
    for linea in csvreader:
        registros.append(linea)

    fdatos.close()
    return registros


def addTask(title, desc, fx):
    fdatos = open(DATOS, 'a')
    csvwriter = csv.writer(fdatos, delimiter=",", quotechar='"')
    csvwriter.writerow([title, desc, fx])
    fdatos.close()


def leeTask(ix):
    fdatos = open(DATOS, 'r')
    csvreader = csv.reader(fdatos, delimiter=",", quotechar='"')

    registroAct = None

    ix = int(ix)
    for ilinea, linea in enumerate(csvreader, start=1):
        if ilinea == ix:
            registroAct = linea
            break

    return registroAct


def borraTask(ix):
    return modTask(ix, True)


def modTask(ix, borra=False):
    original, copia = openFiles(DATOS, COPIA)
    csvreader = csv.reader(original, delimiter=",", quotechar='"')
    for ilinea, linea in enumerate(csvreader, start=1):
        csvwriter = csv.writer(copia, delimiter=",",
                               quotechar='"', lineterminator='\r')

        if ilinea == ix:
            if not borra:
                title = request.values.get('title')
                desc = request.values.get('description')
                fx = request.values.get('fx')
                csvwriter.writerow([title, desc, fx])
        else:
            title = linea[0]
            desc = linea[1]
            fx = linea[2]
            csvwriter.writerow([title, desc, fx])
    closeFiles(original, copia)
    renameFiles(DATOS, COPIA)


@app.route("/")
def index():
    #Para ficheros
    #registros = todasTareas()
    registros = todasTareasDB()
    return render_template("index.html", registros=registros)


@app.route("/newtask", methods=['GET', 'POST'])
def newTask():
    form = TaskForm(request.form)

    if request.method == 'GET':
        return render_template("task.html", form=form)

    if form.validate():
        title = request.values.get('title')
        desc = request.values.get('description')
        fx = request.values.get('fx')

        #Para ficheros
        # addTask(title, desc, fx)
        addTaskDB(title, desc, fx)

        return redirect(url_for("index"))
    else:
        return render_template("task.html", form=form)


@app.route("/processtask", methods=['GET', 'POST'])
def proccesTask():
    form = ProccesTaskForm(request.form)

    if request.method == 'GET':
        ix = request.values.get('ix')
        if ix:
            # Para ficheros
            # registroAct = leeTask(ix)
            filas = leeTaskDB(ix)
            print(f'\n\nVer que hay aqui--> {filas}\n\n')
            if len(filas) > 0:
                registroAct = filas[0]

            if registroAct:
                if registroAct[2]:
                    fechaTarea = date(int(registroAct[2][:4]), int(
                        registroAct[2][5:7]), int(registroAct[2][8:]))
                else:
                    fechaTarea = None

                accion = ''

                if 'btnModificar' in request.values:
                    accion = 'M'

                if 'btnBorrar' in request.values:
                    accion = 'B'

                form = ProccesTaskForm(
                    data={'ix': ix, 'title': registroAct[0], 'description': registroAct[1], 'fx': fechaTarea, 'btn': accion})

            return render_template("processtask.html", form=form)
        else:
            return redirect(url_for("index"))

    if form.btn.data == 'B':
        ix = int(request.values.get('ix'))
        # Para Ficheros
        # borraTask(ix)
        borraTaskDB(ix)

        return redirect(url_for('index'))

    if form.btn.data == 'M':
        if form.validate():
            ix = int(request.values.get('ix'))
            modTask(ix)
            return redirect(url_for("index"))
        return render_template("processtask.html", form=form)
