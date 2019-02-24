from django.core.management import BaseCommand
from django.db.models import Count

from sentry_sdk import capture_exception

from twitch.models import Whitelist
from twitch.api import verify_whitelist_subscribers


class Command(BaseCommand):
    help = 'Work with the Twitch API to figure who to kick out'

    def handle(self, *args, **options):
        # Get whitelists with twitch members (not just VIPs)
        for w in Whitelist.objects.annotate(sql_member_count=Count('members')).filter(sql_member_count__gt=0):
            try:
                verify_whitelist_subscribers(w)
                w.clear_cache()
            except ValueError as e:
                capture_exception(e)
