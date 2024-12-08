from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Connect to DB
def connect_db():
    conn = sqlite3.connect('car_inventory.db')
    conn.row_factory = sqlite3.Row  # Return results as dictionaries
    return conn

##### --------------- GET METHODS --------------- #####

# Get all cars in DB
@app.route('/cars', methods=['GET'])
def get_cars():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cars")
    cars = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify(cars), 200

# Get specific car in DB
@app.route('/cars/<int:car_id>', methods = ['GET'])
def get_car_by_id(car_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cars WHERE car_id = ?", (car_id,))
    car = cursor.fetchone()
    conn.close()

    if car is None:
        return jsonify({'Error': f'Car with ID {car_id} was not found. Try something else.'})
    
    car_dict = dict(car)
    return jsonify(car_dict), 200

# Get all cars with damage in DB
@app.route('/cars/damaged', methods = ['GET'])
def get_damaged_cars():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cars WHERE has_damage = 1")
    damaged_cars = [dict(row) for row in cursor.fetchall()] 
    conn.close

    if not damaged_cars:
        return jsonify({'No cars require service at the moment.'}), 404

    return jsonify(damaged_cars), 200

##### --------------- PUT METHODS --------------- #####

# Add car to DB
@app.route('/cars', methods=['POST'])
def add_car():
    data = request.json
    brand = data.get('brand')
    model = data.get('model')
    fuel_type = data.get('fuel_type')
    mileage = data.get('mileage')
    status = data.get('status')
    has_damage = data.get('has_damage', 0) 

    if not (brand and model and fuel_type and mileage and status):
        return jsonify({'error': 'All fields are required'}), 400

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cars (brand, model, fuel_type, mileage, status, has_damage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (brand, model, fuel_type, mileage, status, has_damage))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Car added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)