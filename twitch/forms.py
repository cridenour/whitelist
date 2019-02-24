from django import forms

from mojang.api import get_uuid


class JoinChannelForm(forms.Form):
    current_username = forms.CharField(max_length=32, required=False)

    def clean_current_username(self):
        data = self.cleaned_data['current_username']

        if data:
            # Ask mojang to validate
            mojang_resp = get_uuid(data)

            if not mojang_resp:
                raise forms.ValidationError('Invalid username. Please check and try again.')

            try:
                data = mojang_resp['name']
                self.cleaned_data['uuid'] = mojang_resp['id']
            except KeyError:
                raise forms.ValidationError('Error talking with Mojang. Please try again.')

        return data


class WhitelistForm(forms.Form):
    public = forms.BooleanField(required=False)
