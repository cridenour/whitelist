import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
from django.urls import reverse
from django.utils.timezone import now
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import redirect

from twitch.api import update_subscription_status
from .models import Whitelist, VIP, Banned
from .forms import JoinChannelForm, WhitelistForm


class ExplainerView(TemplateView):
    template_name = 'explainer.html'


class TwitchConnectView(TemplateView):
    template_name = 'twitch_connect.html'

    broadcaster = None
    whitelist = None

    def dispatch(self, request, *args, **kwargs):
        # Logged in users can jump straight to join
        if request.user.is_authenticated:
            return redirect('broadcaster-join', username=kwargs['username'])

        # Add the important pieces up here I guess
        self.broadcaster = User.objects.filter(username=kwargs['username']).first()
        self.whitelist = Whitelist.objects.filter(user=self.broadcaster).first()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.broadcaster:
            context['unknown_broadcaster'] = True
            return context

        if not self.whitelist:
            context['no_whitelist'] = True
            return context

        context['broadcaster'] = self.broadcaster.username
        context['existing'] = self.whitelist.member_count

        return context


class TwitchJoinView(FormView):
    template_name = 'twitch_join.html'
    form_class = JoinChannelForm
    success_url = '/profile'

    broadcaster = None
    whitelist = None

    def dispatch(self, request, *args, **kwargs):
        # Need to be logged in
        if not request.user.is_authenticated:
            return redirect('broadcaster-connect', username=kwargs['username'])

        # Add the important pieces up here I guess
        self.broadcaster = User.objects.filter(username=kwargs['username']).first()
        self.whitelist = Whitelist.objects.filter(user=self.broadcaster).first()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.broadcaster:
            context['unknown_broadcaster'] = True
            return context

        if not self.whitelist:
            context['no_whitelist'] = True
            return context

        if not settings.DEBUG:
            update_subscription_status(self.broadcaster, self.request.user)

        context['needs_mojang'] = self.request.user.profile.uuid == ''

        context['broadcaster'] = self.broadcaster.username
        context['existing'] = self.whitelist.member_count
        context['joined'] = self.whitelist.user == self.request.user or self.whitelist.members.filter(
            id=self.request.user.id).exists()

        three_days_ago = now() - timedelta(days=3)
        context['subscriber'] = self.whitelist.user == self.request.user or \
            self.request.user.subscriptions.filter(
                broadcaster=self.broadcaster, last_verified__gte=three_days_ago).exists()

        return context

    def form_valid(self, form):
        # Add their username to their profile
        if form.cleaned_data['current_username']:
            profile = self.request.user.profile
            profile.current_username = form.cleaned_data['current_username']
            profile.uuid = form.cleaned_data['uuid']

            profile.save()

        # Regardless, add them to the whitelist
        self.whitelist.members.add(self.request.user)
        self.whitelist.clear_cache()

        # Now redirect
        return super().form_valid(form)


class WhitelistView(FormView):
    template_name = 'whitelist.html'
    form_class = WhitelistForm
    success_url = '/profile/whitelist'

    def dispatch(self, request, *args, **kwargs):
        # Need to be logged in
        if not request.user.is_authenticated:
            return redirect('')

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        whitelist = Whitelist.objects.filter(user=self.request.user).first()
        if whitelist:
            return {'public': whitelist.public}

        return {}

    def form_valid(self, form):
        whitelist = Whitelist.objects.filter(user=self.request.user).first()
        if whitelist:
            whitelist.public = form.cleaned_data['public']
            whitelist.save()
            whitelist.clear_cache()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        whitelist = Whitelist.objects.filter(user=self.request.user).first()

        if not whitelist:
            context['no_whitelist'] = True
            return context

        three_days_ago = now() - timedelta(days=3)
        active = whitelist.members.filter(
            subscriptions__broadcaster=self.request.user,
            subscriptions__last_verified__gte=three_days_ago
        ).exclude(profile__current_username='').exclude()

        expired = whitelist.members.exclude(
            subscriptions__broadcaster=self.request.user,
            subscriptions__last_verified__gte=three_days_ago
        ).exclude(profile__current_username='')

        context['active'] = active
        context['expired'] = expired
        context['bans'] = whitelist.bans.all()
        context['vips'] = whitelist.vips.all()

        access_key = '' if whitelist.public else f'?access_key={whitelist.access_key}'

        context['txt_url'] = self.request.build_absolute_uri(
            reverse('whitelist-txt', kwargs={'username': self.request.user.username})) + access_key
        context['json_url'] = self.request.build_absolute_uri(
            reverse('whitelist-json', kwargs={'username': self.request.user.username})) + access_key

        context['invite_url'] = self.request.build_absolute_uri(
            reverse('broadcaster-connect', kwargs={'username': self.request.user.username})
        )

        return context


