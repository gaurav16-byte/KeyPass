from flask import Flask, render_template, request, abort
import KeyPass
import threading
import os
from datetime import datetime as date
import sqlite3
import sys
import random
import subprocess
from cryptography.fernet import Fernet
from socket import gethostname
from prettytable import PrettyTable as pt
import csv
import pythoncom
import threading
import wmi

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/why')
def why():
    return render_template('why.html')

@app.route('/install')
def installation():
    return render_template('installation.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/after_sign')
def after_sign():
    return render_template('after_sign.html')

fail = 0
@app.route('/sign', methods=['POST'])
def sign():
    global fail
    if os.name == 'nt':
        f = open(os.path.expanduser("~") + '\\creds.txt','r')
    elif os.name == 'posix':
        f = open(os.path.expanduser("~") + '/Documents/creds.txt','r')

    check = f.read()
    f.close()
    if fail < 2:
        password = request.form['password']
        vv = KeyPass.signin(password, check)
        if 'WRONG' in vv:
            fail += 1
            return render_template('login.html', message=vv, is_safe=True)
            password = request.form['password']
        else:
            return after_sign()
    else:
        return abort(401, 'Too many wrong attempts')

@app.route('/addition', methods=['GET', 'POST'])
def addition():
    output = ''
    vx = ''
    tables = []
    if request.method == 'GET':
        if os.name == 'nt':
            conn = sqlite3.connect(os.path.expanduser("~") + '\\db.db')
        elif os.name == 'posix':
            conn = sqlite3.connect(os.path.expanduser("~") + '/Documents/db.db')
        cur = conn.cursor()
        tables = []
        num_range = ''
        for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
            tables += [i[0]]
        for i in range(len(tables)):
            output += str(i) + ') ' + tables[i] + "<br>"
            num_range += str(i)

        return render_template('addition.html', message=output, vx=vx, is_safe=True)
        
    elif request.method == 'POST':
        if os.name == 'nt':
            conn = sqlite3.connect(os.path.expanduser("~") + '\\db.db')
        elif os.name == 'posix':
            conn = sqlite3.connect(os.path.expanduser("~") + '/Documents/db.db')
        cur = conn.cursor()
        num_range = ''
        for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
            tables += [i[0]]
        for i in range(len(tables)):
            output += str(i) + ') ' + tables[i] + "<br>"
            num_range += str(i)

        name = request.form.get('name')
        user = request.form.get('user')
        password = request.form.get('password')
        if name is None or user is None or password is None:
            vx = 'Please fill out all fields'
        else:
            vx = KeyPass.addition(name, user, password, num_range)
            if 'Successfully' not in vx:
                vx = 'Error: ' + vx
                
        return render_template('addition.html', message=output, vx=vx, is_safe=True)

@app.route('/view')
def view():
    return render_template('view.html', table=KeyPass.view(), is_safe=True)

@app.route('/addserv', methods=['GET', 'POST'])
def addserv():
    output = 'AVAILABLE SERVICES:-- <br><br>'
    err = ''
    success = ''
    if os.name == 'nt':
        conn = sqlite3.connect(os.path.expanduser("~") + '\\db.db')
    elif os.name == 'posix':
        conn = sqlite3.connect(os.path.expanduser("~") + '/Documents/db.db')

    cur = conn.cursor()
    tables = []
    for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        tables += [i[0]]
        output += i[0] + "<br>"
    
    if request.method == 'GET':
        return render_template('addserv.html', output=output, is_safe=True, name='')
    else:
        name = request.form.get('name')
        result = KeyPass.service(name)
        return render_template('addserv.html', output=output, err=result[0], success=result[1], is_safe=True, name=name)

@app.route('/drop', methods=['GET', 'POST'])
def drop():
    output = ''
    if os.name == 'nt':
        conn = sqlite3.connect(os.path.expanduser("~") + '\\db.db')
    elif os.name == 'posix':
        conn = sqlite3.connect(os.path.expanduser("~") + '/Documents/db.db')

    cur = conn.cursor()
    tables = []
    num_range = ''
    for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        tables += [i[0]]

    for i in range(len(tables)):
        output += str(i) + ')' + tables[i] + "<br>"

    if request.method == 'GET':
        return render_template('remove.html', output=output, is_safe=True, name='')
    else:
        name = request.form.get('name')
        result = KeyPass.drop(name)
        return render_template('remove.html', output=output, err=result[0], success=result[1], is_safe=True, name=name)

