from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Vote, Question
import logging

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()

def broadcast_vote_stats(question_id):
    """투표 통계를 WebSocket으로 브로드캐스트"""
    try:
        question = Question.objects.get(id=question_id)
        stats = {
            'show_results': question.show_results,
            'o_percentage': question.o_percentage,
            'x_percentage': question.x_percentage,
            'total_votes': question.total_votes,
            'o_votes': question.o_votes,
            'x_votes': question.x_votes,
        }
        
        room_group_name = f'vote_{question_id}'
        
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'vote_stats',
                    'data': stats
                }
            )
        else:
            logger.warning("Channel layer not available")
            
    except Question.DoesNotExist:
        logger.error(f"Question {question_id} not found")
    except Exception as e:
        logger.error(f"Error broadcasting vote stats: {e}")

@receiver(post_save, sender=Vote)
def vote_created_or_updated(sender, instance, created, **kwargs):
    """투표가 생성되거나 업데이트될 때 실시간 통계 업데이트"""
    if created:
        logger.info(f"New vote created for question {instance.question.id}")
    broadcast_vote_stats(instance.question.id)

@receiver(post_delete, sender=Vote)
def vote_deleted(sender, instance, **kwargs):
    """투표가 삭제될 때 실시간 통계 업데이트"""
    logger.info(f"Vote deleted for question {instance.question.id}")
    broadcast_vote_stats(instance.question.id)

@receiver(post_save, sender=Question)
def question_updated(sender, instance, created, **kwargs):
    """질문이 업데이트될 때 (특히 show_results 변경 시) 실시간 업데이트"""
    if not created:  # 질문이 수정된 경우에만
        logger.info(f"Question {instance.id} updated")
        broadcast_vote_stats(instance.id) 