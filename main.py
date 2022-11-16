from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select
from random import randint, choice
import config


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
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes]), 200
    else:
        return jsonify(error={"Error": "Sorry, we don't have a cafe at the that location."}), 404


# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."}), 200


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['PATCH', 'GET'])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": "Successfully updated the price"}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404


# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def close_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == config.API_KEY:
        cafe = Cafe.query.get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            db.session.close_all_sessions()
            return jsonify(response={"Success": "Successfully deleted cafe"}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
