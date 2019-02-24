from django.contrib import admin

from .models import Subscription, Whitelist, VIP


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass


@admin.register(Whitelist)
class WhitelistAdmin(admin.ModelAdmin):
    pass


@admin.register(VIP)
class VIPAdmin(admin.ModelAdmin):
    pass
