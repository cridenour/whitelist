from django.core.management import BaseCommand

from mojang.models import Profile
from mojang.api import name_history


class Command(BaseCommand):
    help = 'Ask Mojang API for the latest usernames'

    def handle(self, *args, **options):
        for profile in Profile.objects.exclude(uuid='').iterator():
            # Get latest username
            data = name_history(profile.uuid)
            try:
                name = data[0]['name']
                if name != profile.current_username:
                    profile.current_username = name
                    profile.save()

            except KeyError:
                pass
