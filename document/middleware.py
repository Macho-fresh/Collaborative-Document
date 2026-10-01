from accounts.models import User
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken

@database_sync_to_async
def get_user_from_token(token_string):
    print(token_string)
    try:
        access_token = AccessToken(token_string)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
    except Exception as e:
        print(f'This line failed because of {e}')
        user = AnonymousUser()
    return user

class JWTAuthMiddleWare:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        raw_token = scope['query_string'].decode("utf-8")
        token_dict = parse_qs(raw_token)
        token_list = token_dict.get('token')

        if token_list:
            token = token_list[0]
            user = await get_user_from_token(token)
        else:
            user = AnonymousUser()

        scope['user'] = user

        return await self.app(scope, receive, send)