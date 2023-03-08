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

account_skey = None
master_skey = None
mb_id = None
new_host = None
new_output = None

def BASE_encode(plain_text):
    numbers = '0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63'
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    encode_ref = dict(zip(numbers.split(),list(characters)))     #DICTIONARY THAT WILL BE USED FOR ENCODED TEXT
    decode_ref = dict(zip(list(characters),numbers.split()))     #DICTIONARY THAT WILL BE USED FOR DECODED TEXT
    binary = []
    total_bin = ''
    divisions_six = []
    final = ''
    
    for ch in plain_text:
        a = bin(ord(ch))[2:]
        extra = 8 - len(a)
        binary += [(extra * '0') + a]
    for i in binary:
        total_bin += i

    total_bin_list = list(total_bin)    #CREATES LIST OF THE COMBINED BITS

    length = len(total_bin_list)        #TO CHECK THE LENGTH FOR 6 DIVISION
    leftover = length % 6               #IF NUMBER NOT PROPERLY DIVISIBLE BY 6
    extra = 6 - leftover
    length -= leftover                  #REMAINING LENGTH IN MULTIPLE OF 6
    leftover_list = total_bin_list[-(leftover):]    #LIST OF EXTRA ELEMENTS

    for dlt in range(leftover):         #TO REMOVE EXTRA ELEMENTS
        total_bin_list.pop()

    if extra < 6:                       #TO DEAL WITH THE EXTRA BITS THAT ARE LESS THAN 6
        for m in range(extra):
            leftover_list.append('0')

    m = 0
    for i in range(6,length + 1,6):     #FOR CREATING 6 BITS
        n = i
        divisions_six += [''.join(total_bin_list[m:n])]
        m = n
        if m == length + 1:
            break

    for sm in divisions_six:
        total = 0
        total = total + int(sm[0])*32 + int(sm[1])*16 + int(sm[2])*8 + int(sm[3])*4 + int(sm[4])*2 + int(sm[5])
        final += encode_ref[str(total)]
    if len(leftover_list) == 6:
        total = 0
        total = total + int(leftover_list[0])*32 + int(leftover_list[1])*16 + int(leftover_list[2])*8 + int(leftover_list[3])*4 + int(leftover_list[4])*2 + int(leftover_list[5])
        final += encode_ref[str(total)]

    return final

def BASE_decode(plain_text):
    numbers = '0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63'
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    encode_ref = dict(zip(numbers.split(),list(characters)))     #DICTIONARY THAT WILL BE USED FOR ENCODED TEXT
    decode_ref = dict(zip(list(characters),numbers.split()))     #DICTIONARY THAT WILL BE USED FOR DECODED TEXT
    binary = []
    total_bin = ''
    divisions_eight = []
    final = ''

    for ch in plain_text:
        a = bin(int(decode_ref[ch]))[2:]
        extra = 6 - len(a)
        binary += [(extra * '0') + a]
    for i in binary:
        total_bin += i

    total_bin_list = list(total_bin)

    length = len(total_bin)
    leftover = length % 8
    length -= leftover
    for j in range(leftover):
        total_bin_list.pop()

    m = 0
    for k in range(8,length + 1,8):     #FOR CREATING 8 BITS
        n = k
        divisions_eight += [''.join(total_bin_list[m:n])]
        m = n
        if m == length + 1:
            break

    for sm in divisions_eight:
        total = 0
        total = total + int(sm[0])*128 + int(sm[1])*64 + int(sm[2])*32 + int(sm[3])*16 + int(sm[4])*8 + int(sm[5])*4 + int(sm[6])*2 + int(sm[7])
        final += chr(total)

    return final

