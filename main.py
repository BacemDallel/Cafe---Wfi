from flask import Flask, jsonify, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Café TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(250), nullable=True)
    seats = db.Column(db.String(250), nullable=True)
    has_toilet = db.Column(db.Boolean, nullable=True)
    has_wifi = db.Column(db.Boolean, nullable=True)
    has_sockets = db.Column(db.Boolean, nullable=True)
    can_take_calls = db.Column(db.Boolean, nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    # Convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    # This uses a List Comprehension, but you could also split it into 3 lines.
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def search():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    # Because we can get more than one café per location:
    all_cafes = result.scalars().all()
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={'Not found': 'Sorry, we do not have a cafe at this location'}), 404


@app.route("/add", methods=["POST"])
def post_new_cafe():
    name = request.form.get("name")
    map_url = request.form.get("map_url")
    img_url = request.form.get("img_url")
    location = request.form.get("location")  # Ensure location is provided

    # Validate if the required data is present before creating the Cafe object
    if name and map_url and img_url and location:
        new_cafe = Cafe(
            name=name,
            map_url=map_url,
            img_url=img_url,
            location=location,  # Assign provided location value
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )

        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})
    else:
        return jsonify(response={"error": "Missing required data for the cafe."})



@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    all_cafes = db.session.execute(db.select(Cafe)).scalars()
    all_cafe_ids = [cafe.id for cafe in all_cafes]
    if cafe_id in all_cafe_ids:
        cafe_to_update = db.get_or_404(Cafe, cafe_id)
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the price")
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"})




@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    all_cafes = db.session.execute(db.select(Cafe)).scalars()
    all_cafe_ids = [cafe.id for cafe in all_cafes]

    if api_key == "TopSecretAPIKey":
        if cafe_id in all_cafe_ids:
            cafe = db.get_or_404(Cafe, cafe_id)
            if cafe:
                db.session.delete(cafe)
                db.session.commit()
                return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
            else:
                return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
        else:
            return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
    else:
        return jsonify(error={"Unauthorized": "Access denied. Please provide a valid API key."}), 401
# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
