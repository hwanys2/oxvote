import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Question, Vote
import logging

logger = logging.getLogger(__name__)

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
        
        # Send initial stats when connected
        stats = await self.get_vote_stats()
        await self.send(text_data=json.dumps({
            'type': 'vote_stats',
            'data': stats
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')

            if message_type == 'get_stats':
                # Send current stats
                stats = await self.get_vote_stats()
                await self.send(text_data=json.dumps({
                    'type': 'vote_stats',
                    'data': stats
                }))
            elif message_type == 'toggle_results':
                # Toggle results visibility
                result = await self.toggle_question_results()
                if result:
                    # Broadcast to all connected clients
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'vote_stats',
                            'data': result
                        }
                    )
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred'
            }))

    # Receive message from room group
    async def vote_stats(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'vote_stats',
            'data': event['data']
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
            return {
                'show_results': False,
                'o_percentage': 0,
                'x_percentage': 0,
                'total_votes': 0,
                'o_votes': 0,
                'x_votes': 0,
            }

    @database_sync_to_async
    def toggle_question_results(self):
        try:
            question = Question.objects.get(id=self.question_id)
            question.show_results = not question.show_results
            question.save()
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