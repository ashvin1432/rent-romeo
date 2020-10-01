from flask import Flask 
from flask import request 
from flask import render_template

from flask_mail import Mail,Message

app = Flask(__name__)
mail = Mail(app)


@app.route("/login", methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        msg = Message("Send Mail Tutorial!", sender="dhananjayarne@gmail.com", recipients=["ashvin4615@gmail.com"])
        msg.html = "<b>testing</b>"
        mail.send(msg)


        return 'Mail sent!'
    return render_template('trial.html')

app.run(debug=True)