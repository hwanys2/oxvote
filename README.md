# O/X 투표 시스템

실시간으로 O/X 질문에 대한 투표를 받을 수 있는 Django 웹 애플리케이션입니다.

## 기능

- **질문 생성**: 메인 페이지에서 O/X 질문을 생성
- **QR 코드 생성**: 질문 생성 후 자동으로 QR 코드 생성
- **실시간 투표**: 학생들이 QR 코드를 스캔하여 O/X 투표
- **실시간 결과**: 투표 결과를 실시간으로 확인 (보이기/숨기기 가능)
- **중복 투표 방지**: IP 주소 기반으로 중복 투표 방지
- **반응형 디자인**: 모바일 친화적인 UI

## 기술 스택

- **Backend**: Django 5.2.6
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript
- **Real-time**: Django Channels (WebSocket)
- **QR Code**: qrcode library
- **Database**: SQLite (개발), PostgreSQL (배포)
- **Deployment**: Railway

## 로컬 실행

1. 가상환경 활성화:
```bash
conda activate goodmessage
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. 데이터베이스 마이그레이션:
```bash
python manage.py migrate
```

4. 정적 파일 수집:
```bash
python manage.py collectstatic
```

5. 서버 실행:
```bash
python manage.py runserver
```

## 사용법

1. 메인 페이지에서 O/X 질문을 입력
2. 생성된 QR 코드를 학생들에게 공유
3. 학생들이 QR 코드를 스캔하여 투표
4. 실시간으로 결과 확인 (보이기/숨기기 토글 가능)

## 배포

Railway에 배포하려면:

1. Railway 계정 생성 및 프로젝트 생성
2. GitHub 저장소 연결
3. 환경변수 설정:
   - `SECRET_KEY`: Django 시크릿 키
   - `DEBUG`: False (배포시)
4. 자동 배포 실행

## 프로젝트 구조

```
oxvote/
├── oxvote/              # Django 프로젝트 설정
├── voting/              # 투표 앱
│   ├── models.py        # 질문, 투표 모델
│   ├── views.py         # 뷰 함수들
│   ├── urls.py          # URL 패턴
│   ├── consumers.py     # WebSocket 컨슈머
│   ├── routing.py       # WebSocket 라우팅
│   └── templates/       # HTML 템플릿
├── static/              # 정적 파일
├── requirements.txt     # Python 의존성
├── Procfile            # Railway 배포 설정
└── README.md           # 프로젝트 설명
```
