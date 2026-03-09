from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile

class Command(BaseCommand):
    help = 'Create admin user with profile'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for admin')
        parser.add_argument('--email', type=str, help='Email for admin')
        parser.add_argument('--password', type=str, help='Password for admin')

    def handle(self, *args, **options):
        username = options.get('username', 'admin')
        email = options.get('email', 'admin@example.com')
        password = options.get('password', 'admin123')

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists')
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            phone='+255123456789',
            address='123 Admin Street',
            city='Dar es Salaam',
            country='Tanzania',
            postal_code='00000'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user "{username}" with profile'
            )
        )
