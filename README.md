# Cars Service

Dette repository indeholder en Flask-baseret mikroservice, der administrerer biloplysninger via et RESTful API. Tjenesten understøtter funktioner som tilføjelse, visning og sletning af biler, lagring i en SQLite-database og sender begivenheder til en Event Broker.

---

## Kom godt i gang

### Installation

1. **Klon repository:**
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Installer afhængigheder:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialiser databasen:**
   ```bash
   python car_database.py
   ```

4. **Start applikationen:**
   ```bash
   python app.py
   ```

### Environment-variabler

Denne service bruger følgende variabler fra .env-filen:

| Variabel         | Beskrivelse                        | Standardværdi       |
|------------------|------------------------------------|---------------------|
| DB_PATH          | Sti til SQLite-databasen           | car_inventory.db    |
| FLASK_ENV        | Flask-miljø (development anbefalet)| development         |
| KEY              | JWT secret key til autentifikation | your_secret_key     |
| EVENT_SERVICE_URL| URL til Event Broker               | (skal angives manuelt)|

### API Endpoints

1. **Hent alle biler**
   - URL: `/cars`
   - Metode: `GET`
   - Autentifikation: JWT (påkrævet)
   - Response:
     ```json
     [
         {
             "car_id": 1,
             "brand": "Toyota",
             "model": "Corolla",
             "fuel_type": "Petrol",
             "mileage": 12000,
             "is_rented": false,
             "has_damage": false
         }
     ]
     ```

2. **Hent specifik bil**
   - URL: `/cars/<car_id>`
   - Metode: `GET`
   - Autentifikation: JWT (påkrævet)
   - Response:
     ```json
     {
         "car_id": 1,
         "brand": "Toyota",
         "model": "Corolla",
         "fuel_type": "Petrol",
         "mileage": 12000,
         "is_rented": false,
         "has_damage": false
     }
     ```
   - 404 Not Found: Hvis bilen ikke findes.

3. **Tilføj en ny bil**
   - URL: `/cars/add`
   - Metode: `POST`
   - Autentifikation: JWT (påkrævet)
   - Request Body:
     ```json
     {
         "brand": "Toyota",
         "model": "Corolla",
         "fuel_type": "Petrol",
         "mileage": 12000,
         "is_rented": false,
         "has_damage": false
     }
     ```
   - Response:
     ```json
     {
         "message": "Car added successfully",
         "car_id": 1
     }
     ```
   - 400 Bad Request: Hvis påkrævede felter mangler.

### Event Broker Integration

Tjenesten sender begivenheder til en Event Broker via HTTP POST, når der tilføjes en ny bil.

- **Standard URL:** EVENT_SERVICE_URL fra .env.

#### Alternativer til HTTP POST

1. **Asynkrone køsystemer**
   - Eksempler: RabbitMQ, Apache Kafka.
   - Fordele: Pålidelige og skalerbare.
   - Ulemper: Kræver mere opsætning og overvågning.

2. **Webhooks**
   - Fordele: Simpel og nem at implementere.
   - Ulemper: Mindre robust ved netværksfejl.

### Bemærkninger

- **Databasen:** Bruger SQLite (car_inventory.db). Overvej en skalerbar løsning til produktion.
- **Autentifikation:** JWT bruges til at beskytte API'et.

### Licens

Projektet er licenseret under MIT License. 😊