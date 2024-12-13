import sqlite3

# Opret tabellen
conn = sqlite3.connect("car_inventory.db")
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

# Gem ændringer og luk forbindelsen
conn.commit()
conn.close()
