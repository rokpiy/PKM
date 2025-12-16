"""
기존 JSON 파일에서 마크다운 재생성
Stage 1이 이미 완료된 경우 사용
"""

import os
import sys
import json
from pathlib import Path

# src 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from atomic_note_agent import AtomicNoteAgent

print("📝 기존 JSON → 마크다운 재생성")
print("=" * 60)

# Atomic Notes 디렉토리 확인
atomic_notes_dir = Path(__file__).parent.parent / "atomic_notes"

if not atomic_notes_dir.exists():
    print("❌ atomic_notes 폴더가 없습니다.")
    print("   먼저 Stage 1을 실행하세요.")
    exit(1)

# JSON 파일 찾기
json_files = list(atomic_notes_dir.glob("*_atomic.json"))

if not json_files:
    print("❌ JSON 파일이 없습니다.")
    exit(1)

print(f"✅ 발견된 JSON 파일: {len(json_files)}개")
print("=" * 60)

# Agent 초기화 (API 키 불필요)
agent = AtomicNoteAgent()

# 각 JSON 파일에서 마크다운 생성
success_count = 0
error_count = 0

for i, json_file in enumerate(json_files, 1):
    print(f"\n[{i}/{len(json_files)}] {json_file.name}")
    
    try:
        # JSON 로드
        with open(json_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        atomic_notes_count = len(result.get("atomic_notes", []))
        print(f"  ℹ️  Atomic Notes: {atomic_notes_count}개")
        
        # 마크다운 생성
        agent.save_as_markdown(result)
        
        print(f"  ✅ 마크다운 생성 완료")
        success_count += 1
        
    except Exception as e:
        print(f"  ❌ 에러: {e}")
        error_count += 1
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print(f"✅ 완료: {success_count}개 성공, {error_count}개 실패")
print(f"📂 출력: ./atomic_notes_md/")

