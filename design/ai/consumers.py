from django.conf import settings

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from . import tasks

class TaskConsumer(AsyncJsonWebsocketConsumer):


    async def connect(self):
        # allow all connections for the time being
        print("got a connection request")
        await self.accept()

    async def receive_json(self, content):
        task = content.get("task", None)
        data = content.get("data", None)
        print("got a task request: ", task)
        getattr(tasks, task).delay(self.channel_name, data)

        print("Task: ", task)
        print("Data: ", data)
        print('channel: ', self.channel_name)

    async def task_return(self, event):
        results = event.get("results", None)
        print("Got some results: ", results)
        await self.send_json(results)
