from flask import Flask, jsonify, request, g
import sqlite3
import requests
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

# Load environment variables from .env file
load_dotenv()

# Get DB_PATH from environment variable or use default
DB_PATH = os.getenv('DB_PATH', 'car_inventory.db')

app = Flask(__name__)

# Configure JWT settings
app.config['JWT_SECRET_KEY'] = os.getenv('KEY', 'your_secret_key')  # Load from .env
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Ensure tokens are in headers
app.config['JWT_HEADER_NAME'] = 'Authorization'  # Default header name for JWT
app.config['JWT_HEADER_TYPE'] = 'Bearer'  # Prefix for the token (e.g., Bearer <token>)

# Initialize the JWT manager
jwt = JWTManager(app)

@app.route('/debug', methods=['GET'])
def debug():
    return jsonify({
        "JWT_SECRET_KEY": os.getenv('KEY', 'Not Set'),
        "Database_Path": DB_PATH
    }), 200


# Connect to DB
def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH) 
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        car_id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        fuel_type TEXT NOT NULL,
        mileage INTEGER NOT NULL,
        is_rented BOOLEAN NOT NULL DEFAULT 0,
        has_damage BOOLEAN NOT NULL DEFAULT 0
    )
    ''')
    conn.commit()

EVENT_SERVICE_URL = "https://eventbroker-enaza3hfeefdd0gm.northeurope-01.azurewebsites.net/events"

def notify_event_service(event_type, event_data):
    try:
        response = requests.post(EVENT_SERVICE_URL, json={
            "type": event_type,
            "data": event_data
        })
        if response.status_code == 200:
            print(f"Event '{event_type}' sent successfully with data: {event_data}")
        else:
            print(f"Failed to send event. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending event: {e}")


##### --------------- GET METHODS --------------- ##### 

# Get all cars in DB
@app.route('/cars', methods=['GET'])
@jwt_required()
def get_cars():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cars")
    cars = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify(cars), 200

# Get specific car in DB
@app.route('/cars/<int:car_id>', methods = ['GET'])
@jwt_required()
def get_car_by_id(car_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cars WHERE car_id = ?", (car_id,))
    car = cursor.fetchone()
    conn.close()

    if car is None:
        return jsonify({'Error': f'Car with ID {car_id} was not found. Try something else.'}), 404
    
    car_dict = dict(car)
    return jsonify(car_dict), 200

##### --------------- POST METHODS --------------- ##### 

# Add new car to DB
@app.route('/cars/add', methods=['POST'])
@jwt_required()
def add_car():
    data = request.json
    brand = data.get('brand')
    model = data.get('model')
    fuel_type = data.get('fuel_type')
    mileage = data.get('mileage')
    is_rented = data.get('is_rented', 0)  # Default to 0 if not provided
    has_damage = data.get('has_damage', 0)  # Default to 0 if not provided

    # Validate required fields
    if not (brand and model and fuel_type and isinstance(mileage, int) and mileage > 0):
        return jsonify({'error': 'Fields brand, model, fuel_type, and mileage (positive integer) are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert new car into the database
        cursor.execute("""
            INSERT INTO cars (brand, model, fuel_type, mileage, is_rented, has_damage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (brand, model, fuel_type, mileage, is_rented, has_damage))
        conn.commit()
        car_id = cursor.lastrowid
        
        # Notify event service about the new car
        event_data = {
            "car_id": car_id,
            "brand": brand,
            "model": model,
            "fuel_type": fuel_type,
            "mileage": mileage,
            "is_rented": is_rented,
            "has_damage": has_damage
        }
        notify_event_service("new_car_added", event_data)
        
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    conn.close()
    
    return jsonify({'message': 'Car added successfully', 'car_id': car_id}), 201

##### --------------- DElETE METHODS --------------- ##### 
# Delete a car from DB
@app.route('/cars/delete/<int:car_id>', methods=['DELETE'])
@jwt_required()
def delete_car(car_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if car exists
    cursor.execute("SELECT * FROM cars WHERE car_id = ?", (car_id,))
    car = cursor.fetchone()

    if car is None:
        conn.close()
        return jsonify({'Error': f'Car with ID {car_id} not found. Cannot delete.'}), 404

    try:
        # Delete the car from the database
        cursor.execute("DELETE FROM cars WHERE car_id = ?", (car_id,))
        conn.commit()

        # Notify event service about the car deletion
        event_data = {"car_id": car_id}
        notify_event_service("car_deleted", event_data)

    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    conn.close()
    
    return jsonify({'message': f'Car with ID {car_id} has been deleted successfully.'}), 200

# test route so we don't get 404
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "cars service",
        "version": "1.0.0",
        "description": "A RESTful API for managing cars"
    })

if __name__ == '__main__':
    app.run(debug=True)
