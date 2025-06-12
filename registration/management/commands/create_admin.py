from django.core.management.base import BaseCommand
from registration.models import User

class Command(BaseCommand):
    help = 'Creates an admin user'

    def handle(self, *args, **kwargs):
        try:
            admin = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                user_type='ADMIN',
                is_staff=True,
                is_superuser=True
            )
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {str(e)}')) 