#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(username='superadmin').exists():
    User.objects.create_superuser('superadmin', 'admin@example.com', 'admin123', role='super_admin')
    print('Superadmin created')
"
