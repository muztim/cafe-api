from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select
from random import randint, choice


app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # -------------- render result to a dictionary --------------- #
    def to_dict(self):
        # method 1 : Loop through each element in the data row
        # dictionary = {}
        # for column in self.__table__.columns:
        #     """ Create a new dictionary entry; where the key is the name of the column
        #     and the value is the value of the column"""
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary

        # method 2: Uses dictionary comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# --------------- All routes --------------- #
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def get_random_cafe():
    # return random record object from database using built functions
    # random_cafe = db.session.query(Cafe).order_by(func.random()).first()
    random_cafe = choice(db.session.query(Cafe).all())  # Does the same thing with python syntax
    # cafe_dictionary = random_cafe.__dict__
    # print(cafe_dictionary)
    # del cafe_dictionary["_sa_instance_state"]
    # return jsonify(cafe_dictionary)

                    # or

    # convert the random_cafe data record to a dictionary of key-value pairs
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_cafes():
    all_cafes = Cafe.query.all()
    return jsonify(cafe=[cafe.to_dict() for cafe in all_cafes])


# HTTP GET - Read Record
@app.route('/search')
def search_cafe_location():
    query_location = request.args.get('loc')
    cafes = Cafe.query.filter_by(location=query_location).all()
    if cafes:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Error": "Sorry, we don't have a cafe at the that location."})

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
