from flask import Flask,render_template,request,url_for,redirect,flash,session    
from flask_mysqldb import MySQL
import os
from flask_mail import Mail, Message
from random import randint

app=Flask(__name__) 

app.secret_key='*&^*)ihg'
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('email')
app.config['MAIL_PASSWORD'] = os.environ.get('password')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

mysql = MySQL(app)

@app.route("/",methods=["POST","GET"])
def frontpage():
    return render_template("frontpage.html")

@app.route("/login",methods=['POST','GET'])
def  login():
    return render_template("login.html")

@app.route("/forgotpwd",methods=["POST","GET"])
def forgotpwd():
    return render_template("forgotpwd.html")

@app.route("/newaccount",methods=["POST","GET"])
def newaccount():
    return render_template("newaccount.html")

@app.route("/verifymail",methods=["POST","GET"])
def verifymail():
    try:
        if request.method == "POST":
            email = request.form['email']
            session['email']=email
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user WHERE email=% s',(email,))
            row = cursor.fetchone()
            mysql.connection.commit()
            cursor.close() 
            if row:
                msg2 = 'Account Already Exists!'
                return render_template("newaccount.html",msg=msg2)
            otp = randint(1000000,9999999)
            msg = Message('Personal Expense Tracker--OTP for New account creation', sender = os.environ.get('email'), recipients = [email])
            msg.body = "OTP to verify your mail is  "+str(otp)
            mail.send(msg)
            msg2 = "OTP has been sent to your email. Enter OTP verify your email."
            return render_template("newaccount.html",email=session['email'],msg=msg2,otp=otp)
        else:
            return render_template("newaccount.html")
    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''

@app.route("/checkotp_newaccount",methods=["POST","GET"])
def checkotp_newaccount():
    try:
        if request.method == "POST":
            sent_otp = request.form['sent_otp']
            entered_otp = request.form['entered_otp']
            email = request.form['eml']
            session['email'] = email
            if int(sent_otp) == int(entered_otp):
                msg = "Hello "+email+" , email is verified! create your account"
                return render_template("createaccount.html",email=session['email'],msg10=msg)
            else:
                msg = "Incorrect OTP"
                return render_template("newaccount.html",email=email,msg9=msg)
        else:
            return render_template("newaccount.html")
    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Enter email again to receive OTP</h1>'''

@app.route("/resetpwd",methods=["POST","GET"])
def resetpwd():
    try:
        if request.method == "POST":
            email = request.form['email']
            session['email']=email
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user WHERE email=% s',(email,))
            row = cursor.fetchone()
            mysql.connection.commit()
            cursor.close()
            if row:
                otp = randint(1000000,9999999)
                msg = Message('Personal Expense Tracker--OTP for password reset', sender = os.environ.get('email'), recipients = [email])
                msg.body = "OTP to reset your password is "+str(otp)
                mail.send(msg)
                msg2 = "OTP has been sent to your email. Enter OTP to reset password."
                return render_template("forgotpwd.html",email=session['email'],msg=msg2,otp=otp)
            else:
                msg3 = "This email is not registered or Invalid email id"
                return render_template("forgotpwd.html",email=session['email'],msg=msg3)
        else:
            return render_template("forgotpwd.html")
    except:
            return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''

@app.route("/checkotp",methods=["POST","GET"])
def checkotp():
    try:
        if request.method == "POST":
            sent_otp = request.form['sent_otp']
            entered_otp = request.form['entered_otp']
            email = request.form['eml']
            session['email'] = email
            if int(sent_otp) == int(entered_otp):
                msg = "Hello "+email+" ,You can now change your password"
                return render_template("resetpwd.html",email=session['email'],msg10=msg)
            else:
                msg = "Incorrect OTP"
                return render_template("forgotpwd.html",email=email,msg9=msg)

        else:
            return render_template("forgotpwd.html",email=session['email'])
    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Enter email again to receive OTP</h1>'''

@app.route("/updatepwd",methods=["POST","GET"])
def updatepwd():
    try:
        if request.method == "POST":
            email = request.form['email']
            session['email']=email
            pwd = request.form['pwd']
            pwd1 = request.form['pwd1']
            if pwd != pwd1:
                msg = "Password does not match!"
                return render_template("resetpwd.html",email=session['email'],msg22=msg)
            else:
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE user SET password=% s WHERE email=% s',(pwd1,session['email']))
                mysql.connection.commit()
                cursor.close()
                msgs = "Password updated successfully for "+str(session['email'])
                return render_template("resetpwd.html",email=session['email'],msg22=msgs)

        else:
            email = request.form['email']
            session['email']=email
            return render_template("resetpwd.html",email=session['email'])

    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''
    

