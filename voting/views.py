from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
import json
import qrcode
import re
from io import BytesIO
import base64
import hashlib
from .models import Question, Vote, ShortAnswerResponse

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

def get_question_by_code(simple_code, require_active=True):
    """간단한 코드로 질문을 찾습니다"""
    if not re.match(r'^\d{4}$', simple_code):
        return None
    
    try:
        if require_active:
            return Question.objects.get(simple_code=simple_code, is_active=True)
        else:
            return Question.objects.get(simple_code=simple_code)
    except Question.DoesNotExist:
        return None

def update_session_activity(request, question):
    """세션 활동 업데이트"""
    if not request.session.session_key:
        request.session.create()
    
    # 질문 생성자의 세션이라면 활동 시간 업데이트
    if question.creator_session == request.session.session_key:
        question.update_activity()

def home(request):
    """메인 페이지 - 질문 입력"""
    if request.method == 'POST':
        question_text = request.POST.get('question', '').strip()
        question_type = request.POST.get('question_type', 'OX')
        
        if question_text:
            # 세션 생성
            if not request.session.session_key:
                request.session.create()
            
            question = Question.objects.create(
                text=question_text,
                question_type=question_type,
                creator_session=request.session.session_key
            )
            
            # 질문 타입에 따라 다른 페이지로 리다이렉트
            if question_type == 'SHORT_ANSWER':
                return redirect('short_answer_qr_page', question_id=question.id)
            else:
                return redirect('qr_page', question_id=question.id)
        else:
            messages.error(request, '질문을 입력해주세요.')
    
    return render(request, 'voting/home.html')

def qr_page(request, question_id):
    """QR 코드 페이지 - 실시간 결과 표시"""
    question = get_object_or_404(Question, id=question_id)
    
    # 비활성 투표 체크
    if not question.is_active:
        return render(request, 'voting/inactive_vote.html', {'question': question})
    
    # 세션 활동 업데이트
    update_session_activity(request, question)
    
    # QR 코드 생성 (간단한 코드 사용)
    vote_url = request.build_absolute_uri(f'/{question.simple_code}/')
    simple_url = f"{request.get_host()}/{question.simple_code}"
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
        'simple_url': simple_url,
    }
    
    return render(request, 'voting/qr_page.html', context)

def vote_page(request, question_id):
    """투표 페이지"""
    question = get_object_or_404(Question, id=question_id)
    
    # 비활성 투표 체크
    if not question.is_active:
        return render(request, 'voting/inactive_vote.html', {'question': question})
    
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

# --- 간단한 코드 기반 뷰들 ---

def vote_by_code(request, simple_code):
    """간단한 코드로 투표 페이지 접근"""
    # 먼저 질문이 존재하는지 확인 (활성/비활성 상관없이)
    question = get_question_by_code(simple_code, require_active=False)
    
    if question is None:
        # 존재하지 않는 코드
        return render(request, 'voting/vote_not_found.html', {'searched_code': simple_code})
    
    if not question.is_active:
        # 비활성 투표
        return render(request, 'voting/inactive_vote.html', {'question': question})
    
    # 단답형이면 단답형 페이지로 리다이렉트
    if question.question_type == 'SHORT_ANSWER':
        return short_answer_vote_by_code(request, simple_code)
    
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
            return redirect('vote_result_by_code', simple_code=simple_code)
    
    context = {
        'question': question,
        'already_voted': already_voted,
    }
    
    return render(request, 'voting/vote_page.html', context)

def qr_page_by_code(request, simple_code):
    """간단한 코드로 QR 페이지 접근"""
    # 먼저 질문이 존재하는지 확인 (활성/비활성 상관없이)
    question = get_question_by_code(simple_code, require_active=False)
    
    if question is None:
        # 존재하지 않는 코드
        return render(request, 'voting/vote_not_found.html', {'searched_code': simple_code})
    
    if not question.is_active:
        # 비활성 투표
        return render(request, 'voting/inactive_vote.html', {'question': question})
    
    # 세션 활동 업데이트
    update_session_activity(request, question)
    
    # QR 코드 생성 (간단한 코드 사용)
    vote_url = request.build_absolute_uri(f'/{question.simple_code}/')
    simple_url = f"{request.get_host()}/{question.simple_code}"
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
        'simple_url': simple_url,
    }
    
    return render(request, 'voting/qr_page.html', context)

