from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
import qrcode
from io import BytesIO
import base64
import hashlib
from .models import Question, Vote

def get_client_fingerprint(request):
    """클라이언트 고유 식별자를 생성합니다 (IP + User-Agent 조합)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # IP + User-Agent를 조합하여 고유한 해시 생성
    fingerprint_string = f"{ip}:{user_agent}"
    fingerprint = hashlib.md5(fingerprint_string.encode()).hexdigest()
    
    return fingerprint

def home(request):
    """메인 페이지 - 질문 입력"""
    if request.method == 'POST':
        question_text = request.POST.get('question', '').strip()
        if question_text:
            question = Question.objects.create(text=question_text)
            return redirect('qr_page', question_id=question.id)
        else:
            messages.error(request, '질문을 입력해주세요.')
    
    return render(request, 'voting/home.html')

def qr_page(request, question_id):
    """QR 코드 페이지 - 실시간 결과 표시"""
    question = get_object_or_404(Question, id=question_id)
    
    # QR 코드 생성
    vote_url = request.build_absolute_uri(f'/vote/{question_id}/')
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(vote_url)
    qr.make(fit=True)
    
    # QR 코드를 이미지로 변환
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Base64로 인코딩
    qr_code_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'question': question,
        'qr_code': qr_code_b64,
        'vote_url': vote_url,
    }
    
    return render(request, 'voting/qr_page.html', context)

def vote_page(request, question_id):
    """투표 페이지"""
    question = get_object_or_404(Question, id=question_id)
    client_fingerprint = get_client_fingerprint(request)
    
    # 이미 투표했는지 확인
    already_voted = Vote.objects.filter(question=question, client_fingerprint=client_fingerprint).exists()
    
    if request.method == 'POST' and not already_voted:
        choice = request.POST.get('choice')
        if choice in ['O', 'X']:
            Vote.objects.create(
                question=question,
                choice=choice,
                client_fingerprint=client_fingerprint
            )
            return redirect('vote_result', question_id=question_id)
    
    context = {
        'question': question,
        'already_voted': already_voted,
    }
    
    return render(request, 'voting/vote_page.html', context)

def vote_result(request, question_id):
    """투표 결과 페이지"""
    question = get_object_or_404(Question, id=question_id)
    
    context = {
        'question': question,
    }
    
    return render(request, 'voting/vote_result.html', context)

@csrf_exempt
@require_POST
def toggle_results(request, question_id):
    """결과 보이기/숨기기 토글"""
    question = get_object_or_404(Question, id=question_id)
    question.show_results = not question.show_results
    question.save()
    
    return JsonResponse({
        'show_results': question.show_results,
        'o_percentage': question.o_percentage,
        'x_percentage': question.x_percentage,
        'total_votes': question.total_votes,
    })

def get_vote_stats(request, question_id):
    """실시간 투표 통계 API"""
    question = get_object_or_404(Question, id=question_id)
    
    return JsonResponse({
        'show_results': question.show_results,
        'o_percentage': question.o_percentage,
        'x_percentage': question.x_percentage,
        'total_votes': question.total_votes,
        'o_votes': question.o_votes,
        'x_votes': question.x_votes,
    })

# --- 정적 페이지 ---

def privacy(request):
    """개인정보처리방침 페이지"""
    return render(request, 'voting/privacy.html')
