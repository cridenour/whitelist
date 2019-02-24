from datetime import timedelta

from django.shortcuts import redirect
from django.utils.timezone import now
from django.views import View
from django.views.generic.edit import FormView

from .forms import EditProfileForm


class ProfileView(FormView):
    template_name = 'profile.html'
    form_class = EditProfileForm
    success_url = '/profile'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        three_days_ago = now() - timedelta(days=3)

        subscriptions = self.request.user.subscriptions.filter(
            last_verified__gte=three_days_ago).values_list('broadcaster_id', flat=True)

        context['profile'] = self.request.user.profile
        context['active'] = self.request.user.whitelists_joined.filter(user_id__in=subscriptions)
        context['expired'] = self.request.user.whitelists_joined.exclude(user_id__in=subscriptions)

        return context

    def form_valid(self, form):
        # We should have a current_username and uuid in cleaned_data now
        profile = self.request.user.profile
        profile.current_username = form.cleaned_data['current_username']
        profile.uuid = form.cleaned_data['uuid']

        profile.save()

        return super().form_valid(form)


class RefreshUsername(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # TODO: Force refresh username in our system
        pass
