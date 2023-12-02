# app.py
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import qrcode


app = Flask(__name__, static_url_path='/static')

uri = "mongodb+srv://admin:passwordnebula@nebuladb.d7wj5do.mongodb.net/test"
client = MongoClient(uri)
db = client.get_database()

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = {
        "name": request.form['name'],
        "role": request.form['role'],
        "bio": request.form['bio'],
        "gender": request.form['gender'],
        "department": request.form['department'],
        "college": request.form['college']
    }

    # Insert data into MongoDB
    collection_name = "collection_" + str(hash(str(data)))
    collection = db[collection_name]
    collection.insert_one(data)

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"static/{collection_name}_qr.png")

    return redirect(url_for('display', collection_name=collection_name))

@app.route('/display/<collection_name>')
def display(collection_name):
    collection = db[collection_name]
    data = collection.find_one()
    return render_template('display.html', data=data, collection_name=collection_name)

@app.route('/edit/<collection_name>')
def edit(collection_name):
    collection = db[collection_name]
    data = collection.find_one()
    return render_template('edit.html', data=data, collection_name=collection_name)

@app.route('/submit_edit/<collection_name>', methods=['POST'])
def submit_edit(collection_name):
    collection = db[collection_name]
    
    updated_data = {
        "name": request.form['name'],
        "role": request.form['role'],
        "bio": request.form['bio'],
        "gender": request.form['gender'],
        "department": request.form['department'],
        "college": request.form['college']
    }

    # Update data in MongoDB
    collection.update_one({}, {"$set": updated_data})

    # Generate QR Code with updated data
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(updated_data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"static/{collection_name}_qr.png")

    return redirect(url_for('edited_successfully', collection_name=collection_name))

@app.route('/edited_successfully/<collection_name>')
def edited_successfully(collection_name):
    return render_template('editedsuccessfully.html', collection_name=collection_name)

if __name__ == '__main__':
    app.run(debug=True)
