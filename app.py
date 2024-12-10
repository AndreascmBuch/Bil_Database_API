from flask import Flask, jsonify, request
import sqlite3
import requests


app = Flask(__name__)

# Connect to DB
def connect_db():
    conn = sqlite3.connect('car_inventory.db')
    conn.row_factory = sqlite3.Row  # Return results as dictionaries
    return conn 

EVENT_SERVICE_URL = "https://eventbroker-enaza3hfeefdd0gm.northeurope-01.azurewebsites.net/events"

def notify_event_service(event_type, event_data):
    try:
        response = requests.post(EVENT_SERVICE_URL, json={
            "type": event_type,
            "data": event_data
        })
        if response.status_code == 200:
            print(f"Event '{event_type}' sent successfully")
        else:
            print(f"Failed to send event. Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending event: {e}")

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
@app.route('/cars', methods=['POST'])
def add_car():
    data = request.json
    brand = data.get('brand')
    model = data.get('model')
    fuel_type = data.get('fuel_type')
    mileage = data.get('mileage')
    is_rented = data.get('is_rented', 0)  # Standardværdi er 0, hvis ikke angivet
    has_damage = data.get('has_damage', 0)  # Standardværdi er 0, hvis ikke angivet

    # Valider påkrævede felter
    if not (brand and model and fuel_type and mileage):
        return jsonify({'error': 'Fields brand, model, fuel_type, and mileage are required'}), 400

    # Opret forbindelse til databasen
    conn = connect_db()
    cursor = conn.cursor()

    # Indsæt data i tabellen
    cursor.execute("""
        INSERT INTO cars (brand, model, fuel_type, mileage, is_rented, has_damage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (brand, model, fuel_type, mileage, is_rented, has_damage))

    conn.commit() 
    car_id = cursor.lastrowid  # Hent ID for den indsatte bil
    # Efter commit og før return
    notify_event_service("new_car_added", {"car_id": car_id,"brand": brand,"model": model,"fuel_type": fuel_type,"mileage": mileage,"is_rented": is_rented,"has_damage": has_damage})
    conn.close()

    # Giv feedback til klienten
    return jsonify({'message': 'Car added successfully', 'car_id': car_id}), 201


if __name__ == '__main__':
    app.run()