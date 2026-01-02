import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

def create_user(username, password, group_name):
    user, created = User.objects.get_or_create(username=username, email=f'{username}@example.com')
    user.set_password(password)
    user.save()
    if created:
        print(f'User "{username}" created.')
    else:
        print(f'User "{username}" updated.')
    
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    print(f'User "{username}" added to group "{group_name}".')

# Ensure Admin user is in Admin group
create_user('admin', 'admin', 'Admin')

# Create Salesperson user
create_user('vendedor', 'vendedor', 'Salesperson')
