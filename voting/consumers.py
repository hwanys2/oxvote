import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Question, Vote

class VoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.question_id = self.scope['url_route']['kwargs']['question_id']
        self.room_group_name = f'vote_{self.question_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'vote_update':
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'vote_update',
                    'message': text_data_json
                }
            )

    async def vote_update(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'vote_update',
            'data': message
        }))

    @database_sync_to_async
    def get_vote_stats(self):
        try:
            question = Question.objects.get(id=self.question_id)
            return {
                'show_results': question.show_results,
                'o_percentage': question.o_percentage,
                'x_percentage': question.x_percentage,
                'total_votes': question.total_votes,
                'o_votes': question.o_votes,
                'x_votes': question.x_votes,
            }
        except Question.DoesNotExist:
            return None
