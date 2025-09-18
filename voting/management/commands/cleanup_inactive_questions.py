from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from voting.models import Question

class Command(BaseCommand):
    help = '비활성 질문들을 정리합니다 (30분 이상 활동이 없는 질문들)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=30,
            help='비활성화할 시간 기준 (분, 기본값: 30분)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제로 삭제하지 않고 대상만 표시'
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        dry_run = options['dry_run']
        
        # N분 이상 활동이 없는 활성 질문들 찾기
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        inactive_questions = Question.objects.filter(
            is_active=True,
            last_activity__lt=cutoff_time
        )
        
        count = inactive_questions.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'{minutes}분 이상 비활성 질문이 없습니다.')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] {count}개의 질문이 비활성화 대상입니다:')
            )
            for question in inactive_questions:
                self.stdout.write(
                    f'  - {question.simple_code}: {question.text[:50]}... '
                    f'(마지막 활동: {question.last_activity})'
                )
        else:
            # 실제로 비활성화
            updated = inactive_questions.update(is_active=False)
            self.stdout.write(
                self.style.SUCCESS(f'{updated}개의 질문을 비활성화했습니다.')
            )
            
            # 비활성화된 질문들의 간단한 코드 재사용 가능하도록 정리
            for question in inactive_questions:
                self.stdout.write(
                    f'  - {question.simple_code}: {question.text[:50]}... 비활성화됨'
                )
