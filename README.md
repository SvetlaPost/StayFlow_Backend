# Test StayFlow

## English

Test StayFlow is a modern web-based housing rental platform built with Django and Django REST Framework. It enables hosts to publish rental listings and renters to book them either daily or monthly. The platform is focused on simplicity, efficiency, and transparency in the rental process.

### 🔧 Features

* User registration, login, and JWT-based authentication
* Separate dashboards for hosts and renters
* Listing creation, update, soft deletion and restoration
* Booking system with confirmation status
* Ratings and reviews with average score calculation
* Renter and host statistics
* Commission-based payment system
* Logging and console/email notifications

### 🛠 Technologies

* Python 3.12
* Django 5.x
* Django REST Framework
* MySQL or SQLite
* JWT Authentication (`SimpleJWT`)
* Swagger / Redoc API documentation (`drf-yasg`)

### 🚀 Installation

```bash
git clone <your-repo-url>
cd Test_StayFlow
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set up a `.env` file:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=mysql://user:password@localhost/dbname
```

Run the server:

```bash
python manage.py migrate
python manage.py runserver
```

Visit the API docs at `http://127.0.0.1:8000/swagger/`

---

## Deutsch

Test StayFlow ist eine moderne, webbasierte Plattform für Wohnungsvermietung, entwickelt mit Django und dem Django REST Framework. Gastgeber können Inserate einstellen, während Mieter diese täglich oder monatlich buchen können. Die Plattform legt Wert auf Benutzerfreundlichkeit und Transparenz.

### 🔧 Funktionen

* Registrierung, Login und JWT-Authentifizierung
* Eigene Dashboards für Vermieter und Mieter
* Erstellung, Aktualisierung und Soft-Löschung von Inseraten
* Buchungssystem mit Bestätigungsstatus
* Bewertungen und Rezensionen mit Durchschnittsberechnung
* Statistiken für Vermieter und Mieter
* Provisionsbasierte Zahlungsabwicklung
* Logging und Benachrichtigungen per Konsole oder E-Mail

### 🛠 Technologien

* Python 3.12
* Django 5.x
* Django REST Framework
* MySQL oder SQLite
* JWT-Authentifizierung (`SimpleJWT`)
* API-Dokumentation mit Swagger / Redoc (`drf-yasg`)

### 🚀 Installation

```bash
git clone <your-repo-url>
cd Test_StayFlow
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Konfiguriere die `.env` Datei:

```
SECRET_KEY=dein-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=mysql://benutzer:passwort@localhost/datenbank
```

Starte den Server:

```bash
python manage.py migrate
python manage.py runserver
```

API-Dokumentation erreichbar unter `http://127.0.0.1:8000/swagger/`