class AddWhitelistView(View):
    def dispatch(self, request, *args, **kwargs):
        # Need to be logged in
        if not request.user.is_authenticated:
            return redirect('')

        # Must NOT have whitelist
        whitelist = Whitelist.objects.filter(user=request.user).first()
        if whitelist:
            return redirect('whitelist')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        whitelist = Whitelist.objects.create(
            user=request.user
        )

        whitelist.clear_cache()

        return redirect('whitelist')


class AddVIPView(FormView):
    template_name = 'add_vip.html'
    form_class = JoinChannelForm
    success_url = '/profile/whitelist'

    def dispatch(self, request, *args, **kwargs):
        # Need to be logged in
        if not request.user.is_authenticated:
            return redirect('')

        # Must have whitelist
        whitelist = Whitelist.objects.filter(user=request.user).first()
        if not whitelist:
            return redirect('whitelist')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Add VIP
        if form.cleaned_data['current_username']:
            vip = VIP.objects.create(
                user=self.request.user,
                current_username=form.cleaned_data['current_username'],
                uuid=form.cleaned_data['uuid']
            )

            self.request.user.whitelist.vips.add(vip)
            self.request.user.whitelist.clear_cache()

        # Now redirect
        return super().form_valid(form)


class RemoveVIPView(View):
    def dispatch(self, request, *args, **kwargs):
        # Need to be logged in
        if not request.user.is_authenticated:
            return redirect('')

        # Must have whitelist
        whitelist = Whitelist.objects.filter(user=request.user).first()
        if not whitelist:
            return redirect('whitelist')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            vip = VIP.objects.get(id=kwargs['id'])
            whitelist = request.user.whitelist
            whitelist.vips.remove(vip)
            whitelist.clear_cache()
        except VIP.DoesNotExist:
            pass
        except Whitelist.DoesNotExist:
            pass
        finally:
            return redirect('/profile/whitelist')


class AddBanView(FormView):
    template_name = 'add_ban.html'
    form_class = JoinChannelForm
    success_url = '/profile/whitelist'

    def dispatch(self, request, *args, **kwargs):
        # Need to be logged in
        if not request.user.is_authenticated:
            return redirect('')

        # Must have whitelist
        whitelist = Whitelist.objects.filter(user=request.user).first()
        if not whitelist:
            return redirect('whitelist')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Add Ban
        if form.cleaned_data['current_username']:
            ban = Banned.objects.create(
                user=self.request.user,
                current_username=form.cleaned_data['current_username'],
                uuid=form.cleaned_data['uuid']
            )

            self.request.user.whitelist.bans.add(ban)
            self.request.user.whitelist.clear_cache()

        # Now redirect
        return super().form_valid(form)


class BanUserView(View):
    def dispatch(self, request, *args, **kwargs):
        # Need to be logged in
        if not request.user.is_authenticated:
            return redirect('')

        # Must have whitelist
        whitelist = Whitelist.objects.filter(user=request.user).first()
        if not whitelist:
            return redirect('whitelist')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs['id'])
            ban = Banned.objects.create(
                user=self.request.user,
                current_username=user.profile.current_username,
                uuid=user.profile.uuid
            )

            self.request.user.whitelist.bans.add(ban)
            self.request.user.whitelist.clear_cache()
        except Whitelist.DoesNotExist:
            pass
        except User.DoesNotExist:
            pass
        finally:
            return redirect('/profile/whitelist')


