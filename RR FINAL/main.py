from flask import Flask,render_template,url_for,request,flash,session,redirect
from flask_material import Material
import folium
import datetime
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
import smtplib
import requests
import MySQLdb.cursors
import random
from werkzeug.security import generate_password_hash , check_password_hash
from flask_login import LoginManager,UserMixin,login_required,login_required,logout_user,current_user,login_user
from sqlalchemy import func

# MySQL Connector Configuration
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="rentromeo"
)

# INITIALATING THE APP
app = Flask(__name__)
app.secret_key = 'besecret'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_USERNAME= 'dhananjayarne@gmail.com',
    MAIL_PASSWORD= 'okgooglepagalhumein00' ,
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USE_TLS=False
)
mail = Mail(app)
Material(app)

local_server = True
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/rentromeo'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@server/db'
db = SQLAlchemy(app)

# GETTING DATABASE INFO
class Register_data(UserMixin,db.Model):
    # id,name,email,password,date
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.String(255), nullable = True)
    instagram = db.Column(db.String(255), nullable = True)
    facebook = db.Column(db.String(255), nullable = True)
    phone_no = db.Column(db.String(255), nullable = True)
    state = db.Column(db.String(255), nullable = True)
    district = db.Column(db.String(255), nullable = True)
    pincode = db.Column(db.String(255), nullable = True)
    date = db.Column(db.String(50), nullable=True)

class Ad_register(db.Model):
    # sno, name, address, lat, log,price,water,electricity,parking,phone,email,date
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    p_type = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(255), nullable=False)
    postal_code = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    log = db.Column(db.Float, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    water = db.Column(db.String(10), nullable=True)
    electricity = db.Column(db.String(10), nullable=True)
    parking = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(50), nullable=True)

# INTIALIZING LOGIN MANAGER
@login_manager.user_loader
def load_user(user_id):
    return Register_data.query.get(int(user_id))

# HOME PAGE ROUTE
@app.route("/")
def home():
    return render_template("Home.html")






















""" ===================================MAP ALGORITHM=========<START>====================================="""
# NOT REGISTERED USER MAP
@app.route("/unreg_map")
def unreg_map():
    return render_template("unreg_map.html")

# MAKING A SEARCH ROUTE DOR SEARCHING AMONG THE MAP
@app.route("/search_map", methods=['GET', 'POST'])
def search_map():
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="http")
    country = "India"
    mycursor = mydb.cursor()
    mycursor.execute("SELECT lat,log FROM ad_register")
    myresult = mycursor.fetchall()
    if (request.method == 'POST'):
        city = request.form.get('address')
        loc = geolocator.geocode(str(city) + ',' + country)
        lat = loc.latitude
        log = loc.longitude
        m = folium.Map(location=[lat, log], zoom_start=12)
        # Global Tooltip
        tooltip = "Click To See details"

        for row in myresult:
            folium.Marker([row[0], row[1]],
                          popup='<form action="/login" method="get"><button type="submit">LOGIN TO SEE MORE DETAIL</button></form>',
                          tooltip=tooltip,
                          icon=folium.Icon(icon='home', color='red')).add_to(m)

            # Generates a Html File
        m.save('templates/map.html')
        return render_template('unreg_map.html')
    return render_template('unreg_map.html')
  
# MAKING A APP  ROUTE TO RENDER TEMPLATE OF MAP.HTML
@app.route("/show_map")
def show_map():
    search_map()
    return render_template("map.html")

""" ===================================MAP ALGORITHM=========<END>====================================="""






















