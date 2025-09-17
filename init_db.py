#!/usr/bin/env python
"""
Railway 배포시 데이터베이스 초기화 스크립트
"""
import os
import sys
import django
from pathlib import Path

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oxvote.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.core.management.commands.migrate import Command as MigrateCommand

def reset_database():
    """데이터베이스를 완전히 초기화합니다"""
    try:
        import shutil
        
        # SQLite 파일 삭제
        db_path = Path('db.sqlite3')
        if db_path.exists():
            db_path.unlink()
            print("✅ 기존 데이터베이스 삭제 완료")
        
        # 마이그레이션 디렉토리 완전 삭제 후 재생성
        migrations_dir = Path('voting/migrations')
        if migrations_dir.exists():
            shutil.rmtree(migrations_dir)
            print("✅ 마이그레이션 디렉토리 완전 삭제")
        
        # 마이그레이션 디렉토리 재생성
        migrations_dir.mkdir(exist_ok=True)
        (migrations_dir / '__init__.py').touch()
        print("✅ 마이그레이션 디렉토리 재생성")
        
        # Django 테이블도 완전 삭제
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS voting_vote")
            cursor.execute("DROP TABLE IF EXISTS voting_question")
            print("✅ 기존 테이블 삭제 완료")
        except:
            pass
        
        # 새 마이그레이션 생성
        execute_from_command_line(['manage.py', 'makemigrations', 'voting'])
        print("✅ 새 마이그레이션 생성 완료")
        
        # 마이그레이션 적용
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ 마이그레이션 적용 완료")
        
        print("🎉 데이터베이스 초기화 성공!")
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        print("강제로 계속 진행...")
        return True  # 오류가 있어도 서버는 시작하도록

if __name__ == '__main__':
    reset_database()
