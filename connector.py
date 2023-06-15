#pip install tensorflow
#pip install flask
#
import numpy as np
import pandas as pd
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, session, redirect, url_for, flash
from tensorflow import keras
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from keras.models import load_model
import smtplib
from email.message import EmailMessage
from os.path import join, dirname, realpath
import MySQLdb.cursors
import datetime
import requests, json
from types import SimpleNamespace
import random, ast, re
from flask_mail import Mail, Message

# Create application, note that template folder must contain all the html/php files that will be used
app = Flask(__name__, template_folder="C:/xampp/htdocs/login")

app.secret_key = 'super secret'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'registered'

# set up mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='trafficprediction13@gmail.com', # replace with your email address
    MAIL_PASSWORD='slcunzinzfzhyepx' # replace with your email password
)

mail = Mail(app)

# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

# Intialize MySQL
mysql = MySQL(app)

# Load machine learning model
model = load_model('C:/xampp/htdocs/login/trafficANN.h5')

# Load the dataset
df = pd.read_csv('C:/xampp/htdocs/login/combined_data.csv')

categorical_data = df[['Time_of_Day', 'Day_of_Week', 'Weather_Condition', 'Road_Type', 'Incident']]
encoder = OneHotEncoder(handle_unknown='ignore')
encoder.fit_transform(categorical_data).toarray()

scaler = StandardScaler()

api_key = "51614e8a5b22455f262f842eed644c6a"
base_url = "http://api.openweathermap.org/data/2.5/weather?"
complete_url = base_url + "appid=" + api_key + "&q=Singapore"

def modelPredict (time_of_day, day_of_week, weather_condition, road_type, incident):
    # Create a DataFrame with the input values
    if type(road_type) == str:
        sample = pd.DataFrame({'Time_of_Day': [time_of_day], 'Day_of_Week': [day_of_week],
                           'Weather_Condition': [weather_condition], 'Road_Type': [road_type],
                           'Incident': [incident]})
    else:
        sample = pd.DataFrame({'Time_of_Day': [time_of_day], 'Day_of_Week': [day_of_week],
                           'Weather_Condition': [weather_condition], 'Road_Type': [road_type[0]],
                           'Incident': [incident]})
        
        for i in range(1, len(road_type)):
            new = pd.DataFrame({'Time_of_Day': [time_of_day], 'Day_of_Week': [day_of_week],
                           'Weather_Condition': [weather_condition], 'Road_Type': [road_type[i]],
                           'Incident': [incident]})
            sample = pd.concat([sample, new])

    
    # One-hot encode the categorical variables
    sample_cat = encoder.transform(sample[['Time_of_Day', 'Day_of_Week', 'Weather_Condition', 'Road_Type', 'Incident']])
    sample_cat = sample_cat.toarray()

    # Use the trained model to make a prediction
    prediction = model.predict(sample_cat)
    prediction = prediction.tolist()
    listPrediction = [item for sublist in prediction for item in sublist]

    return listPrediction

def timePredict(road_type, prediction, prediction2, distance, duration, routes):
    deduct = 0
    timeAdded = []
    print(routes)
    print(road_type)
    for i in range(len(prediction)):
        # average speed based on data of SpeedBand
        avg_speed = 0
        if road_type[i] == "CAT1":
            avg_speed = round(random.uniform(60, 90), 2)
        elif road_type[i] == "CAT2":
            avg_speed = round(random.uniform(40, 69), 2)
        elif road_type[i] == "CAT3":
            avg_speed = round(random.uniform(20, 29), 2)
        elif road_type[i] == "CAT4":
            avg_speed = round(random.uniform(30, 39), 2)
        elif road_type[i] == "CAT5":
            avg_speed = round(random.uniform(10, 19), 2)
        elif road_type[i] == "SLIP_ROAD":
            avg_speed = round(random.uniform(30, 39), 2)
        
        if (i < len(routes) and 'and' in routes[i]):
            avg_speed2 = 0
            if road_type[i+1] == "CAT1":
                avg_speed2 = round(random.uniform(60, 90), 2)
            elif road_type[i+1] == "CAT2":
                avg_speed2 = round(random.uniform(40, 69), 2)
            elif road_type[i+1] == "CAT3":
                avg_speed2 = round(random.uniform(20, 29), 2)
            elif road_type[i+1] == "CAT4":
                avg_speed2 = round(random.uniform(30, 39), 2)
            elif road_type[i+1] == "CAT5":
                avg_speed2 = round(random.uniform(10, 19), 2)
            elif road_type[i+1] == "SLIP_ROAD":
                avg_speed2 = round(random.uniform(30, 39), 2)
            avg_speed = (avg_speed + avg_speed2)/2
            i += 1
        print("pred 1")
        print(prediction[i])
        # print("pred 2")
        # print(prediction2[i])  #out of range
        
        # calculate est_time_added 
        min_time = duration[i-deduct]
        
        est_time_added = 0
        for j in range(len(prediction2)):
            predIncrease = (prediction2[j] - prediction[i])/prediction[i]
            avg_speed = float(avg_speed * (1 - predIncrease))
            max_time = float((distance[i]/avg_speed)*60)
        
            est_time_added = (est_time_added + abs(max_time - min_time))/1.5
        
        
        timeAdded.append(est_time_added)
        
    return timeAdded