@app.route("/home", methods=["POST","GET"])
def home():
    try:
        if request.method == "POST":
            email = request.form['email']
            session['email']=email
            pwd = request.form['pwd']
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user WHERE email=% s AND password=% s',(email,pwd))
            row = cursor.fetchone()
            mysql.connection.commit()
            cursor.close()
            if row:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT balance FROM wallet WHERE email=% s',(email,))
                row1 = cursor.fetchone()
                mysql.connection.commit()
                cursor.close()
                if row1[0] == 0:
                    msg3 = "Wallet is empty! Add the amount of money that you have."
                    return render_template("home.html",msg=msg3,email=session['email'])

                msg3 = 'Available balance '+str(row1[0])
                return render_template("home.html",email=session['email'],msg=msg3)

            msg = 'Invalid Username or Password! Try again'
            return render_template("login.html",msg=msg)
        else:
            return render_template("home.html",email=session['email'])


    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''

    

@app.route("/home/<email>",methods=['GET','POST'])
def hm(email):
    return render_template("home.html",email=email)

    
        

@app.route("/createaccount", methods=["POST","GET"])
def createaccount():
    try:
        if request.method == "POST":
            name = request.form['name1']
            email = request.form['eml']
            default_balence = 0
            password = request.form['pwd1']
            password2 = request.form['pwd2']
            if password != password2 :
                msg = "password does not match!"
                return render_template("createaccount.html",msg=msg)
            else:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT * FROM user WHERE email=% s',(email,))
                row = cursor.fetchone()
                mysql.connection.commit()
                cursor.close() 
                if row:
                    msg2 = 'Account Already Exists!'
                    return render_template("createaccount.html",msg=msg2) 
                msg1 = "Successfully Created!"
                cursor = mysql.connection.cursor()
                cursor.execute(' INSERT INTO user VALUES(% s, % s, % s)',(name,email,password))
                cursor.execute('INSERT INTO wallet VALUES(% s, % s)',(email,default_balence))
                mysql.connection.commit()
                cursor.close()
                return render_template("createaccount.html",msg=msg1)
        return render_template("createaccount.html")
    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''

    

@app.route("/updatewallet/<email>",methods=["POST","GET"])
def updatewallet(email):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT balance FROM wallet WHERE email=% s',(email,))
    amount=cursor.fetchone()
    mysql.connection.commit()
    cursor.close()
    return render_template("updatewallet.html",email=email,amount=amount[0])

