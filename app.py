from flask import Flask, render_template, g, request
import sqlite3 as sql
from  datetime import datetime
def dateconv(date):
    return datetime.strftime(datetime.strptime(str(date['entry_date']),
                                               "%Y%m%d"),
                             "%d %B, %Y")
app = Flask(__name__)
# Establish a connection
app.config['DEBUG'] = True
def dbConnect():
    con = sql.connect('db/data.db')
    con.row_factory = sql.Row
    return con
# Gets the database
def get_db():
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite3_db = dbConnect()
    return g.sqlite3_db
# switches off con if remained open
@app.teardown_appcontext
def Close(error):
    if hasattr(g, 'sqlite3_db'):
        g.sqlite3_db.close()
# Index page or main page
@app.route('/',methods = ['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        forms = request.form['date']
        disp_date = datetime.strftime(datetime.strptime(forms,
                                                   "%Y-%m-%d"),
                                 "%d %B, %Y")
        database_date = datetime.strftime(datetime.strptime(forms,
                                                   "%Y-%m-%d"),
                                 "%Y%m%d")
        db.execute('Insert into log_date(entry_date) values(?)',\
            [database_date])
        db.commit()
    result = db.execute('select id,entry_date from log_date order by entry_date desc')
    results = result.fetchall()
    ress = []
    total = []
    for i in results:
        solver = db.execute('select food_id from food_date where log_date_id=?',[i['id']])
        solver  = solver.fetchall()
        totals = {'name':0,'p':0,'c':0,'f':0,'total':0}
        for j in solver:
            foods = db.execute('select * from food where id=?',[j['food_id']])
            res =  foods.fetchall()
            # print(res[0]['protien'])
            totals['p']+=res[0]['protien']
            totals['c']+=res[0]['carbohydrate']
            totals['f']+=res[0]['fat']
            totals['total']+=res[0]['calories']
        single_date = {}
        single_date['total'] = totals
        d = datetime.strptime(str(i['entry_date']),"%Y%m%d")
        single_date['disp_date'] = datetime.strftime(d, "%d %B, %Y")
        single_date['entry_date'] = i['entry_date']
        ress.append(single_date)
    return render_template('home.html',results = ress)

# View Page
@app.route('/view/<date>', methods=['GET','POST'])
def view(date):
    db = get_db()
    # print(date)
    cur = db.execute('select id, entry_date from log_date where entry_date = ?',[date])
    res = cur.fetchone()
    # print(res['id'])
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into food_date (food_id, log_date_id) values(?, ?)',
                   [request.form['food-select'],
                   res['id']])
        db.commit()

    curs = db.execute('select food_id from food_date where log_date_id == ?',[res['id']])
    result = curs.fetchall()
    finals = []
    totals = {'name':0,'p':0,'c':0,'f':0,'total':0}
    for i in result:
        r = db.execute('select * from food where id = ?',[i['food_id']])
        ress = r.fetchall()
        totals['p']+=ress[0]['protien']
        totals['c']+=ress[0]['carbohydrate']
        totals['f']+=ress[0]['fat']
        totals['total']+=ress[0]['calories']
        finals.append({'name': ress[0]['name'],
                       'p':ress[0]['protien'],
                       'c':ress[0]['carbohydrate'],
                       'f': ress[0]['fat'],
                       'total':ress[0]['calories']
                       })
    disp_date = dateconv(res)
    cur = db.execute('select id, name from food')
    ress = cur.fetchall()
    return render_template('day.html',date=disp_date, food_res= ress,
                           date_food = finals,
                           total = totals, in_date=res['entry_date'])
# Food Page as well as add food depends on the type
# Of server request
@app.route('/food', methods =['GET', 'POST'])
def food():

    db = get_db()
    if request.method == 'POST':
        forms = [request.form['protein'],
                 request.form['carbs'],
                 request.form['fat']]
        forms = list(map(int,forms[::-1]))
        forms.append(request.form['food-name'])
        forms = forms[::-1]
        forms.append(forms[3] * 9 + forms[1] * 4 + forms[2] *4)
        # This code above is peice of art

        db.execute('Insert into food(name, protien, carbohydrate, fat, calories) values(?, ?, ?, ?, ?)',\
            forms)
        db.commit()

    cur = db.execute('Select * from food')
    results = cur.fetchall()
        # Totally legit way to check working or not
    return render_template('add_food.html',results = results)


if __name__ == "__main__":
    app.run(debug = True)
