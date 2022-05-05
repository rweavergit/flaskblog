from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

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
migrate = Migrate(app, db)

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
    return render_template('login.html', form=form)

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    return render_template('dashboard.html')

# Create Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

# Create Post Form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Post')

# Post List
@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

# Individual Post Page
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

# Edit Post Page
@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
def edit_post(id):
    form = PostForm()
    post = Posts.query.get_or_404(id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.author = form.author.data
        post.slug = form.slug.data
        #Update DB
        db.session.add(post)
        db.session.commit()
        flash('Your post has been updated!')
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.content.data = post.content
    form.slug.data = post.slug
    return render_template('edit_post.html', form=form, post=post)

# Delete Post Page
@app.route('/posts/<int:id>/delete')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Your post has been deleted!')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)
        
    except:
        flash('Something went wrong!')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

# Add Post Page
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        # Clear the Form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        # Add Post to DB
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!')

    return render_template("add_post.html", form=form)

#Jsons
@app.route('/date')
def get_current_date():
    return {"Date": date.today()}



#Create Model Class 
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    #Password
    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('You cannot read the password attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a class
    def __repr__(self):
        return '<Name %r>' % self.name

# Create a Form Class
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    favorite_color = StringField('Favorite Color')
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Delete User
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully')

        our_users = Users.query.order_by(Users.date)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
        
    except:
        flash('Error Deleting User')
        return render_template('add_user.html', form=form, name=name, our_users=our_users)

# Update the database
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form.name
        name_to_update.email = request.form.email
        name_to_update.favorite_color = request.form.favorite_color
        try:
            db.session.commit()
            flash('User Updated Successfully')
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            flash('Error Updating User')
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)



# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Create a Password Form Class
class PasswordForm(FlaskForm):
    email = StringField('What is your email?', validators=[DataRequired()])
    password_hash = PasswordField('What is your Password?', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, username=form.username.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''
        
        flash('User added successfully!')
    our_users = Users.query.order_by(Users.date_added)
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

# Invalid URL

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

    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")
    return render_template('name.html', name=name, form=form)
    
# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    #Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        form.email.data = ''
        form.password_hash.data = ''

        #Lookup User by Email
        pw_to_check = Users.query.filter_by(email=email).first()

        #Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)
    return render_template('test_pw.html', email=email, password=password, form=form, pw_to_check=pw_to_check, passed=passed)
    
