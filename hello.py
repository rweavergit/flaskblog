from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Flask instance
app = Flask(__name__)
#add database
#New DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Kresnik$884@localhost/our_users'
#Old DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Secret Key
app.config['SECRET_KEY'] = 'mysecretkey'
#Init DB
db = SQLAlchemy(app)

#Create Model Class 
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Create a class
    def __repr__(self):
        return '<Name %r>' % self.name

# Create a Form Class
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')
# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/user/add', methods=['GET', 'POST'])

def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash('User added successfully!')
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
    our_users = Users.query.order_by(Users.date)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

# Route Decorator
@app.route('/')

def index():
    first_name = "Robert"
    stuff = "this is bold"


    favorite_pizza = ['pepperoni', 'cheese', 'veggie', 41]
    return render_template('index.html', first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza)

@app.route('/user/<name>')

def user(name):
    return render_template('user.html', user_name=name)

# Custom Error Pages

#invalid URL

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#Internal Server Error

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 404

# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")
    return render_template('name.html', name=name, form=form)
    