def vote_result_by_code(request, simple_code):
    """간단한 코드로 결과 페이지 접근"""
    # 먼저 질문이 존재하는지 확인 (활성/비활성 상관없이)
    question = get_question_by_code(simple_code, require_active=False)
    
    if question is None:
        # 존재하지 않는 코드
        return render(request, 'voting/vote_not_found.html', {'searched_code': simple_code})
    
    if not question.is_active:
        # 비활성 투표
        return render(request, 'voting/inactive_vote.html', {'question': question})
    
    context = {
        'question': question,
    }
    
    return render(request, 'voting/vote_result.html', context)

@csrf_exempt
@require_POST
def toggle_results_by_code(request, simple_code):
    """간단한 코드로 결과 보이기/숨기기 토글"""
    question = get_question_by_code(simple_code, require_active=False)
    
    if question is None:
        return JsonResponse({'error': 'Vote not found'}, status=404)
    
    if not question.is_active:
        return JsonResponse({'error': 'Voting is inactive'}, status=410)
    
    # 세션 활동 업데이트
    update_session_activity(request, question)
    
    question.show_results = not question.show_results
    question.save()
    
    return JsonResponse({
        'show_results': question.show_results,
        'o_percentage': question.o_percentage,
        'x_percentage': question.x_percentage,
        'total_votes': question.total_votes,
    })

def get_vote_stats_by_code(request, simple_code):
    """간단한 코드로 실시간 투표 통계 API"""
    question = get_question_by_code(simple_code, require_active=False)
    
    if question is None:
        return JsonResponse({'error': 'Vote not found'}, status=404)
    
    if not question.is_active:
        return JsonResponse({'error': 'Voting is inactive'}, status=410)
    
    return JsonResponse({
        'show_results': question.show_results,
        'o_percentage': question.o_percentage,
        'x_percentage': question.x_percentage,
        'total_votes': question.total_votes,
        'o_votes': question.o_votes,
        'x_votes': question.x_votes,
    })

@csrf_exempt
@require_POST
def end_vote(request, question_id):
    """투표 종료"""
    question = get_object_or_404(Question, id=question_id)
    
    # 세션 활동 업데이트
    update_session_activity(request, question)
    
    # 투표 비활성화
    question.deactivate()
    
    return JsonResponse({'success': True, 'message': 'Vote ended successfully'})

@csrf_exempt
@require_POST
def end_vote_by_code(request, simple_code):
    """간단한 코드로 투표 종료"""
    question = get_question_by_code(simple_code, require_active=False)
    
    if question is None:
        return JsonResponse({'error': 'Vote not found'}, status=404)
    
    if not question.is_active:
        return JsonResponse({'error': 'Vote already inactive'}, status=410)
    
    # 세션 활동 업데이트
    update_session_activity(request, question)
    
    # 투표 비활성화
    question.deactivate()
    
    return JsonResponse({'success': True, 'message': 'Vote ended successfully'})

# --- 정적 페이지 ---

def privacy(request):
    """개인정보처리방침 페이지"""
    return render(request, 'voting/privacy.html')

def ads_txt(request):
    """ads.txt 파일 서빙"""
    content = "google.com, pub-8902099051011521, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type='text/plain')

# --- 단답형 투표 관련 뷰들 ---

def short_answer_qr_page(request, question_id):
    """단답형 QR 코드 페이지 - 실시간 워드클라우드 표시"""
    question = get_object_or_404(Question, id=question_id)
    
    # 비활성 투표 체크
    if not question.is_active:
        return render(request, 'voting/inactive_vote.html', {'question': question})
    
    # 세션 활동 업데이트
    update_session_activity(request, question)
    
    # QR 코드 생성 (간단한 코드 사용)
    vote_url = request.build_absolute_uri(f'/{question.simple_code}/')
    simple_url = f"{request.get_host()}/{question.simple_code}"
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
        'simple_url': simple_url,
    }
    
    return render(request, 'voting/short_answer_qr_page.html', context)

def short_answer_vote_page(request, question_id):
    """단답형 투표 페이지"""
    question = get_object_or_404(Question, id=question_id)
    
    # 비활성 투표 체크
    if not question.is_active:
        return render(request, 'voting/inactive_vote.html', {'question': question})
    
    client_fingerprint = get_client_fingerprint(request)
    
    if request.method == 'POST':
        response_text = request.POST.get('response', '').strip()
        if response_text and len(response_text) <= 200:
            ShortAnswerResponse.objects.create(
                question=question,
                response_text=response_text,
                client_fingerprint=client_fingerprint
            )
            messages.success(request, '응답이 제출되었습니다!')
            # 같은 페이지로 리다이렉트하여 추가 응답 가능
            return redirect('short_answer_vote_page', question_id=question_id)
    
    # 이 사용자가 제출한 응답 개수
    user_response_count = ShortAnswerResponse.objects.filter(
        question=question,
        client_fingerprint=client_fingerprint
    ).count()
    
    context = {
        'question': question,
        'user_response_count': user_response_count,
    }
    
    return render(request, 'voting/short_answer_vote_page.html', context)

