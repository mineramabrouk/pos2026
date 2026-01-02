from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Creates default user groups and permissions'

    def handle(self, *args, **options):
        # Create Admin Group
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Admin group'))
        else:
            self.stdout.write(self.style.WARNING('Admin group already exists'))

        # Create Salesperson Group
        sales_group, created = Group.objects.get_or_create(name='Salesperson')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Salesperson group'))
        else:
            self.stdout.write(self.style.WARNING('Salesperson group already exists'))
            
        # Assign permissions (placeholder for now, can be expanded)
        # For example, Salesperson might only have "add_transaction" permission
        
        self.stdout.write(self.style.SUCCESS('Successfully set up roles'))
