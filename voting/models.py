from django.db import models
import uuid

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(verbose_name="질문")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    show_results = models.BooleanField(default=False)  # 결과 보이기/숨기기
    
    def __str__(self):
        return self.text[:50]
    
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
    ip_address = models.GenericIPAddressField(default='127.0.0.1')  # 임시로 추가
    client_fingerprint = models.CharField(max_length=32, default='unknown')  # MD5 해시 (32자)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['question', 'ip_address']  # 임시로 기존 설정 유지
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.choice}"