def ROT_encode(data):      #encrypt data
    dic = {'a': 'n', 'b': 'o', 'c': 'p', 'd': 'q', 'e': 'r', 'f': 's', 'g': 't', 'h': 'u', 'i': 'v', 'j': 'w', 'k': 'x', 'l': 'y', 'm': 'z', 'n': 'a', 'o': 'b', 'p': 'c', 'q': 'd', 'r': 'e', 's': 'f', 't': 'g', 'u': 'h', 'v': 'i', 'w': 'j', 'x': 'k', 'y': 'l', 'z': 'm', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0', 'A': 'N', 'B': 'O', 'C': 'P', 'D': 'Q', 'E': 'R', 'F': 'S', 'G': 'T', 'H': 'U', 'I': 'V', 'J': 'W', 'K': 'X', 'L': 'Y', 'M': 'Z', 'N': 'A', 'O': 'B', 'P': 'C', 'Q': 'D', 'R': 'E', 'S': 'F', 'T': 'G', 'U': 'H', 'V': 'I', 'W': 'J', 'X': 'K', 'Y': 'L', 'Z': 'M', '-': '-', '_': '_', '=': '=', '+': '+', '.': '.', ',': ',', '<': '<', '>': '>', '/': '_', ' ': ' ', '\\': '\\', '|': '|', '?': '?'}
    encrypted = ''
    for i in data:
        encrypted += dic[i]
    return encrypted

def ROT_decode(data):      #decrypt data
    dic = {'a': 'n', 'b': 'o', 'c': 'p', 'd': 'q', 'e': 'r', 'f': 's', 'g': 't', 'h': 'u', 'i': 'v', 'j': 'w', 'k': 'x', 'l': 'y', 'm': 'z', 'n': 'a', 'o': 'b', 'p': 'c', 'q': 'd', 'r': 'e', 's': 'f', 't': 'g', 'u': 'h', 'v': 'i', 'w': 'j', 'x': 'k', 'y': 'l', 'z': 'm', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0', 'A': 'N', 'B': 'O', 'C': 'P', 'D': 'Q', 'E': 'R', 'F': 'S', 'G': 'T', 'H': 'U', 'I': 'V', 'J': 'W', 'K': 'X', 'L': 'Y', 'M': 'Z', 'N': 'A', 'O': 'B', 'P': 'C', 'Q': 'D', 'R': 'E', 'S': 'F', 'T': 'G', 'U': 'H', 'V': 'I', 'W': 'J', 'X': 'K', 'Y': 'L', 'Z': 'M', '-': '-', '_': '_', '=': '=', '+': '+', '.': '.', ',': ',', '<': '<', '>': '>', '_': '/', ' ': ' ', '\\': '\\', '|': '|', '?': '?'}
    decrypted = ''
    for i in data:
        decrypted += dic[i]
    return decrypted

def ALGO(user):
    lower_dic = {'a': '01', 'b': '02', 'c': '03', 'd': '04', 'e': '05', 'f': '06', 'g': '07', 'h': '08', 'i': '09', 'j': '10', 'k': '11', 'l': '12', 'm': '13', 'n': '14', 'o': '15', 'p': '16', 'q': '17', 'r': '18', 's': '19', 't': '20', 'u': '21', 'v': '22', 'w': '23', 'x': '24', 'y': '25', 'z': '26'}
    upper_dic = {'A': '01', 'B': '02', 'C': '03', 'D': '04', 'E': '05', 'F': '06', 'G': '07', 'H': '08', 'I': '09', 'J': '10', 'K': '11', 'L': '12', 'M': '13', 'N': '14', 'O': '15', 'P': '16', 'Q': '17', 'R': '18', 'S': '19', 'T': '20', 'U': '21', 'V': '22', 'W': '23', 'X': '24', 'Y': '25', 'Z': '26'}
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    output = ''
    summ = 0
    mod = 0

    for i in user:
        if i.isupper() == True:
            summ += (2 * int(upper_dic[i])) + int(upper_dic[i][1])
            mod = summ % 26
            output += upper[mod - 1]
            summ = 0
        elif i.islower() == True:
            summ += (2 * int(lower_dic[i])) + int(lower_dic[i][1])
            mod = summ % 26
            output += lower[mod - 1]
            summ = 0
        else:
            output += i

    return output

def host():             #FOR THE SYSTEM'S HOSTNAME
    hostin = ''
    for i in gethostname():
        if i.isalnum() == True:
            hostin += i
        else:
            pass

    return hostin

def motherboard_nt():   #BACKUP KEY WINDOWS
    import pythoncom
    pythoncom.CoInitialize()

    c = wmi.WMI()
    m = c.Win32_BaseBoard()[0]
    mbo_id = m.SerialNumber.strip()

    return mbo_id

def motherboard_posix():#BACKUP KEY FOR POSIX SYSTEMS
    try:
        cmd = ['dmidecode', '-s', 'baseboard-serial-number']
        result = subprocess.check_output(cmd)
        return result.decode().strip()
    except subprocess.CalledProcessError:
        return None

def private_bytes():    #CREATES A PRIVATE KEY IN BYTES 44 STR CHARS
    return Fernet.generate_key()

def master_key():
    global account_skey
    global master_skey

    account_bkey = private_bytes()  #KEY THAT WILL BE ENCRYPTED AND STORED IN THE DB
    master_bkey = private_bytes()   #KEY THAT WILL ENCRYPT THE KEY BEING STORED IN DB
    account_skey = str(account_bkey)[2:-1]
    master_skey = str(master_bkey)[2:-1]
    f = Fernet(master_bkey)
    token = f.encrypt(account_bkey)
    return str(token)[2:-1]

def ac_key():
    if os.name == 'nt':
        creds_file = os.path.expanduser("~") + "\\creds.txt"
        f = open(creds_file, "r")
        a = f.read()
        master_key = a[-44:].encode('utf-8')     #IN BYTES
        account_key = a[500:544].encode('utf-8') #IN BYTES
        f.close()
        f = Fernet(account_key)                  #KEY READY TO ENCRYPT
        return f

    elif os.name == 'posix':
        creds_file = os.path.expanduser("~/Documents/creds.txt")
        f = open(creds_file, "r")
        a = f.read()
        master_key = a[-44:].encode('utf-8')     #IN BYTES
        account_key = a[500:544].encode('utf-8') #IN BYTES
        f.close()
        f = Fernet(account_key)                  #KEY READY TO ENCRYPT
        return f        

def backup_file():
    if os.name == 'nt':
        conn = sqlite3.connect(os.path.expanduser("~") + '\\db.db')
    elif os.name == 'posix':
        conn = sqlite3.connect(os.path.expanduser("~") + '/Documents/db.db')

    data = []
    columns = ["Service","Username", "Password"]
    cur = conn.cursor()
    tables = []
    for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        tables += [i[0]]

    user = []
    password = []
    ymd = []
    today_date = date.now()
    for i in tables:
        for j in cur.execute('SELECT * FROM ' + i):
            if j[0] == 'null':
                user += [j[0]]
            else:    
                user += [str(ac_key().decrypt(j[0].encode('utf-8')))[2:-1]]
            pass_string = j[1]
            if pass_string == 'null':
                password += [j[1]]
            else:
                password += [str(ac_key().decrypt(pass_string.encode('utf-8')))[2:-1]]
            if 0 in [j[2], j[3], j[4]]:
                ymd.append([0, 0, 0])
            else:
                ymd.append([j[4], j[3], j[2]])
        if password[-1] in 'null':
            continue
        else:
            older_date = date(ymd[-1][0], ymd[-1][1], ymd[-1][2])
            data.append([i, user[-1], password[-1]])

    conn.close()
    if os.name == 'nt':
        output_file = os.path.expanduser("~") + '\\backup.csv'
    elif os.name == 'posix':
        output_file = os.path.expanduser("~") + '/Documents/backup.csv'
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(data)

    f.close()
    success = "Backup file stored in: " + output_file
    return success    

def db_check():
    global new_host     #ENCODES THE HOST NAME AFTER STRING SORT
    new_host = ROT_encode(BASE_encode(host()))
    global mb_id        #IMP MOTHERBOARD ID

    if os.name == 'nt':    
        if 'db.db' not in os.listdir(os.path.expanduser("~") + "\\"):
            #f = open(os.path.expanduser("~") + '\\db.db','x')
            #f.close()
            services = ['AMAZON_PRIME', 'ATM_PIN', 'BANKING_APP', 'DISCORD', 'FACEBOOK', 'GOOGLE', 'HOTSTAR', 'INSTAGRAM', 'MICROSOFT', 'NETFLIX', 'SNAPCHAT', 'SPOTIFY', 'TELEGRAM', 'TWITTER', 'UPI_PIN']
            conn = sqlite3.connect(os.path.expanduser("~") + '\\db.db')
            cur = conn.cursor()
            for i in services:
                cur.execute('CREATE TABLE ' + i.upper() + '(user text, password text, date integer, month integer, year integer)')
                cur.execute('INSERT INTO ' + i.upper() + ' VALUES("null" , "null", 0, 0, 0)')
                conn.commit()
            conn.close()
        else:
            pass

        if new_host+'.db' not in os.listdir(os.path.expanduser("~") + "\\"):
            mb_id = motherboard_nt() + '00'
            new_host = ROT_encode(BASE_encode(host()))
            conn = sqlite3.connect(os.path.expanduser("~") + "\\" + new_host + ".db")
            cur = conn.cursor()
            for i in range(4):
                cur.execute('CREATE TABLE ' + mb_id[i*4:(i+1)*4] + '(gibberish text)')
                cur.execute('INSERT INTO ' + mb_id[i*4:(i+1)*4] + ' VALUES(?)',[master_key()[i*35:(i+1)*35]])
                conn.commit()
            conn.close()
        else:
            pass

    elif os.name == 'posix':
        if 'db.db' not in os.listdir(os.path.expanduser("~") + '/Documents/'):
            #f = open(os.path.expanduser("~") + '/Documents/db.db','x')
            #f.close()
            services = ['AMAZON_PRIME', 'ATM_PIN', 'BANKING_APP', 'DISCORD', 'FACEBOOK', 'GOOGLE', 'HOTSTAR', 'INSTAGRAM', 'MICROSOFT', 'NETFLIX', 'SNAPCHAT', 'SPOTIFY', 'TELEGRAM', 'TWITTER', 'UPI_PIN']
            conn = sqlite3.connect(os.path.expanduser("~") + '/Documents/db.db')
            cur = conn.cursor()
            for i in services:
                cur.execute('CREATE TABLE ' + i.upper() + '(user text, password text, date integer, month integer, year integer)')
                cur.execute('INSERT INTO ' + i.upper() + ' VALUES("null" , "null", 0, 0, 0)')
                conn.commit()
            conn.close()
        else:
            pass

        if new_host+'.db' not in os.listdir(os.path.expanduser("~") + "/Documents/"):
            mb_id = motherboard_posix() + '00'
            new_host = ROT_encode(BASE_encode(host()))
            conn = sqlite3.connect(os.path.expanduser("~") + "/Documents/" + new_host + ".db")
            cur = conn.cursor()
            for i in range(4):
                cur.execute('CREATE TABLE ' + mb_id[i*4:(i+1)*4] + '(gibberish text)')
                cur.execute('INSERT INTO ' + mb_id[i*4:(i+1)*4] + ' VALUES(?)',[master_key()[i*35:(i+1)*35]])
                conn.commit()
            conn.close()
        else:
            pass

    return mb_id

def register_cont(confirm_password):
    db_check()
    if os.name == 'nt':
        first = last = ''
        for i in range(500):
            first += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+|')
            last += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+|')
        text = first + account_skey + ALGO(ROT_encode(BASE_encode(confirm_password))) + last + master_skey
        f = open(os.path.expanduser("~") + "\\creds.txt", 'w')
        f.write(text)
        f.close()

        new_output = ''
        new_output += "!!BACKUP KEY!!: " + mb_id
        new_output += "<br>Store it in a safe place as it will help you backup your passwords when needed."

    elif os.name == 'posix':        
        first = last = ''
        for i in range(500):
            first += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+|')
            last += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+|')

        text = first + account_skey + ALGO(ROT_encode(BASE_encode(confirm_password))) + last + master_skey
        f = open(os.path.expanduser("~") + '/Documents/creds.txt','w')
        f.write(text)
        f.close()

        new_output = ''
        new_output += "!!BACKUP KEY!!: " + mb_id
        new_output += "<br>Store it in a safe place as it will help you backup your passwords when needed."
        new_output += "<br>REGISTRATION COMPLETE, WELCOME ONBOARD!"

    return new_output
fail = 0

def signin(nsfw, check):
    global fail
    if ALGO(ROT_encode(BASE_encode(nsfw))) not in check:
        fail += 1
        latter =  "X WRONG PASSWORD X"
        return latter
    else:
        latter = "LOGIN SUCCESSFUL"
        return latter

def addition(option, user, password, num_range):
    if option not in num_range:
        return 'Invalid Option!'
    else:
        if os.name == 'nt':
            conn = sqlite3.connect(os.path.expanduser("~") + '\\db.db')
        elif os.name == 'posix':
            conn = sqlite3.connect(os.path.expanduser("~") + '/Documents/db.db')
        cur = conn.cursor()
        dec = ac_key()
        old_creds = []
        tables = []
        num_range = ''
        for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
            tables += [i[0]]
        for j in cur.execute('SELECT password FROM ' + tables[int(option)]):
            x = j[0]
            if x == 'null':
                old_creds += [x]
            else:
                old_creds += [dec.decrypt(j[0].encode('utf-8'))]

        if password in old_creds:
            return 'This password has already been used in the past. Add another one'
        else:
            ex_values = [str(dec.encrypt(user.encode('utf-8')))[2:-1], str(dec.encrypt(password.encode('utf-8')))[2:-1], date.now().day, date.now().month, date.now().year]
            cur.execute('INSERT INTO ' + tables[int(option)] + ' VALUES(?, ?, ?, ?, ?)',ex_values)
            conn.commit()
            conn.close()
        return "Password Added Successfully"

def view():
    x = pt()
    x.field_names = ["SERVICE","USERNAME", "PASSWORD", "PASSWORD AGE DAY(S)"]
    if os.name == 'nt':
        conn = sqlite3.connect(os.path.expanduser("~") + '\\db.db')
    elif os.name == 'posix':
        conn = sqlite3.connect(os.path.expanduser("~") + '/Documents/db.db')

    cur = conn.cursor()
    tables = []
    for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        tables += [i[0]]

    user = []
    password = []
    ymd = []
    today_date = date.now()
    for i in tables:
        for j in cur.execute('SELECT * FROM ' + i):
            if j[0] == 'null':
                user += [j[0]]
            else:    
                user += [str(ac_key().decrypt(j[0].encode('utf-8')))[2:-1]]
            pass_string = j[1]
            if pass_string == 'null':
                password += [j[1]]
            else:
                password += [str(ac_key().decrypt(pass_string.encode('utf-8')))[2:-1]]
            if 0 in [j[2], j[3], j[4]]:
                ymd.append([0, 0, 0])
            else:
                ymd.append([j[4], j[3], j[2]])
        if password[-1] in 'null':
            x.add_row([i, 'Credentials not yet saved', '', ''])
        else:
            older_date = date(ymd[-1][0], ymd[-1][1], ymd[-1][2])
            x.add_row([i, user[-1], password[-1], (today_date - older_date).days])

    conn.close()
    return x.get_html_string()

def service(ser):
    output = 'AVAILABLE SERVICES:-- <br>'
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

    if ser.upper() in tables:
        err = "Service already exists..."
    else:
        cur.execute('CREATE TABLE ' + ser.upper() + '(user text, password text, day integer, month integer, year integer)')
        cur.execute('INSERT INTO ' + ser.upper() + ' VALUES("null", "null", 0, 0, 0)')
        success = 'Service ' + ser.upper() + ' added!\n'
        conn.commit()
        conn.close()

    return err, success

def drop(opt):
    err = ''
    success = ''
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
        num_range += str(i)

    if opt not in num_range:
        err = 'Invalid Choice'
    else:
        cur.execute('DROP TABLE ' + tables[int(opt)])
        conn.commit()
        conn.close()
        success = 'Service ' + tables[int(opt)] + ' removed!'

    return err, success

fail = 0
def backup(password, mm):
    err = ''
    global fail
    if os.name == 'nt':
        f = open(os.path.expanduser("~") + '\\creds.txt')
        conn = sqlite3.connect(os.path.expanduser("~") + '\\' + ROT_encode(BASE_encode(host())) + '.db')
    elif os.name == 'posix':
        f = open(os.path.expanduser("~") + '/Documents/creds.txt')
        conn = sqlite3.connect(os.path.expanduser("~") + '/Documents/' + ROT_encode(BASE_encode(host())) + '.db')

    secret = f.read()
    f.close()
    if fail < 2:
        if ALGO(ROT_encode(BASE_encode(password))) not in secret:
            fail += 1
            err = "Password doesn't match. Try Again!"
            return err
        else:                
            cur = conn.cursor()
            tables = []
            ver = ''
            for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
                tables += [i[0]]

            for i in tables:
                ver += i

            if mm not in ver:
                err = "Wrong backup key!"
                return err
            else:
                return backup_file()
    else:
        err = "Wrong password entered too many times!"
        return err
#PASSWORD=PASSWORD MM=BACKUP KEY RETURNED EVERYTHING IN ERR AND BACKUP FILE, IF NEEDED CHECK STRING IN NOT IN, TO USE ERROR
