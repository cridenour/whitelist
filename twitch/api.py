import requests
from django.utils.timezone import now
from social_django.utils import load_strategy

from twitch.models import Subscription


def update_subscription_status(broadcaster, user):
    broadcaster_social = broadcaster.social_auth.filter(provider='twitch').first()
    user_social = user.social_auth.filter(provider='twitch').first()

    if not broadcaster_social:
        raise ValueError('Missing social data for broadcaster.')

    broadcaster_token = broadcaster_social.get_access_token(load_strategy())
    resp = requests.get('https://api.twitch.tv/helix/subscriptions',
                        headers={'Authorization': f'Bearer {broadcaster_token}'},
                        params={
                            'broadcaster_id': broadcaster_social.uid,
                            'user_id': user_social.uid,
                        })

    # If the length is greater than 0, they're good.
    if not resp.ok:
        raise ValueError('Error retrieving subscription information.')

    data = resp.json()['data']

    if len(data) > 0:
        Subscription.objects.update_or_create(
            broadcaster=broadcaster,
            user=user,
            defaults={
                'last_verified': now()
            }
        )


def verify_whitelist_subscribers(whitelist):
    broadcaster = whitelist.user
    broadcaster_social = broadcaster.social_auth.filter(provider='twitch').first()

    if not broadcaster_social:
        raise ValueError('Missing social data for broadcaster.')

    broadcaster_token = broadcaster_social.get_access_token(load_strategy())
    broadcaster_id = broadcaster_social.uid

    subscriber_ids = []
    paging = True
    cursor = None
    while paging:
        data, cursor = get_subscriber_ids(broadcaster_token, broadcaster_id, cursor)
        if len(data) == 0:
            paging = False

        for subscriber in data:
            subscriber_ids.append(subscriber['user_id'])

    # Update our subscriptions
    Subscription.objects.filter(
        broadcaster=broadcaster,
        user__social_auth__provider='twitch',
        user__social_auth__uid__in=subscriber_ids
    ).update(last_verified=now())


def get_subscriber_ids(broadcaster_token, broadcaster_id, after=None):
    params = {
        'broadcaster_id': broadcaster_id,
    }

    # Do we have a cursor
    if after is not None:
        params['after'] = after

    resp = requests.get('https://api.twitch.tv/helix/subscriptions',
                        headers={'Authorization': f'Bearer {broadcaster_token}'},
                        params=params)

    if not resp.ok:
        raise ValueError('Error updating subscription information for whitelist {}'.format(broadcaster_id))

    json = resp.json()

    return json['data'], json['pagination']['cursor']