def roadtype (road):
    road = road.upper()
    if ("PIE" in road or "AYE" in road or "ECP" in road or "CTE" in road or "E'WAY" in road\
        or "TPE" in road or "KPE" in road or "SLE" in road or "BKE" in road\
        or "KJE" in road or "MCE" in road or "PARKWAY" in road or "EXPRESSWAY" in road):
        return "CAT1"
    elif ("BOULEVARD" in road or "AVENUE" in road or "FIELD" in road or "TERRANCE" in road
          or ("WAY" in road and "FARMWAY" not in road and "GATEWAY" not in road) or "DRIVE" in road\
          or "HIGHWAY" in road or "AVE" in road or "BLVD" in road or "HWAY" in road\
          or "PARKWAY" in road or "CROSSING" in road):
        return "CAT2"
    elif ("DRIVE" in road or "ROAD" in road or "STREET" in road or "CRESCENT" in road or "TRACK" in road\
        or "DR" in road or "RD" in road or "CRES" in road or "CENTRAL" in road or "RISE" in road\
        or "JLN" in road or "ST" in road or "Lengkong" in road or "BOW" in road or "CONCOURSE" in road\
        or "JALAN" in road or "BUKIT" in road or "LENGKOK" in road or "EAST" in road\
        or "TANJONG" in road or "PADANG" in road or "LORONG" in road or "UNDERPASS" in road or "GREEN" in road\
        or "VALE" in road or "VIADUCT" in road):
        return "CAT3"
    elif ("QUAY" in road or "PROMENADE" in road or "BUSINESS PARK" in road or "FARMWAY" in road\
        or "WALK" in road or "VIEW" in road or "HILL" in road or "GARDEN" in road or "GRANDE" in road\
        or "INDUSTRAIL PARK" in road or "IND PARK" in road or "KAMPONG" in road or "HEIGHT" in road\
        or "ISLAND" in road or "PLAZA" in road or "EAST" in road or "VISTA" in road or "JUNCTION" in road\
        or "JCT" in road or "LINK" in road or "MOUNT" in road or "RIDGE" in road or "NORTH" in road\
        or "WEST" in road):
        return "CAT4"
    elif ("GATEWAY" in road or "SECTOR" in road or "CIRCLE" in road or "CIRCUIT" in road or "LOOP" in road\
          or "CLOSE" in road or "COURT" in road or "CROSS" in road or "ESTATE" in road or "RING" in road\
          or "LANE" in road or "CIRCLE" in road or "TURN" in road or "CLOSE" in road or "TERRANCE" in road\
          or "SQUARE" in road or "RIDGE" in road or "PLAIN" in road or "PATH" in road or "BANK" in road\
        or "GATE" in road or "GROVE" in road or "MALL" in road or "PLACE" in road or "VALLEY" in road):
        return "CAT5"
    else:
        return "SLIP_ROAD"