def get_short_answer_stats(request, question_id):
    """단답형 실시간 통계 API"""
    question = get_object_or_404(Question, id=question_id)
    
    # 전체 응답 개수
    total_responses = ShortAnswerResponse.objects.filter(question=question).count()
    
    # 고유 참여자 수 (중복 제거)
    unique_participants = ShortAnswerResponse.objects.filter(
        question=question
    ).values('client_fingerprint').distinct().count()
    
    # 워드 클라우드용 데이터 (각 응답의 빈도수)
    word_data = ShortAnswerResponse.objects.filter(
        question=question
    ).values('response_text').annotate(
        count=Count('response_text')
    ).order_by('-count')[:100]  # 상위 100개만
    
    return JsonResponse({
        'total_responses': total_responses,
        'unique_participants': unique_participants,
        'word_data': list(word_data),
    })

def short_answer_vote_by_code(request, simple_code):
    """간단한 코드로 단답형 투표 페이지 접근"""
    question = get_question_by_code(simple_code, require_active=False)
    
    if question is None:
        return render(request, 'voting/vote_not_found.html', {'searched_code': simple_code})
    
    if not question.is_active:
        return render(request, 'voting/inactive_vote.html', {'question': question})
    
    # 단답형이 아니면 일반 투표 페이지로
    if question.question_type != 'SHORT_ANSWER':
        return vote_by_code(request, simple_code)
    
    client_fingerprint = get_client_fingerprint(request)
    
    if request.method == 'POST':
        response_text = request.POST.get('response', '').strip()
        if response_text and len(response_text) <= 200:
            ShortAnswerResponse.objects.create(
                question=question,
                response_text=response_text,
                client_fingerprint=client_fingerprint
            )
            messages.success(request, '응답이 제출되었습니다!')
            return redirect('short_answer_vote_by_code', simple_code=simple_code)
    
    user_response_count = ShortAnswerResponse.objects.filter(
        question=question,
        client_fingerprint=client_fingerprint
    ).count()
    
    context = {
        'question': question,
        'user_response_count': user_response_count,
    }
    
    return render(request, 'voting/short_answer_vote_page.html', context)

def short_answer_qr_page_by_code(request, simple_code):
    """간단한 코드로 단답형 QR 페이지 접근"""
    question = get_question_by_code(simple_code, require_active=False)
    
    if question is None:
        return render(request, 'voting/vote_not_found.html', {'searched_code': simple_code})
    
    if not question.is_active:
        return render(request, 'voting/inactive_vote.html', {'question': question})
    
    # 세션 활동 업데이트
    update_session_activity(request, question)
    
    # QR 코드 생성
    vote_url = request.build_absolute_uri(f'/{question.simple_code}/')
    simple_url = f"{request.get_host()}/{question.simple_code}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(vote_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    qr_code_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'question': question,
        'qr_code': qr_code_b64,
        'vote_url': vote_url,
        'simple_url': simple_url,
    }
    
    return render(request, 'voting/short_answer_qr_page.html', context)

def get_short_answer_stats_by_code(request, simple_code):
    """간단한 코드로 단답형 실시간 통계 API"""
    question = get_question_by_code(simple_code, require_active=False)
    
    if question is None:
        return JsonResponse({'error': 'Vote not found'}, status=404)
    
    if not question.is_active:
        return JsonResponse({'error': 'Voting is inactive'}, status=410)
    
    total_responses = ShortAnswerResponse.objects.filter(question=question).count()
    unique_participants = ShortAnswerResponse.objects.filter(
        question=question
    ).values('client_fingerprint').distinct().count()
    
    word_data = ShortAnswerResponse.objects.filter(
        question=question
    ).values('response_text').annotate(
        count=Count('response_text')
    ).order_by('-count')[:100]
    
    return JsonResponse({
        'total_responses': total_responses,
        'unique_participants': unique_participants,
        'word_data': list(word_data),
    })
