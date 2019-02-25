from django.core.management import BaseCommand
from django.db.models import Count

from mojang.models import Profile
from mojang.api import name_history
from twitch.models import VIP, Banned


class Command(BaseCommand):
    help = 'Ask Mojang API for the latest usernames'

    def update_username(self, profile_like):
        # Get latest username
        data = name_history(profile_like.uuid)
        try:
            name = data[0]['name']
            if name != profile_like.current_username:
                profile_like.current_username = name
                profile_like.save()

        except KeyError:
            pass

    def handle(self, *args, **options):
        # Profiles first
        for profile in Profile.objects.exclude(uuid='').iterator():
            self.update_username(profile)

        # VIPs (only current)
        for vip in VIP.objects.annotate(
                whitelists=Count('whitelists_joined')).exclude(uuid='', whitelists=0).iterator():
            self.update_username(vip)

        # Bans
        for ban in Banned.objects.annotate(
                whitelists=Count('whitelists_banned')).exclude(uuid='', whitelists=0).iterator():
            self.update_username(ban)
