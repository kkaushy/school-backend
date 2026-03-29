from django.core.management.base import BaseCommand
from api.models import User


class Command(BaseCommand):
    help = 'Create or reset the company_admin superuser'

    def add_arguments(self, parser):
        parser.add_argument('--email',    default='kkaushy@gmail.com')
        parser.add_argument('--password', default='RR5gL4zPnAM9!$#6')
        parser.add_argument('--name',     default='Admin User')

    def handle(self, *args, **options):
        email = options['email']
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'name': options['name'], 'role': 'company_admin'},
        )
        user.set_password(options['password'])
        user.is_staff = True
        user.is_superuser = True
        user.save()
        action = 'Created' if created else 'Reset password for'
        self.stdout.write(self.style.SUCCESS(f'{action} admin: {email}'))
