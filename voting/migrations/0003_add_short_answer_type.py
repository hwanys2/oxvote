# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_add_simple_code_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_type',
            field=models.CharField(
                choices=[('OX', 'O/X 투표'), ('SHORT_ANSWER', '단답형')],
                default='OX',
                max_length=20,
                verbose_name='질문 유형'
            ),
        ),
        migrations.CreateModel(
            name='ShortAnswerResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_text', models.CharField(max_length=200, verbose_name='응답 내용')),
                ('client_fingerprint', models.CharField(default='unknown', max_length=32, verbose_name='클라이언트 식별자')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='short_answers', to='voting.question')),
            ],
        ),
        migrations.AddIndex(
            model_name='shortanswerresponse',
            index=models.Index(fields=['question', 'created_at'], name='voting_shor_questio_idx'),
        ),
    ]