@app.route("/addmoney",methods=["POST","GET"])
def addmoney():
    try:
        if request.method == 'POST':
            email = request.form['email']
            amount = request.form['amount']
            session['email']=email
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT balance FROM wallet WHERE email=% s',(email,))
            bal = cursor.fetchone()
            mysql.connection.commit()
            cursor.close()

            newAmount = bal[0]+int(amount)

    
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE wallet SET balance=% s WHERE email=% s',(newAmount,email))
            mysql.connection.commit()
            cursor.close()

            cursor = mysql.connection.cursor()
            cursor.execute('SELECT balance FROM wallet WHERE email=% s',(email,))
            balance = cursor.fetchone()
            mysql.connection.commit()
            cursor.close()
            successmsg = 'Balance Updated. Available balance is '+str(newAmount)
            return render_template("updatewallet.html",email=email,successmsg=successmsg)
        else:
            return render_template("updatewallet.html",email=session['email'])

    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>''' 
    
    

@app.route("/addexpense/<email>",methods=['GET','POST'])
def addexpense(email):
    return render_template("addexpense.html",email=email)

@app.route("/newexpense/<email>",methods=["POST","GET"])
def newexpense(email):
    try:
        if request.method == "POST":
            category = request.form['expensetype']
            date = request.form['date']
            amount = request.form['amount']

            cursor = mysql.connection.cursor()
            cursor.execute('SELECT balance FROM wallet WHERE email=% s',(email,))
            balance = cursor.fetchone()
            mysql.connection.commit()
            cursor.close()

            cursor = mysql.connection.cursor()
            cursor.execute('SELECT amount,MONTH(date) as month, YEAR(date) as year FROM expenses WHERE email=% s',(email,))
            subtable = cursor.fetchall()
            mysql.connection.commit()
            cursor.close()

            cursor = mysql.connection.cursor()
            cursor.execute('SELECT MONTH(% s)',(date,))
            month_val = cursor.fetchone()
            mysql.connection.commit()
            cursor.close()

            cursor = mysql.connection.cursor()
            cursor.execute('SELECT YEAR(% s)',(date,))
            year_val = cursor.fetchone()
            mysql.connection.commit()
            cursor.close()

            total_amt=0
            for amt in subtable:
                if amt[1]==month_val[0] and amt[2]==year_val[0]:
                    total_amt+=int(amt[0])

            if balance[0]-int(amount) >= 0:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT budget FROM budget WHERE email=% s AND monthno=% s AND year=% s',(email,month_val[0],year_val[0]))
                budget_val = cursor.fetchone()
                mysql.connection.commit()
                cursor.close()
                if budget_val == None:
                    msg = 'Budget is not set for '+str(month_val[0])+'th month of '+str(year_val[0])+'. Please add budget before adding expenses!'
                    return render_template("addexpense.html",email=email,msg=msg)
                if (total_amt+int(amount)) > (int(budget_val[0])):
                    msg9 = 'EXPENSE LIMIT EXCEEDED w.r.t BUDGET! Mail has been sent regarding this.'
                    msg = Message('Personal Expense Tracker--Limit reached!',sender=os.environ.get('email'), recipients=[email])
                    msg.body = ('Warning! Your expense limit has reached for the '+str(month_val[0])+'th month of '+str(year_val[0])+ '. Update your limit if you want to add more expense for this perticular month')
                    mail.send(msg)
                    
                    return render_template("addexpense.html",email=email,msg=msg9)
                Available = balance[0] - int(amount)
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE wallet SET balance=% s WHERE email=% s',(Available,email))
                cursor.execute('INSERT INTO expenses(date,category,amount,email) VALUES(% s, % s, % s, % s)',(date,category,amount,email))
                mysql.connection.commit()
                cursor.close()
                msg = 'Expense added successfully. Balance Updated. Available Balance  : '+str(Available)
                return render_template("addexpense.html",msg=msg,email=email)

            else:
                msg = 'Not enough money in wallet!, could not add expense. Update wallet to proceed.'
                return render_template("addexpense.html",msg=msg,email=email)
    
        else:
            return render_template("addexpense.html",email=email)
    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''

    

@app.route("/addbudget/<email>")
def addbudget(email):
    return render_template("addbudget.html",email=email)
        
@app.route("/newbudget/<email>",methods=["POST","GET"])
def newbudget(email):
    try:
        if request.method == "POST":
            month = request.form['months']
            budget = request.form['budget']
            year = request.form['years']

            cursor = mysql.connection.cursor()
            cursor.execute('SELECT budget FROM budget WHERE email=% s AND monthno=% s AND year=% s',(email,month,year))
            val = cursor.fetchone()
            if val:
                cursor.execute('UPDATE budget set budget=% s WHERE email=% s AND monthno=% s AND year=% s',(budget,email,month,year))
            else:
                cursor.execute('INSERT INTO budget VALUES(% s, % s, % s, % s)',(email,month,budget,year))

            mysql.connection.commit()
            cursor.close()
            msg = 'Limit Updated Successfully.'
            return render_template("addbudget.html",email=email,msg=msg)

        else:
            return render_template("addbudget.html",email=email)
    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''

    

@app.route("/viewallexpenses/<email>",methods=["POST","GET"])
def viewallexpenses(email):
    return render_template("expensetable.html",email=email)

@app.route("/expensetable/<email>",methods=["POST","GET"])
def expensetable(email):
    try:
        if request.method == 'POST':
            year = request.form['years']
            month = request.form['months']

            cursor = mysql.connection.cursor()
            cursor.execute('SELECT MONTH(date) as month, YEAR(date) as year, amount,category FROM expenses WHERE email=% s AND MONTH(date)=% s AND YEAR(date)=% s',(email,month,year))
            subtable = cursor.fetchall()
            mysql.connection.commit()
            cursor.close()

            if len(subtable) == 0:
                msg = 'There are no expenses to show in '+str(month)+'th month of '+str(year)
                return render_template("expensetable.html",email=email,msg=msg)

            return render_template("expensetable.html",table=subtable,email=email) 

        else:
            return render_template("expensetable.html",email=email)

    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''

    
    

@app.route("/graphs/<email>",methods=['POST','GET'])
def graphs(email):
    return render_template("graphs.html",email=email)

@app.route("/getgraph/<email>",methods=['GET','POST'])
def getgraph(email):
    try:
        session['email']=email
        if request.method == 'POST':
            year = request.form['years']
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT MONTH(date) as month, amount FROM expenses WHERE email=% s AND YEAR(date)=% s',(email,year))
            subtable = cursor.fetchall()
            mysql.connection.commit()
            cursor.close()
    
            if len(subtable) == 0:
                msg = 'There are no expenses to show in '+str(year)
                return render_template("graphs.html",email=email,msg=msg)
            labels=[]
            values=[]
            for row in subtable:
                labels.append(row[0])
                values.append(row[1])
            return render_template("graphs.html",labels=labels,values=values,email=email,year=year)

        else:
            return render_template("graphs.html",email=session['email'])

    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''

    


@app.route("/viewlimits/<email>",methods=['POST','GET'])
def viewlimits(email):
    return render_template("viewlimits.html",email=email)

@app.route("/getlimits/<email>",methods=['POST','GET'])
def getlimits(email):
    try:
        if request.method == "POST":
            year = request.form['years']
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT year,monthno,budget FROM budget WHERE email=% s AND year=% s',(email,year))
            subtable = cursor.fetchall()
            mysql.connection.commit()
            cursor.close()
            if len(subtable) == 0:
                msg = 'There are no Limits set in '+str(year)
                return render_template("viewlimits.html",email=email,msg=msg)
            return render_template("viewlimits.html",table=subtable,email=email)

        else:
            return render_template("viewlimits.html",email=email)

    except:
        return '''<h1 style="text-align:center;color:red;">Something Went Wrong <br> Check your Internet connection!</h1>'''

    


if __name__ == "__main__":
    app.run(debug=True)