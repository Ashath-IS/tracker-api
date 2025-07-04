# 🧠 Learning Tracker - Backend API

This is the Django-based backend server for the **Learning Tracker App**. It manages topics, quiz questions, user answers, and progress tracking.

---

## 🚀 Features

- 🔐 Email-based User Authentication
- 🧩 Multiple-choice quiz per topic
- ✅ Tracks user answers with correctness
- 📊 Per-topic progress & score calculation
- 🗃️ PostgreSQL data persistence

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Django 5.x**
- **PostgreSQL**
- **Django ORM**
- **CORS + JSON APIs**

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/learning-tracker-backend.git
cd learning-tracker-backend
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is not present, you can generate one using:
> ```bash
> pip freeze > requirements.txt
> ```

### 4. Configure PostgreSQL Database

Edit `backend/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'public',
        'USER': 'admin',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Make sure your PostgreSQL server is running.

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Start the Server

```bash
python manage.py runserver
```

Visit: [http://localhost:8000](http://localhost:8000)

---

## 🔌 API Endpoints

| Endpoint                         | Method | Description                            |
|----------------------------------|--------|----------------------------------------|
| `/api/user/?email=...`          | GET    | Get user by email                      |
| `/api/users/`                   | GET    | List all users                         |
| `/api/create/`                  | POST   | Create a new user                      |
| `/api/questions/`               | GET    | Get questions by topic & user_id       |
| `/api/answer/`                  | POST   | Submit selected answer                 |
| `/api/progress/?user_id=...`    | GET    | Get per-topic progress & score         |

---

## 📘 Example: Submit Answer

```json
POST /api/answer/

{
  "user_id": 1,
  "question_id": 4,
  "selected_option_id": 13
}
```

---

## 📦 Example Response: Progress

```json
{
  "progress": [
    {
      "id": 1,
      "name": "React",
      "total_questions": 5,
      "completed": 5,
      "percent": 100.0,
      "correct_count": 4,
      "wrong_count": 1
    },
    {
      "id": 2,
      "name": "JS",
      "total_questions": 5,
      "completed": 2,
      "percent": 40.0
    }
  ]
}
```

---

## 🧑‍💻 Developer Notes

- All API responses are in JSON format.
- CSRF is disabled for API endpoints (for now).
- Use Postman or your frontend to test endpoints via Axios.

---

## 🧩 Roadmap Ideas

- [ ] JWT-based authentication
- [ ] Role-based admin panel
- [ ] Restrict re-answering questions
- [ ] Real-time quiz analytics
- [ ] Docker support

---

## 🧑‍🔧 Author

Created by **Ashath IS**

---

## 📄 License

MIT License
