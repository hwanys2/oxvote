from django.db import models
from django.utils import timezone
import uuid
import random
import string

def generate_simple_code():
    """중복되지 않는 4자리 코드 생성"""
    while True:
        code = ''.join(random.choices(string.digits, k=4))
        if not Question.objects.filter(simple_code=code, is_active=True).exists():
            return code

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(verbose_name="질문")
    simple_code = models.CharField(max_length=4, unique=False, blank=True, verbose_name="간단 코드")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    show_results = models.BooleanField(default=False)  # 결과 보이기/숨기기
    creator_session = models.CharField(max_length=40, blank=True, verbose_name="생성자 세션")  # 세션 관리용
    last_activity = models.DateTimeField(default=timezone.now, verbose_name="마지막 활동")  # 활성 상태 추적
    
    def save(self, *args, **kwargs):
        if not self.simple_code:
            self.simple_code = generate_simple_code()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.simple_code} - {self.text[:50]}"
    
    def update_activity(self):
        """활동 시간 업데이트"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def deactivate(self):
        """질문 비활성화"""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    @property
    def total_votes(self):
        return self.votes.count()
    
    @property
    def o_votes(self):
        return self.votes.filter(choice='O').count()
    
    @property
    def x_votes(self):
        return self.votes.filter(choice='X').count()
    
    @property
    def o_percentage(self):
        if self.total_votes == 0:
            return 0
        return round((self.o_votes / self.total_votes) * 100, 1)
    
    @property
    def x_percentage(self):
        if self.total_votes == 0:
            return 0
        return round((self.x_votes / self.total_votes) * 100, 1)

class Vote(models.Model):
    CHOICES = [
        ('O', 'O'),
        ('X', 'X'),
    ]
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')
    choice = models.CharField(max_length=1, choices=CHOICES)
    client_fingerprint = models.CharField(max_length=32, default='unknown')  # MD5 해시 (32자)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['question', 'client_fingerprint']  # 같은 기기에서 중복 투표 방지
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.choice}"
