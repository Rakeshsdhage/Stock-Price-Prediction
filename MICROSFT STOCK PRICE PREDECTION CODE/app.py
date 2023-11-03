
from flask import Flask, render_template, url_for, request,redirect,session, url_for
import sqlite3 as sql
import json
import plotly
import pandas as pd


from flask_bootstrap import Bootstrap
from model import Model

from datetime import datetime
from plotly.graph_objs import Scatter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'


@app.route("/")
def index():
    return render_template("home.html")

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route('/userlogin')
def userlogin():
    return render_template("userlogin.html")

@app.route('/userloginNext',methods=['GET','POST'])
def userloginNext():
    msg=None
    if (request.method == "POST"):
        username = request.form['username']
      
        upassword = request.form['upassword']
        
        with sql.connect("stock.db") as con:
            c=con.cursor()
            c.execute("SELECT username,upassword  FROM signup WHERE username = '"+username+"' and upassword ='"+upassword+"'")
            r=c.fetchall()
            for i in r:
                if(username==i[0] and upassword==i[1]):
                    session["logedin"]=True
                    session["fusername"]=username
                    return redirect(url_for("userhome"))
                else:
                    msg= "please enter valid username and password"
    
    return render_template("userlogin.html",msg=msg)

@app.route('/adminlogin')
def adminlogin():
    return render_template("adminlogin.html")

@app.route('/adminloginNext',methods=['GET','POST'])
def adminloginNext():
    msg=None
    if (request.method == "POST"):
        ausername = request.form['ausername']
        apassword = request.form['apassword']
        
        with sql.connect("stock.db") as con:
            c=con.cursor()
            c.execute("SELECT ausername,apassword  FROM adminlogin WHERE ausername = '"+ausername+"' and apassword ='"+apassword+"'")
            r=c.fetchall()
            for i in r:
                if(ausername==i[0] and apassword==i[1]):
                    session["logedin"]=True
                    session["fusername"]=ausername
                    return redirect(url_for("adminhome"))
                else:
                    msg= "please enter valid username and password"
    return render_template("adminlogin.html",msg=msg)


@app.route("/signup", methods = ["GET","POST"])
def signup():
    msg=None
    if(request.method=="POST"):
        if (request.form["uname"]!="" and request.form["uphone"]!="" and request.form["username"]!="" and request.form["upassword"]!=""):
            uname=request.form["uname"]
            uphone=request.form["uphone"]
            username=request.form["username"]
            password=request.form["upassword"]
            with sql.connect("stock.db") as con:
                c=con.cursor()
                c.execute("INSERT INTO  signup VALUES('"+uname+"','"+uphone+"','"+username+"','"+password+"')")
                msg = "Your account is created"
                con.commit()
        else:
            msg="Something went wrong"
    return render_template("signup.html", msg=msg)

@app.route('/userhome')
def userhome():
    return render_template("userhome.html")

@app.route('/usergallery')
def usergallery():
    return render_template("gallery.html")

@app.route('/adminhome')
def adminhome():
    return render_template("adminhome.html")


@app.route('/viewqueries')
def viewqueries():
    con=sql.connect("stock.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select question,answer from faq")
    rows=cur.fetchall()
    print(rows)
    return render_template("userviewfaq.html",rows=rows)

@app.route('/userlogout')
def userlogout():
	# Remove the session variable if present
	session.clear()
	return redirect(url_for('index'))

@app.route('/viewusers')
def viewusers():
    con=sql.connect("stock.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select uname,uphone,username from signup")
    rows=cur.fetchall()
    print(rows)
    return render_template("viewusers.html",rows=rows)



@app.route('/adminviewqueries')
def adminviewqueries():
    con=sql.connect("stock.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select question,answer from faq")
    rows=cur.fetchall()
    print(rows)
    return render_template("adminviewfaq.html",rows=rows)


@app.route("/addfaq", methods = ["GET","POST"])
def addfaq():
    msg=None
    if(request.method=="POST"):
        if (request.form["question"]!="" and request.form["answer"]!=""):
            question=request.form["question"]
            answer=request.form["answer"]
            with sql.connect("stock.db") as con:
                c=con.cursor()
                c.execute("INSERT INTO  faq VALUES('"+question+"','"+answer+"')")
                msg = "Your Query sent successfully "

                con.commit()
        else:
            msg="Something went wrong"


    return render_template("addfaq.html", msg=msg)


@app.route('/adminlogout')
def adminlogout():
	# Remove the session variable if present
	session.clear()
	return redirect(url_for('index'))


@app.route('/predict.html')
def predict():
 
    return render_template('predict.html')

@app.route('/result.html')
def predict_plot():

    #get the varaible inputs from the user
    companyname = request.args.get("companyname", "")
    ReferenceStartPeriod = request.args.get("ReferenceStartPeriod", "")
    ReferenceEndPeriod = request.args.get("ReferenceEndPeriod", "")
    PredictionDate = request.args.get("PredictionDate", "")

    
    stock_symbol = companyname.upper() #["WIKI/AMZN"]
    start_date = ReferenceStartPeriod #datetime(2017, 1, 1)
    end_date = ReferenceEndPeriod #datetime(2017, 12, 31)
    prediction_date = PredictionDate


    #build model
    arima = Model()

    #extract data from api
    arima.extract_data(stock_symbol, start_date, end_date)

    #train the data 
    arima.model_train()

    #Predict the stock price for a given date
    stock_predict = round(arima.predict(prediction_date)[1],2)
    
    #get the plot data 
    graph_data = arima.plot_data()


    #ids = ["graph-{}".format(i) for i, _ in enumerate(graph_data)]
    graphJSON = json.dumps(graph_data, cls = plotly.utils.PlotlyJSONEncoder)
    

    return render_template('result.html', stock_predict = stock_predict, graphJSON = graphJSON, prediction_date = prediction_date, stock_symbol = stock_symbol)#, ids =ids )

if __name__ == "__main__":
    app.run(debug=True)