""" ================REGISTRATION , LOGIN , LOGOUT,  FORGOT PASSWORD=========<START>========================="""
# MAKING REGISTER ROUTE
@app.route("/register",methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('Name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        email = request.form.get('email')
        register = Register_data.query.filter_by(email=email).first()
        if register:
            flash("YOUR EMAIL IS ALREADY REGISTERED PLEASE LOGIN")
        else:
            otp = str(random.randint(10000,99999))
            first_name = request.form.get('Name')
            last_name = request.form.get('last_name')
            password = request.form.get('password')
            email = str(request.form.get('email'))
            message = f'YOUR OTP FOR REGISTERING IN RENTROMIO IS \n {otp}',
            sub = f"YOUR OTP FOR RENTROMEO SIGNUP IS {otp}"
            message = render_template('trial.html')
            mail.send_message( 
                            subject=sub,
                            sender='dhananajayarne@gmail.com',
                            recipients=[email],
                            body= message 
                            )
                            
            user  = [first_name,last_name,password,email,otp]
            session['user'] = user
            flash(f'Your OTP is sent succesfully To {email}.\n Your otp IS {otp}')
            print(f'Your OTP is sent succesfully To {email}.\n Your otp IS {otp}')
            return redirect(url_for('otp'))
    return render_template('Register.html')


# MAKING OTP ROUTE
@app.route("/otp", methods=['GET','POST'])
def otp():
    user = session.get('user')
    if request.method == 'POST':
        otp = request.form.get('otp')
        otp = str(otp)
        if otp == user[4]:
            entry = Register_data(first_name = user[0],last_name = user[1], password =  generate_password_hash(user[2],method='sha256'),email = user[3],date = datetime.datetime.now())
            db.session.add(entry)
            db.session.commit()
            flash('Your Email Is Registered Succesfully')
            return redirect(url_for('login'))
        else:
            flash('You Entered Wrong OTP! Please Check Your OTP.')
            return redirect(url_for('otp'))

    return render_template('otp.html')

# MAKING FORGOUT PASSWORD ROUTE
@app.route("/forgot_pass",methods=['GET','POST']) 
def forgot_pass():
    if request.method == 'POST':
        email = request.form.get('email')
        user  = Register_data.query.filter_by(email=email).first()
        if user:
            otp = str(random.randint(10000,99999))
            mail.send_message( 'RentRomeo Password Reset Email Verification',
                            sender='dhananajayarne@gmail.com',
                            recipients=[email],
                            body= otp )
            forgot_user = [email,otp]
            session['forgot_user'] = forgot_user
            flash(f'YOUR OTP IS SUCCESFULLY SENT TO {email},\n{otp}')
            return redirect(url_for('forgot_otp'))
    return render_template("forget.html")  

# MAKING THAT OTP ROUTE WHICH WILL BE USED IN FORGOT PASSWORD ALGORITHM
@app.route("/forgot_otp", methods=['GET','POST'])
def forgot_otp():
    forgot_user = session.get('forgot_user')
    if request.method == 'POST':
        otp_forgot = request.form.get('otp')
       
        if otp_forgot == forgot_user[1]:
            flash("OTP CONFIRMED!\n RESET YOUR PASSWORD")
            return redirect(url_for('new_pass'))
        else:
            flash("YOUR OTP IS INCORRECT.TRY AGAIN")
    return render_template("otp_forgot.html")

# MAKING NEW PASSWORD ENTERING ROUTE
@app.route("/new_pass",methods=['GET','POST'])
def new_pass():
    forgot_user = session.get('forgot_user')
    email_forgot = forgot_user[0]
    if request.method == 'POST':
        new_pass = request.form.get('password')
        hash_new_pass = generate_password_hash(new_pass,method='sha256')
        mycursorn = mydb.cursor(MySQLdb.cursors.DictCursor)
        mycursorn.execute("UPDATE Register_data SET password='{}' where email = '{}'".format(hash_new_pass,email_forgot))
        mydb.commit()
        mail.send_message( 'YOUR RENT ROMEO PASSSWORD IS REST',
                            sender='dhananajayarne@gmail.com',
                            recipients=[email_forgot],
                            body= f"YOUR PASSWORD WAS CHANGD on {datetime.datetime.now()}" )
        flash('PASSWORD IS CHANGED SUCCESFULLY')
        return redirect(url_for('login'))
    return render_template("new_pass.html")

# MAKING LOGIN ROUTE
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        session['user_email'] = email
        user_account = Register_data.query.filter_by(email=email).first()
        if user_account:
            if check_password_hash(user_account.password,password):
                login_user(user_account,remember=True)
                flash(f'WELCOME {user_account.first_name} ')
                return redirect(url_for('dashboard'))
            else:
                flash(f'USERNAME OR PASSWORD IS INCORRECT')
                return redirect(url_for('login'))
        else:
            flash('YOUR EMAIL IS NOT REGISTERED YET!')
            return render_template('index.html')
    return render_template('index.html') 

# MAKING LOGOUT ROUTE
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
""" ================REGISTRATION , LOGIN , LOGOUT,  FORGOT PASSWORD=========<END>========================="""






















""" ================USER PROFILE, EDIT USER PROFILE , DELETE USER PROFILE=========<START>================="""

@app.route("/user_profile",methods = ['GET','POST'])
@login_required
def user_profile():
    email = session.get('user_email')
    user = Register_data.query.filter_by(email = email).first()
    return render_template("profile.html",user=user)


@app.route("/edit_uprofile")
@login_required
def edit_uprofile():
    user = Register_data.query.filter_by(id = id).first()
    return render_template("user.html",user = user)



@app.route("/edit_profile/<string:id>",methods = ['GET','POST'])
@login_required
def edit_profile(id):
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        birthday = request.form.get('birthday')
        instagram = request.form.get('instagram')
        facebook = request.form.get('facebook')
        phone_no = request.form.get('phone_no')
        state = request.form.get('state')
        district = request.form.get('district')
        pincode = request.form.get('pincode')


        user = Register_data.query.filter_by(id = id).first()
        user.first_name = first_name
        user.last_name = last_name
        user.birthday = birthday
        user.instagram = instagram
        user.facebook =facebook
        user.phone_no =phone_no
        user.state =state
        user.district = district
        user.pincode = pincode
        user.date = datetime.datetime.now()
        db.session.commit()
        flash("Your Profile Is Updated Suucesfully")
        return redirect(url_for('user_profile'))

    user = Register_data.query.filter_by(id = id).first()
    return render_template("user.html",user = user)


# TO DO ADD A CUSTOM JAVA SCRIPT MESSAGE HERE
# TO DO PASS THE EMAIL FROM SESSION 
@app.route("/delete_profile",methods=['GET','POST'])
@login_required
def delete_profile(id):
    if request.method == 'POST':
        email = session.get('email')
        mail.send_message( 'Your Account Has Deleted!!',
                            sender='dhananajayarne@gmail.com',
                            recipients=[Register_data.email],
                            body= f"Your RentRomeo Profile Was Deleted Succesfully")
        Register_data.query.filter_by(email=email).delete()
        db.session.commit()
        flash('Your Profile deleted Succesfully')
        return redirect(url_for('register'))
    return render_template("delete_profile.html")


""" ================USER PROFILE, EDIT USER PROFILE , DELETE USER PROFILE=========<END>================="""



















@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/feedback")
def feedback():
    return render_template("feedbaack.html")

# RUNNING FLASK APP
if __name__ == "__main__":
    app.run(debug=True)