# Bind home function to URL  (this will be the log in page), for now we use 
@app.route('/',  methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'user_login' in request.form and 'user_password' in request.form:
        # Create variables for easy access
        username = request.form['user_login']
        password = request.form['user_password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, str(hash(password)),))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
        # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "DELETE from traffic_data"
    cursor.execute(sql)
    mysql.connection.commit()
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/register',  methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        print(password)
        email = request.form['email']
        print(email)
        roles = request.form['role']
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        # Check if email can be registered as power user
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        email_check = cursor.fetchone()
        # If account exists show error and validation checks
        cursor.execute('SELECT * FROM poweremail')
        power_check = cursor.fetchall()
        df = pd.DataFrame(power_check)
        eformat_all = df["eFormat"].tolist()
        for i in range(len(eformat_all)):
            if roles == 'power' and not re.match(eformat_all[i],email):
                msg = 'Not registered Power User Email'
                return render_template('register.html', msg=msg)
            
        # checks for duplicate username
        if account:
            msg = 'Account already exists!'
            return render_template('register.html', msg=msg)
        # checks for duplicate email
        elif email_check:
            msg = 'Email already exists!'
            return render_template('register.html', msg=msg)
        # checks for email format
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
            return render_template('register.html', msg=msg)
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
            return render_template('register.html', msg=msg)
        # Check if password is at least 6 characters long and contains at least 1 letter and 1 digit
        elif len(password) < 6 or not re.search(r'\d', password) or not re.search(r'[A-Za-z]', password): 
            msg = 'Password must have length of 6 and contain at least 1 alphabet and 1 number!'
            return render_template('register.html', msg=msg)
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
            return render_template('register.html', msg=msg)
        else:
            cursor.execute('SELECT SYSDATE()')
            reg_date = cursor.fetchone()
            password = str(hash(password))
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute('INSERT INTO `users`(`username`, `email`,`password`, `roles`, `reg_date`) VALUES (%s, %s, %s, %s, %s)',
                           (username, email, password, roles, reg_date))
            mysql.connection.commit()
            flash('You have successfully registered!')
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    user = account["username"]
    
    return render_template('mainPython.html', name = user)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    user = account["username"]
    
    roles = account["roles"]
    
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    id_all = df["id"].tolist()
    user_all = df["username"].tolist()
    email_all = df["email"].tolist()
    roles_all = df["roles"].tolist()
    
    
    return render_template('profile.html', name = user, role = roles, id_all = id_all, user_all = user_all, email_all = email_all, roles_all = roles_all)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    user_id = account["id"]
    
    msg = ''
    # Check POST requests exist (user submitted form)
    if request.method == 'POST' and 'new_password' in request.form and 'confirm_password' in request.form:
        new_password = request.form['new_password'].strip()
        confirm_password = request.form['confirm_password'].strip()
        
        if new_password == confirm_password:
            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute('UPDATE users SET password = %s WHERE id = %s', (str(hash(confirm_password)), user_id))
            mysql.connection.commit()
            flash('You have successfully changed your password! Please log in again.')
            return redirect(url_for('login'))
        else:
            msg = 'new password and confirm password does not match'
            # Show registration form with message (if any)
            return render_template('change_password.html', msg=msg)
            
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('change_password.html', msg=msg)

@app.route('/update_user', methods=['POST'])
def update_user():
    if request.method == 'POST':
        user_id = request.form['edit-user-id']
        new_name = request.form['edit-user-name']
        new_email = request.form['edit-user-email']
        new_roles = request.form['edit-user-roles']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE users SET username = %s, email = %s, roles = %s WHERE id = %s', (new_name, new_email, new_roles, user_id))
        mysql.connection.commit()
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    user = account["username"]
    
    roles = account["roles"]
    
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    id_all = df["id"].tolist()
    user_all = df["username"].tolist()
    email_all = df["email"].tolist()
    roles_all = df["roles"].tolist()
    
    cursor.execute('UPDATE users SET username = %s, email = %s, roles = %s WHERE id = %s', (new_name, new_email, new_roles, user_id))
    
    
    
    return render_template('profile.html', name = user, role = roles, id_all = id_all, user_all = user_all, email_all = email_all, roles_all = roles_all)


@app.route('/dashboard')
def dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    roles = account["roles"]
    print(roles)
    
    liTraffic = request.args['liTraffic']  # counterpart for url_for()
    liTraffic = session['liTraffic'] 
    liRoutes = request.args['liRoutes']  # counterpart for url_for()
    liRoutes = session['liRoutes']
    return render_template('report.html', liTraffic = liTraffic, liRoutes = liRoutes, roles = roles)
    
@app.route('/uploadtocsvdb', methods = ['GET', 'POST'])
def upload():
    msg = ''
    if request.method == 'POST':
        if request.form["submit"] == "Upload":
            # get the uploaded file
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                f = request.files.get('file')
                # Extracting uploaded file name
                data_filename = secure_filename(f.filename)
                # Use Pandas to parse the CSV file
                f.save(data_filename)
                csvData = pd.read_csv(data_filename, header=0)
                print(csvData)
                # Loop through the Rows
                try:
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    for i,row in csvData.iterrows():
                        sql = "INSERT INTO traffic_data VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)"
                        value = (row['Time_of_Day'],int(row['Value_of_Time_of_Day']),row['Day_of_Week']\
                                ,row['Weather_Condition'],row['Road_Name'],row['Road_Type'],row['Incident']\
                                ,int(row['Traffic_Volume']))
                        cursor.execute(sql, value)
                        mysql.connection.commit()
                        msg = 'Added to database'
                except:
                    msg = 'Error has Occured. Please check if all Columns are in CSV file'
        elif request.form["submit"] == "Clear Data":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "DELETE from traffic_data"
            cursor.execute(sql)
            mysql.connection.commit()
            msg = 'Deleted from database'
    return render_template('UploadCSVToDB.html', msg = msg)

@app.route('/byTime')
def byTime():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT \
                    CASE \
                      WHEN Time_of_Day >= '00:00:00' AND Time_of_Day < '06:00:00' THEN 'Midnight' \
                      WHEN Time_of_Day >= '06:00:00' AND Time_of_Day < '12:00:00' THEN 'Day' \
                      WHEN Time_of_Day >= '12:00:00' AND Time_of_Day < '18:00:00' THEN 'Afternoon'  \
                      WHEN Time_of_Day >= '18:00:00' AND Time_of_Day <= '23:59:59' THEN 'Night' \
                    END AS Time_Period, \
                    AVG(Traffic_Volume) AS Traffic_Volume \
                  FROM traffic_data  \
                  GROUP BY Time_Period \
                  ORDER BY FIELD(Time_Period, 'Midnight', 'Day', 'Afternoon', 'Night')")
    # Fetch one record and return result
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    time = df["Time_Period"].tolist()
    values = df["Traffic_Volume"].tolist()
    print(values)
    print(time)
    for i in range(len(values)):
        values[i] = str(values[i])
    return render_template('AvgTrafficVolumebyTimeofDay.html', values=values, time=time)

@app.route('/byHour')
def byHour():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Time_of_Day, AVG(Traffic_Volume)\
                    AS Traffic_Volume FROM traffic_data GROUP BY Time_of_Day ")
    # Fetch one record and return result
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    time = df["Time_of_Day"].tolist()
    for i in range(len(time)):
        total_seconds = time[i].total_seconds() 
        seconds_in_hour = 60 * 60 
        td_in_hours = total_seconds / seconds_in_hour
        time[i] = round(td_in_hours)
    values = df["Traffic_Volume"].tolist()
    for i in range(len(values)):
        values[i] = str(values[i])
    return render_template('AvgTrafficVolumebyHourofDay.html', values=values, time=time)

@app.route('/byDay')
def byDay():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Day_of_Week, AVG(Traffic_Volume) AS Traffic_Volume\
                    FROM traffic_data GROUP BY Day_of_Week ORDER BY FIELD(Day_of_Week, \
                   'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')")
    # Fetch one record and return result
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    day = df["Day_of_Week"].tolist()
    values = df["Traffic_Volume"].tolist()
    for i in range(len(values)):
        values[i] = str(values[i])
    return render_template('AvgTrafficVolumebyDayOfWeek.html', values=values, day=day)

@app.route('/byWeather')
def byWeather():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Weather_Condition, AVG(Traffic_Volume) \
                   AS Traffic_Volume FROM traffic_data GROUP BY \
                   Weather_Condition ORDER BY Traffic_Volume DESC")
    # Fetch one record and return result
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    weather = df["Weather_Condition"].tolist()
    values = df["Traffic_Volume"].tolist()
    for i in range(len(values)):
        values[i] = str(values[i])
    return render_template('AvgTrafficVolumebyWeatherCondition.html', values=values, weather=weather)

@app.route('/byRoadName')
def byRoadName():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Road_Name, AVG(Traffic_Volume) AS\
                    Traffic_Volume FROM traffic_data GROUP\
                    BY Road_Name ORDER BY Traffic_Volume DESC")
    # Fetch one record and return result
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    roadname = df["Road_Name"].tolist()
    values = df["Traffic_Volume"].tolist()
    for i in range(len(values)):
        values[i] = str(values[i])
    return render_template('TrafficVolumebyRoadName.html', values=values, roadname=roadname)

@app.route('/byRoadType')
def byRoadType():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Road_Type, AVG(Traffic_Volume)\
                    AS Traffic_Volume FROM traffic_data\
                    GROUP BY Road_Type ORDER BY Traffic_Volume DESC")
    # Fetch one record and return result
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    print(df)
    roadtype = df["Road_Type"].tolist()
    values = df["Traffic_Volume"].tolist()
    for i in range(len(values)):
        values[i] = str(values[i])
    return render_template('TrafficVolumebyRoadType.html', values=values, roadtype=roadtype)

@app.route('/byIncident')
def byIncident():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT incident, AVG(traffic_volume) \
                   AS Traffic_Volume FROM traffic_data GROUP BY incident")
    # Fetch one record and return result
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    print(df)
    incident = df["incident"].tolist()
    values = df["Traffic_Volume"].tolist()
    for i in range(len(values)):
        values[i] = str(values[i])
    return render_template('AvgTrafficVolumebyIncident.html', values=values, incident=incident)

@app.route('/alarm', methods=['GET', 'POST'])
def alarm():
    if request.method =='POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        user_id = account["id"]
        recipient = request.form.get('recipient')
        subject = request.form.get('subject')
        message = request.form.get('message')
        schedule_time = request.form.get('schedule_time')
        schedule_date = request.form.get('schedule_date')
        origin = request.form.get('originInput')
        destination = request.form.get('destinationInput')
        print(origin)
        print(destination)
        # header = "trafficprediction13@gmail.com"
        
        
        content = str(message) + ", origin: " + str(origin) + "\n destination: " + str(destination)
        msg = EmailMessage()
        msg.set_content(content)
        
        # create a new message
        msg = Message(
            'Hello',
            sender='trafficprediction13@gmail.com', # replace with your email address
            recipients=[recipient] # replace with the recipient's email address
        )
        # add some text to the message body
        msg.body = "you have scheduled time has arrived \n + https://unaginagi.pythonanywhere.com"
        # msg.body = "you have scheduled time has arrived \n + https://unaginagi.pythonanywhere.com + \n click this link to go now! \n" + "https://unaginagi.pythonanywhere.com/predict?origin-input=" + str(origin) + "&destination-input=" + str(destination)
        # send the message using the mail object
        mail.send(msg)
        print(msg.body)
        
        # add to database
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # sql = "INSERT INTO schedule_emails (user_id, recipient, message, schedule_time, schedule_date) VALUES (%s, %s, %s, %s, %s)"
        # val = (user_id, recipient, message.body, schedule_time, schedule_date)
        # cursor.execute(sql, val)
        # mysql.connection.commit()
    
    return render_template('SetAlarm.html')


@app.route('/predict', methods =['POST', 'GET'])
def predict():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    user = account["username"]
    current_id = account["id"]
    current = datetime.datetime.now()
    
    # If a form is submitted
    if request.method == "POST":
        # Get the input values from the HTML form
        time_of_day = request.form.get('time')
        day_of_week = request.form.get('day')
        current = datetime.datetime.now()

        if time_of_day == '':
            time_of_day = current.hour
        if day_of_week =='':
            day_of_week = current.strftime("%A")
        else:
            year, month, day = (int(x) for x in day_of_week.split('-')) 
            ans = datetime.date(year, month, day)
            day_of_week = ans.strftime("%A")

        weather_condition = request.form.get('weather')


        if (weather_condition == 'Current Weather'):
            # get method of requests module
            # return response object
            response = requests.get(complete_url)
    
            # json method of response object
            # convert json format data into
            # python format data
            x = response.json()

            if x["cod"] != "404":
    
                # store the value of "main"
                # key in variable y
                y = x["main"]
                # store the value of "weather"
                # key in variable z
                z = x["weather"]
    
                # store the value corresponding
                # to the "description" key at
                # the 0th index of z
                weather_description = z[0]["description"]

            if (weather_description == "clear sky"):
                weather_condition = "Clear"
            elif (weather_description == "shower rain" or 
                weather_description == "rain" or
                weather_description == "thunderstorm"):
                weather_condition = "Rainy"
            elif (weather_description == "broken clouds" or 
                weather_description == "few clouds" or
                weather_description == "scattered clouds"):
                weather_condition = "Foggy"
            else:
                weather_condition = "Clear"

        route = request.form.get("route")
        incident = "None"
        road_type = []
        route = route.split(',')
        for roads in route:
            if ' and ' in roads:
                roads = roads.split()
                road = roads[0]
                road1 = roads[2]
                if road in df.values :
                    roadtype1 =  df.loc[df['Road_Name'] == road, 'Road_Type'].iloc[0]
                else:
                    roadtype1 = roadtype(road)

                road_type.append(roadtype1)

                if road1 in df.values :
                    roadtype2 = df.loc[df['Road_Name'] == road1, 'Road_Type'].iloc[0]
                else:
                    roadtype2 = roadtype(road1)
                road_type.append(roadtype2)

            else: 
                if roads in df.values :
                    roadtype1 = df.loc[df['Road_Name'] == roads, 'Road_Type'].iloc[0]
                else:
                    roadtype1 = roadtype(roads)
                road_type.append(roadtype1)
        
        
        
        #prediction for the route
        prediction = modelPredict(time_of_day, day_of_week, weather_condition, road_type, incident)
        prediction2 = ""
        marker = request.form.get("event")
        print(marker)
        if (marker != '' and marker is not None):
            roadtype2 = []
            x = json.loads(marker, object_hook=lambda d: SimpleNamespace(**d))
            print(x)
            road_t = "None"
            for i in range(len(x)):
                incident = x[i].incident
                road = x[i].address
                if road in df.values :
                    road_t = df.loc[df['Road_Name'] == road, 'Road_Type'].iloc[0]
                else:
                    road_t = roadtype(road)
            roadtype2.append(road_t)
        #prediction for incident if have
            prediction2 = modelPredict(time_of_day, day_of_week, weather_condition, road_type, incident)
            
        # save into route database
        add = 0
        for i in range(len(route)): 
            print(route[i])
            print("adding new route to database...")
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "INSERT INTO route (users_id, timestamp, route, Time_of_Day, Day_of_Week, Weather_Condition, Road_Type, Incident, Traffic_Volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            if " and " in route[i]:
                val = (current_id, current, route[i], time_of_day, day_of_week, weather_condition, road_type[i], incident, prediction[i]+prediction2[i+1+add])
                add+= 1
            else:
                val = (current_id, current, route[i], time_of_day, day_of_week, weather_condition, road_type[i], incident, prediction[i]+prediction2[i])
            cursor.execute(sql, val)
            mysql.connection.commit()
            
        if request.form["submit"] == "Predict":
            # Render the result HTML template with the predicted traffic volume
            if prediction2 != "":
                roadDetail = request.form.get('roadDetail')
                roadDetail = "[" + roadDetail + "]"
                road_detail = ast.literal_eval(roadDetail)
                
                distances = []
                durations = []
                i = 0
                for s in road_detail:
                    m = re.match(r'^([\d\.]+)\s*km\s*-\s*([\d\.]+)\s*mins$', s)
                    if m:
                        if ('and' in route[i]):
                            distances.append(float(m.group(1)))
                            durations.append(float(m.group(2)))
                            distances.append(float(m.group(1)))
                            durations.append(float(m.group(2)))
                        else:
                            distances.append(float(m.group(1)))
                            durations.append(float(m.group(2)))
                    i += 1
                        
                print(distances)
                print(durations)
                
                timePred = timePredict(road_type, prediction, prediction2, distances, durations, route)
            
            # Render the result HTML template with the predicted traffic volume
            if prediction2 != "":
                return render_template('mainPython.html', result = prediction, road = prediction2, time = timePred, name = user)
            else:
                return render_template('mainPython.html', result = prediction, name = user)
        elif request.form["submit"] == "Dashboard":
            liTraffic = []
            liRoutes = []
            add = 0
            print(route)
            for i in range (len(route)):
                print(i)
                traffic = prediction[i + add]
                if " and " in route[i]:
                    traffic += prediction [i+1 +add]
                    add+= 1
                liTraffic.append(traffic)
                liRoutes.append(route[i])
            session['liTraffic'] = liTraffic
            session['liRoutes'] = liRoutes
            print(liTraffic)

            return redirect(url_for('dashboard', liTraffic = liTraffic, liRoutes = liRoutes))
            
if __name__ == '__main__':
    #Run the application
    app.run(use_reloader=False, debug=True)