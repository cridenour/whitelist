from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from .utils import generate_access_key


class VIP(models.Model):
    user = models.ForeignKey(User, related_name='vips', on_delete=models.CASCADE)
    current_username = models.CharField(max_length=32, default='', blank=True)
    uuid = models.CharField(max_length=32, default='', help_text='Mojang UUID', blank=True)


class Banned(models.Model):
    user = models.ForeignKey(User, related_name='banned', on_delete=models.CASCADE)
    current_username = models.CharField(max_length=32, default='', blank=True)
    uuid = models.CharField(max_length=32, default='', help_text='Mojang UUID', blank=True)


class Whitelist(models.Model):
    user = models.OneToOneField(User, related_name='whitelist', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='whitelists_joined', blank=True)

    # Special people
    vips = models.ManyToManyField(VIP, related_name='whitelists_joined', blank=True)
    bans = models.ManyToManyField(Banned, related_name='whitelists_banned', blank=True)

    public = models.BooleanField(default=False)
    access_key = models.CharField(max_length=32, default=generate_access_key)

    @property
    def member_count(self):
        return self.members.all().count() + self.vips.all().count()

    def clear_cache(self):
        pass


class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions', on_delete=models.CASCADE)
    broadcaster = models.ForeignKey(User, related_name='subscribers', on_delete=models.CASCADE)
    last_verified = models.DateTimeField(default=now, db_index=True)
