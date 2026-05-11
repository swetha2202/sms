# EduManage

A multi-tenant school management system built with Django. Schools are isolated from each other — each one has its own users, classes, and content.

Built as part of a 24-hour machine test.

---

## The idea

Three types of users, each with their own slice of the system:

- **Super Admin** — manages schools at the platform level. Can create, edit, or deactivate any school.
- **School Admin** — runs things inside their school. Creates teachers and students, sets up classes, assigns subjects, posts announcements.
- **Teacher** — uploads notes and videos for their classes.
- **Student** — logs in and sees whatever their teacher has uploaded for them.

Login requires a school code, username, and password. Super admin just uses `ADMIN` as the code.

---

## Stack

- Django + SQLite (dev) / PostgreSQL (prod)
- Bootstrap 5 for the frontend — nothing fancy
- Local file storage, or swap in S3 if needed

---

## Running locally

```bash
git clone <your-repo-url>
cd school_mgmt

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# fill in SECRET_KEY and database settings

python manage.py migrate
python manage.py runserver
```

Then seed the database with test users:

```bash
python manage.py shell
```

```python
from accounts.models import User
from schools.models import School

school = School.objects.create(name='Demo School', school_code='SCH001', is_active=True)

User.objects.create_superuser(username='superadmin', email='superadmin@example.com', password='admin123', role='super_admin', is_staff=True, is_superuser=True)
User.objects.create_user(username='schooladmin', password='admin123', role='school_admin', school=school)
User.objects.create_user(username='teacher1', password='admin123', role='teacher', school=school)
User.objects.create_user(username='student1', password='admin123', role='student', school=school)
```

Go to http://127.0.0.1:8000/login/

---

## Test accounts

| Role         | School Code | Username     | Password  |
|--------------|-------------|--------------|-----------|
| Super Admin  | `ADMIN`     | `superadmin` | `admin123`|
| School Admin | `SCH001`    | `schooladmin`| `admin123`|
| Teacher      | `SCH001`    | `teacher1`   | `admin123`|
| Student      | `SCH001`    | `student1`   | `admin123`|

---

## Deploying to Render

Push to GitHub, create a Web Service on Render, and set these env vars:

```
SECRET_KEY=<generate one>
DATABASE_URL=<from your postgres add-on>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
```

Build command: `./build.sh`
Start command: `gunicorn core.wsgi`

The build script handles migrations and seeds the superadmin automatically.

---

## Project layout

```
school_mgmt/
├── core/          # settings, root urls
├── accounts/      # user model, login
├── schools/       # schools, classes, subjects
├── content/       # study materials, announcements
├── templates/     # all html templates
├── media/         # uploaded files (gitignored)
├── build.sh       # render build script
└── requirements.txt
```

---

## Notes

- All data is scoped to `request.user.school` — no cross-tenant leaks
- Passwords hashed with Django's default PBKDF2
- CSRF enabled on all forms
- Switch SQLite → PostgreSQL before going live, seriously

## Live Demo
https://edumanage-p11l.onrender.com