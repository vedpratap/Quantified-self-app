#------Imports----------
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import LoginManager,login_required, current_user, login_user, logout_user, UserMixin
from jinja2 import *
from flask_sqlalchemy import *
import flask_excel as excel
import pandas as pd
import os


#--------Initialization-----------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(id):
    return Customer.query.get(int(id))



#------Database----------
db = SQLAlchemy(app)
class Customer(db.Model, UserMixin):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True, autoincrement =True)
    fullname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    city = db.Column(db.String(150))
    tracker = db.relationship('Tracker')
    log = db.relationship('Log')

class Tracker(db.Model):
    __tablename__ = 'tracker'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    details = db.Column(db.String(150))
    tracker_type = db.Column(db.String(150))
    settings = db.Column(db.String(150))
    log = db.relationship('Log')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(150))
    value = db.Column(db.Integer)
    notes = db.Column(db.String(150))
    tracker_id = db.Column(db.Integer, db.ForeignKey('tracker.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    added_date_time = db.Column(db.String(150))


class Options(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    option = db.Column(db.String(1500))
    


#-------Flask-------------------
# Pass the required route to the decorator.

#------------Login---------------------------------------------------
@app.route("/", methods =['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user1 = Customer.query.filter_by(email=email, password=password).first()
        if user1:
            tracker = Tracker.query.filter_by(customer_id = user1.id)
            flash("Login successful")
            login_user(user1, remember=True)
            return redirect('/home')
        else:
            flash("Something went wrong!! Please check your email and password.")
    return render_template('login.html')


#--------------Home/Dashboard--------------------------
@app.route('/home')
@login_required
def home():
    import datetime
    now = datetime.datetime.now()
    from datetime import datetime
    trackers = Tracker.query.filter_by(customer_id = current_user.id).all()
    name = []
    for i in trackers:
        name.append(i.name)
    l = len(name)
    ltime = []
    lvalue = []
    for i in trackers:
        logs = Log.query.filter_by(customer_id = current_user.id, tracker_id = i.id).all()
        if len(logs) >= 1:
            last_date_time = logs[len(logs)-1].added_date_time
            d1 = datetime.strptime(last_date_time, "%Y-%m-%d %H:%M:%S.%f")
            last_update = now - d1
            last_updated_str = str(last_update)
            hour = last_updated_str[:1]
            min1 = last_updated_str[2]
            min2 = last_updated_str[3]
            minute = min1 + min2
            sec1 = last_updated_str[5]
            sec2 = last_updated_str[6]
            second = sec1 + sec2
            last_review = (hour + 'hr' + ' ' + minute + 'mins' + ' ' + second + 'Sec' + ' ' + 'ago')
            last_value = logs[len(logs)-1].value
            ltime.append(last_review)
            lvalue.append(last_value)
        else:
            ltime.append('No data')
            lvalue.append('No data')
    tracker = Tracker.query.all()
    return render_template("home.html", user=current_user, tracker=tracker,  name = name, l = l, ltime = ltime, lvalue = lvalue)


#-----------------Sign Up---------------------------
@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        fullname = request.form['name']
        city = request.form['city']
        password = request.form['password']

        user = Customer.query.filter_by(email=email).first()
        if user:
            flash('Email already exist. Please use different email id.')
        else:
            # Add user to the database
            new_user = Customer(fullname=fullname, email=email,  password=password, city=city)
            db.session.add(new_user)
            db.session.commit()
            flash("Sign up successfully.")
            return redirect('/')
    return render_template('signup.html')


#-------------Add Tracker---------------------------
@app.route("/addtracker", methods = ['GET', 'POST'])
@login_required
def addtracker():
    if request.method == 'POST':
        name = request.form['name']
        details = request.form['details']
        setting = request.form['setting']
        tracker_type = request.form['type']
        option = request.form['options']
        tracker = Tracker.query.filter_by(name = name).first()
        if tracker and tracker.customer_id == current_user.id:
              flash("You have already created this tracker. Please try different one.")
        elif tracker_type != 'Multiple choice':
            new_tracker = Tracker(name=name, details=details, tracker_type=tracker_type,settings = setting, customer_id=current_user.id)
            db.session.add(new_tracker)
            db.session.commit()
            flash("Tracker has been created.")
            return redirect('/home')
        else:
            new_tracker = Tracker(name=name, details=details, tracker_type=tracker_type,settings = setting, customer_id=current_user.id)
            db.session.add(new_tracker)
            db.session.commit()
            newdata = Options(name = name, customer_id = current_user.id, option = option)
            db.session.add(newdata)
            db.session.commit()
            flash("Tracker has been created.")
            return redirect('/home')
    return render_template('addtracker.html', user = current_user )   
  
#---------------------Remove/Delete Tracker---------------------
@app.route('/removetracker/<int:tracker_id>', methods = ['GET', 'POST'])
@login_required
def removetracker(tracker_id):
    try:
        Tracker_details = Tracker.query.get(tracker_id)
        Tracker_name = Tracker_details.name
        db.session.delete(Tracker_details)
        db.session.commit()
        data = Options.query.filter_by(customer_id = current_user.id, name = Tracker_name).first()
        if data:
            db.session.delete(data)
            db.session.commit()
        logs = Log.query.filter_by(customer_id = current_user.id, tracker_id = tracker_id).all()
        if logs:
            db.session.delete(logs)
            db.session.commit()
        flash("Tracker has been removed Successfully.")
        return redirect('/home')
    except:
        return redirect('/home')
        
    


#------------------Edit Tracker----------------------------
@app.route('/edittracker<int:tracker_id>', methods = ['GET', 'POST'])
@login_required
def edittracker(tracker_id):
    this_tracker = Tracker.query.get(tracker_id)
    this_tracker_name = this_tracker.name
    try:
        if request.method == 'POST':
            name = request.form['name']
            details = request.form['details']
            settings = request.form['settings']
            tracker_type = request.form['type']
            option = request.form['options']
            current_user_id = current_user.id
            tracker = Tracker.query.filter_by(name=name).first()
            if tracker and tracker.customer_id == current_user_id and this_tracker_name != name:
                flash('The tracker is already added by you, Try a new name for your tracker.')
            elif tracker_type != 'Multiple choice':
                this_tracker.name = name
                this_tracker.details = details
                this_tracker.tracker_type = tracker_type
                this_tracker.settings = settings
                db.session.commit()
                flash('Tracker Updated Successfully.')
                return redirect('/home')
            elif tracker_type == 'Multiple choice':
                data1 = Options.query.filter_by(customer_id = current_user.id, name = name ).first()
                this_tracker.name = name
                this_tracker.details = details
                this_tracker.tracker_type = tracker_type
                this_tracker.settings = settings
                db.session.commit()
                if data1:
                    data1.option = option
                    db.session.commit()
                else:
                    newdata = Options(name = name, customer_id = current_user.id, option = option)
                    db.session.add(newdata)
                    db.session.commit()
                flash('Tracker Updated Successfully.')
                return redirect('/home')
    except:
        flash('Something went wrong.')
    return render_template("edittracker.html", user=current_user, tracker=this_tracker)


#-----------------View Profile---------------------
@app.route('/viewprofile')
@login_required
def viewprofile():
    return render_template('profile.html', user = current_user)

#------------------Edit Profile-----------------
@app.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    if request.method == 'POST':
        fullname = request.form['name']
        email = request.form['email']
        city = request.form['city']
        user_id = current_user.id
        current_user_email = current_user.email
        user = Customer.query.filter_by(email=email).first()
        if user and current_user_email != email:
             flash('Email is already taken, try another email.')
        else:
            edit_user = Customer.query.get(user_id)
            edit_user.fullname = fullname
            edit_user.email = email
            edit_user.city = city
            db.session.commit()
            flash('Profile Updated Successfully.')
            return redirect('/viewprofile')
    return render_template('editprofile.html', user = current_user)


#-------------------Logging details-------------------------
@app.route('/addlog/<int:tracker_id>', methods = ['GET', 'POST'])
def addlog(tracker_id):
    import datetime
    now = datetime.datetime.now()
    this_tracker = Tracker.query.get(tracker_id)
    trackername = this_tracker.name
    if this_tracker.tracker_type != 'Multiple choice':
        if request.method == 'POST':
            time = request.form['date']
            value = request.form['value']
            notes = request.form['notes']
            new_log = Log(timestamp=time, value=value, notes=notes, tracker_id=tracker_id, customer_id=current_user.id,added_date_time=now)
            db.session.add(new_log)
            db.session.commit()
            flash('New Log Added For ' + this_tracker.name + ' Tracker')
            return redirect('/home')
        return render_template('log.html', user=current_user, tracker=this_tracker, now = now)
    elif this_tracker.tracker_type == 'Multiple choice':
        mcq = Options.query.filter_by(customer_id = current_user.id, name = trackername).first()
        s = str(mcq.option)
        sl = s.split(' ')
        if request.method == 'POST':
            time = request.form['date']
            value = request.form['value']
            notes = request.form['notes']
            new_log = Log(timestamp=time, value=value, notes=notes, tracker_id=tracker_id, customer_id=current_user.id,added_date_time=now)
            db.session.add(new_log)
            db.session.commit()
            flash('New Log Added For ' + this_tracker.name + ' Tracker')
            return redirect('/home')
        return render_template('log.html', user=current_user, tracker=this_tracker, now = now, sl = sl )


#-------------------------------View Tracker-------------------------
@app.route('/viewtracker/<int:tracker_id>')
@login_required
def viewtracker(tracker_id):
    import matplotlib.pyplot as plt
    from matplotlib import style
    style.use('fivethirtyeight')
    this_tracker = Tracker.query.get(tracker_id)
    logs = Log.query.filter_by(tracker_id = tracker_id, customer_id = current_user.id).all()
    dates = []
    values = []
    for i in range(len(logs)):
        dates.append(logs[i].timestamp)
        values.append(logs[i].value)
    if this_tracker.tracker_type == 'Numerical':
        plt.figure(figsize=(18, 8))
        def addlabels(dates,values):
            for i in range(len(dates)):
                plt.text(i, values[i], values[i], ha = 'center')
        plt.bar(dates, values)
        plt.plot(dates, values, color="black")
        addlabels(dates, values)
        plt.title(this_tracker.name)
        plt.xlabel('Date and Time')
        plt.ylabel('Values')
        plt.tight_layout()
        plt.savefig('.\static\graph.png')
        #plt.show()
        return render_template('viewtracker.html', tracker = this_tracker, logs = logs)
    elif this_tracker.tracker_type == 'Boolean':
        plt.figure(figsize=(18, 8))
        def addlabels(dates,values):
            for i in range(len(dates)):
                plt.text(i, values[i], values[i], ha = 'center')
        #plt.bar(dates, values)
        plt.plot(dates, values)
        addlabels(dates, values)
        plt.title(this_tracker.name)
        plt.xlabel('Date and Time')
        plt.ylabel('Values')
        plt.tight_layout()
        plt.savefig('.\static\graph.png')
        #plt.show()
        return render_template('viewtracker.html', tracker = this_tracker, logs = logs)
    elif this_tracker.tracker_type == 'Time duration':
        vmins = []
        for i in values:
            s = str(i).split(':')
            hr = int(s[0])
            min = int(s[1])
            sec = int(s[2])
            vmins.append(round((hr*60)+ min +(sec/60)))
        print(vmins)
        plt.figure(figsize=(18, 8))
        def addlabels(dates,values):
            for i in range(len(dates)):
                plt.text(i, values[i], values[i], ha = 'center')
        plt.bar(dates, vmins)
        plt.plot(dates, vmins, color='black')
        addlabels(dates, vmins)
        plt.title(this_tracker.name)
        plt.xlabel('Date and Time')
        plt.ylabel('Duration in minutes')
        plt.tight_layout()
        plt.savefig('.\static\graph.png')
        #plt.show()
        return render_template('viewtracker.html', tracker = this_tracker, logs = logs)
    else:
        opt1 = Options.query.filter_by(customer_id = current_user.id, name = this_tracker.name).first()
        s = str(opt1.option)
        sl = s.split(' ')
        fig = plt.figure(figsize=(18, 8))
        def addlabels(dates,values):
            for i in range(len(dates)):
                plt.text(i, values[i], values[i], ha = 'center')
        plt.plot(dates, values)
        addlabels(dates, values)
        plt.xlabel('Date and Time')
        plt.ylabel('Values')
        plt.tight_layout()
        plt.savefig('.\static\graph.png')
        #plt.show()
        return render_template('viewtracker.html', tracker = this_tracker, sl = sl, logs = logs)


#-------------Remove/Delete log-----------------
@app.route('/dlog/<int:log_id>', methods = ['GET', 'POST'])
@login_required
def deletelog(log_id):
    logdetail = Log.query.get(log_id)
    tracker_id = logdetail.tracker_id
    try:
        db.session.delete(logdetail)
        db.session.commit()
        flash('Log Removed Successfully.')
    except:
        flash('Something went wrong.')
    return redirect(url_for('viewtracker', tracker_id = tracker_id))


#------------Edit Log----------------
@app.route('/editlog/<int:log_id>', methods = ['GET', 'POST'])
@login_required
def editlog(log_id):
    current_log = Log.query.get(log_id)
    current_tracker = Tracker.query.get(current_log.tracker_id)
    if current_tracker.tracker_type != 'Multiple choice':
        try:
            if request.method == 'POST':
                when = request.form['date']
                value = request.form['value']
                notes = request.form['notes']

                current_log.timestamp = when
                current_log.value = value
                current_log.notes = notes
                db.session.commit()
                flash('Log Updated Successfully.')
                return redirect(url_for('viewtracker', tracker_id=current_log.tracker_id))
        except:
            flash('Something went wrong.')
        return render_template("editlog.html", user=current_user, tracker=current_tracker, log=current_log)
    elif current_tracker.tracker_type == 'Multiple choice':
        mcq = Options.query.filter_by(customer_id = current_user.id, name = current_tracker.name).first()
        s = str(mcq.option)
        sl = s.split(' ')
        try:
            if request.method == 'POST':
                when = request.form['date']
                value = request.form['value']
                notes = request.form['notes']

                current_log.timestamp = when
                current_log.value = value
                current_log.notes = notes
                db.session.commit()
                flash('Log Updated Successfully.')
                return redirect(url_for('viewtracker', tracker_id=current_log.tracker_id))
        except:
            flash('Something went wrong.')
        return render_template("editlog.html", user=current_user, tracker=current_tracker, log=current_log, sl = sl)

#---------Optional-Exporting data into excel file----------------
@app.route("/exportlog/<int:tracker_id>", methods=['GET', 'POST'])
@login_required
def exportlog(tracker_id):
    logs = Log.query.filter_by(tracker_id = tracker_id, customer_id = current_user.id).all()
    column_names = ['id', 'timestamp', 'value', 'notes', 'tracker_id', 'customer_id', 'added_date_time']
    return excel.make_response_from_query_sets(logs, column_names, "xls")

@app.route("/exportlogsall", methods=['GET', 'POST'])
@login_required
def exportlogsall():
    logs = Log.query.filter_by(customer_id = current_user.id).all()
    column_names = ['id', 'timestamp', 'value', 'notes', 'tracker_id', 'customer_id', 'added_date_time']
    return excel.make_response_from_query_sets(logs, column_names, "xls")

#------------------Import logs from Excel file---------------------
@app.route("/importlog/<int:tracker_id>", methods=['GET', 'POST'])
@login_required
def importlog(tracker_id):
    if request.method == 'POST':
        nfile = request.files['data']
        if not os.path.isdir('static'):
            os.mkdir('static')
        filepath = os.path.join('static', nfile.filename)
        nfile.save(filepath)
        d = pd.read_excel(filepath)
        for i in range(len(d)):
            timestamp = d['timestamp'][i]
            value = int(d['value'][i])
            notes = str(d['notes'][i])
            #tracker_id = d['tracker_id'][i]
            #customer_id = d['customer_id'][i]
            added_date_time = d['added_date_time'][i]
            nlog = Log(timestamp=timestamp, value=value, notes = notes, tracker_id = tracker_id, customer_id =current_user.id, added_date_time = added_date_time)
            db.session.add(nlog)
            db.session.commit()
        os.remove(filepath)
        flash("logs has been import. Explore on dashboard for corresponding tracker.")
        return redirect('/home')
    return render_template("import.html")

#-----------logout------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out from our application.')
    return redirect('/')


#---------App Run------------------
if __name__ == "__main__":
    excel.init_excel(app)
    app.secret_key = 'super secret key'
    app.debug = True
    app.run()
    

