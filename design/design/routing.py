# design/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from ai.consumers import TaskConsumer
from api.consumers import APIConsumer
from bot.consumers import BotConsumer
from chat.consumers import ChatConsumer, OrganizationConsumer
from twin.consumers import TwinConsumer

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter([
            url(r'ws/api/$', APIConsumer),
            url(r'ws/bot/$', BotConsumer),
            url(r'ws/chat/$', ChatConsumer),
            url(r'ws/org/$', OrganizationConsumer),            
            url(r'ws/tasks/$', TaskConsumer),
            url(r'ws/twin/$', TwinConsumer),
        ])
    ),
})