@app.route('/backup', methods=['GET', 'POST'])
def backup():
    output = "ENTER THE REQUIRED DETAILS TO CREATE A BACKCUP FILE OF YOUR PASSWORDS."
    if request.method == 'GET':
        return render_template('backup.html', output=output, is_safe=True, user='', password='')
    else:
        user = request.form.get('user')
        password = request.form.get('password')
        result = KeyPass.backup(password, user)
        if "too many" in result:
            return abort(401, 'Too many wrong attempts')
        elif 'match' or 'Wrong' in result:
            user = request.form.get('user')
            password = request.form.get('password')
            result = KeyPass.backup(password, user)
            return render_template('backup.html', output=output, err=result, is_safe=True, user=user, password=password)
        else:
            return render_template('backup.html', output=output, err=result, is_safe=True, user=user, password=password)

@app.route('/register')
def register():
    output = ''
    msg_match = ''
    if os.name == 'nt':
        creds_file = os.path.expanduser("~") + "\\creds.txt"
        if not os.path.isfile(creds_file):
            output += "LOOKS LIKE YOU ARE NEW HERE !!<br>"
            output += "ENTER A STRONG COMPLEX PASSWORD THAT YOU WILL REMEMBER FOREVER OTHERWISE YOU WON'T BE ABLE TO ACCESS THEM.<br>"
            output += "COMPLEX PASSWORD RULES:<br>"
            output += "PASSWORD TO BE EQUAL OR LONGER THAN 8 CHARACTERS<br>"
            output += "IT SHOULD HAVE A MINIMUM OF 1 UPPERCASE CHARACTER<br>"
            output += "IT SHOULD HAVE A MINIMUM OF 1 DIGIT<br>"
            output += "IT SHOULD CONTAIN A MINIMUM OF 1 SPECIAL CHARACTER<br>"

        else:
            output += "YOU HAVE ALREADY REGISTERED, HEAD OVER TO THE LOGIN PAGE"

    elif os.name == 'posix':
        creds_file = os.path.expanduser("~/Documents/creds.txt")
        if not os.path.isfile(creds_file):
            output += "LOOKS LIKE YOU ARE NEW HERE !!<br>"
            output += "ENTER A STRONG COMPLEX PASSWORD THAT YOU WILL REMEMBER FOREVER OTHERWISE YOU WON'T BE ABLE TO ACCESS THEM.<br>"
            output += "COMPLEX PASSWORD RULES:<br>"
            output += "<ul>"
            output += "<li>PASSWORD TO BE EQUAL OR LONGER THAN 8 CHARACTERS</li>"
            output += "<li>IT SHOULD HAVE A MINIMUM OF 1 UPPERCASE CHARACTER</li>"
            output += "<li>IT SHOULD HAVE A MINIMUM OF 1 DIGIT</li>"
            output += "<li>IT SHOULD CONTAIN A MINIMUM OF 1 SPECIAL CHARACTER</li>"
            output += "</ul>"

        else:
            output += "YOU HAVE ALREADY REGISTERED, HEAD OVER TO THE LOGIN PAGE"

    message_begin = output
    return render_template('register.html', message=message_begin, msg_match=msg_match, is_safe=True)

@app.route('/check_password', methods=['POST'])
def check_password():
    output = ''
    output += "LOOKS LIKE YOU ARE NEW HERE !!<br>"
    output += "ENTER A STRONG COMPLEX PASSWORD THAT YOU WILL REMEMBER FOREVER<br>"
    output += "IF IT ASKS YOU FOR A PASSWORD REPEATEDLY CHECK WHETHER YOU MEET THE PASSWORD RULES!<br>"
    output += "COMPLEX PASSWORD RULES:<br>"
    output += "<ul>"
    output += "<li>PASSWORD TO BE EQUAL OR LONGER THAN 8 CHARACTERS</li>"
    output += "<li>IT SHOULD HAVE A MINIMUM OF 1 UPPERCASE CHARACTER</li>"
    output += "<li>IT SHOULD HAVE A MINIMUM OF 1 DIGIT</li>"
    output += "<li>IT SHOULD CONTAIN A MINIMUM OF 1 SPECIAL CHARACTER</li>"
    output += "</ul>"
    message_begin = output
    
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    if password != confirm_password:
        msg_match = "X PASSWORDS DO NOT MATCH X"
        return render_template('register.html', message=message_begin, msg_match=msg_match, is_safe=True)
        password = request.form['password']
        confirm_password = request.form['confirm_password']
    else:
        digit = spc = upper = 0
        for i in password:
            if i.isdigit() == True:
                digit += 1
            elif i.isupper() == True:
                upper += 1
            elif i in "!@#$%^&*()_-+|":
                spc += 1

        if len(confirm_password) < 8 or digit < 1 or spc < 1 or upper < 1:
            msg_match = "X PASSWORDS DO NOT MATCH X"
            return render_template('register.html', message=message_begin, msg_match=msg_match, is_safe=True)
            password = request.form['password']
            confirm_password = request.form['confirm_password']
        else:
            x = KeyPass.register_cont(confirm_password)

    return render_template('register.html', message=message_begin, new_output=x, is_safe=True)

if __name__ == '__main__':
    app.run(debug=True)