class RemoveBanView(View):
    def dispatch(self, request, *args, **kwargs):
        # Need to be logged in
        if not request.user.is_authenticated:
            return redirect('')

        # Must have whitelist
        whitelist = Whitelist.objects.filter(user=request.user).first()
        if not whitelist:
            return redirect('whitelist')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            ban = Banned.objects.get(id=kwargs['id'])
            whitelist = request.user.whitelist
            whitelist.bans.remove(ban)
            whitelist.clear_cache()
        except Banned.DoesNotExist:
            pass
        finally:
            return redirect('/profile/whitelist')


class BrowseView(TemplateView):
    template_name = 'browse.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['whitelists'] = []

        return context


class WhitelistTXTView(View):
    def get(self, request, *args, **kwargs):
        access_key = request.GET.get('access_key', '')
        cached_response = cache.get('{}{}_txt_response'.format(kwargs['username'], '_{}'.format(access_key) if access_key else ''), None)
        if cached_response:
            return cached_response

        broadcaster = User.objects.filter(username=kwargs['username']).first()
        whitelist = Whitelist.objects.filter(user=broadcaster).first()

        if not broadcaster or not whitelist:
            return HttpResponse(content_type='text/plain; charset=utf-8', content='', status=404)

        if not whitelist.public:
            if access_key != whitelist.access_key:
                response =  HttpResponse(content_type='text/plain; charset=utf-8', content='', status=404)
                cache.set('{}_txt_response'.format(kwargs['username']), response)
                return response

        # Get a set of current_username
        user_list = set()

        three_days_ago = now() - timedelta(days=3)

        for username in whitelist.members.filter(
            subscriptions__broadcaster=broadcaster,
            subscriptions__last_verified__gte=three_days_ago
        ).exclude(profile__current_username='').values_list('profile__current_username', flat=True):
            user_list.add(username)

        for vip in whitelist.vips.exclude(current_username='').values_list('current_username', flat=True):
            user_list.add(vip)

        for ban in whitelist.bans.exclude(current_username='').values_list('current_username', flat=True):
            user_list.remove(ban)

        content = '\n'.join(user_list)

        response = HttpResponse(content_type='text/plain; charset=utf-8', content=content, status=200)
        cache.set('{}{}_txt_response'.format(kwargs['username'], '_{}'.format(access_key) if access_key else ''), response)

        return response


class WhitelistJSONView(View):
    def get(self, request, *args, **kwargs):
        access_key = request.GET.get('access_key', '')
        cached_response = cache.get('{}{}_json_response'.format(kwargs['username'], '_{}'.format(access_key) if access_key else ''), None)
        if cached_response:
            return cached_response

        broadcaster = User.objects.filter(username=kwargs['username']).first()
        whitelist = Whitelist.objects.filter(user=broadcaster).first()

        if not broadcaster or not whitelist:
            return HttpResponse(content_type='application/json', content=json.dumps([]), status=404)

        if not whitelist.public:
            if access_key != whitelist.access_key:
                response = HttpResponse(content_type='application/json', content=json.dumps([]), status=404)
                cache.set('{}_json_response'.format(kwargs['username']), response)
                return response

        # Keep a set of uuids
        uuid_set = set()
        user_list = []

        three_days_ago = now() - timedelta(days=3)

        for current_username, uuid in whitelist.members.filter(
                subscriptions__broadcaster=broadcaster,
                subscriptions__last_verified__gte=three_days_ago
        ).exclude(profile__current_username='').values_list('profile__current_username', 'profile__uuid'):
            if uuid not in uuid_set:
                uuid_set.add(uuid)
                user_list.append({
                    'uuid': uuid,
                    'name': current_username
                })

        for current_username, uuid in whitelist.vips.exclude(current_username='').values_list(
                'current_username', 'uuid'):
            if uuid not in uuid_set:
                uuid_set.add(uuid)
                user_list.append({
                    'uuid': uuid,
                    'name': current_username
                })

        for current_username, uuid in whitelist.bans.exclude(current_username='').values_list(
                'current_username', 'uuid'):
            if uuid in uuid_set:
                user_list.remove({
                    'uuid': uuid,
                    'name': current_username
                })

        response = HttpResponse(content_type='application/json', content=json.dumps(list(user_list), indent=2), status=200)
        cache.set('{}{}_json_response'.format(kwargs['username'], '_{}'.format(access_key) if access_key else ''), response)

        return response


class CNameHelpView(TemplateView):
    template_name = 'cname.html'
