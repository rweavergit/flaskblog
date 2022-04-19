from flask import Flask, render_template


# Flask instance
app = Flask(__name__)

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