"""
Atomic Note Agent 테스트 스크립트
Google Gemini API 사용
"""

import os
import sys
import json
from pathlib import Path

# src 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from atomic_note_agent import AtomicNoteAgent
from obsidian_loader import ObsidianVaultLoader

# .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# API 키 확인
if not os.environ.get("GEMINI_API_KEY"):
    print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
    print("\n다음 중 하나를 선택하세요:")
    print("1. .env 파일에 GEMINI_API_KEY=your-api-key 추가")
    print("2. 환경변수로 설정: export GEMINI_API_KEY='your-api-key'")
    print("\nAPI 키는 https://makersuite.google.com/app/apikey 에서 발급받을 수 있습니다.")
    exit(1)

# Agent 초기화 - Gemini 2.5 Flash 사용
agent = AtomicNoteAgent(model="gemini-2.5-flash")

print(f"\n🤖 Atomic Note Agent")
print("=" * 60)
print(f"🔧 모델: {agent.model_name}")
print(f"⚡ 특징: Gemini 2.5 Flash - 최신 모델, 빠르고 정확함")
print("=" * 60)

# Vault 로드
VAULT_PATH = "/Users/inyoungpark/Documents/Obsidian Vault"
loader = ObsidianVaultLoader(VAULT_PATH)
notes = loader.load_vault()

print(f"\n📚 로드된 노트: {len(notes)}개")
print("=" * 60)

# 메인 메뉴
print("\n📋 처리 옵션:")
print("1. 단일 노트 테스트 (자동 선택 - 적당한 길이)")
print("2. 특정 노트 선택 (목록에서 선택)")
print("3. 전체 Vault 분해 (모든 노트)")
print("4. 종료")

choice = input("\n선택 (1-4): ").strip()

if choice == "1":
    # 자동으로 적당한 길이의 노트 찾기
    test_note = None
    for note in notes:
        content_length = len(note.content.strip())
        if 100 < content_length < 3000:  # 적당한 길이
            test_note = note
            break
    
    if not test_note:
        test_note = notes[0]
    
    print(f"\n🔍 선택된 노트: {test_note.title}")
    print(f"📏 길이: {len(test_note.content)} 글자")
    print("\n처리 중...")
    
    result = agent.decompose_note(test_note)
    
    print("\n✅ 결과:")
    print("=" * 60)
    print(f"생성된 Atomic Notes: {len(result.get('atomic_notes', []))}개")
    
    # 첫 번째 Atomic Note 출력
    if result.get('atomic_notes'):
        first = result['atomic_notes'][0]
        print(f"\n📝 예시: {first['title']}")
        print(f"내용: {first['content'][:200]}...")
        print(f"엔티티: {first.get('extracted_entities', [])[:5]}")
        print(f"관계: {len(first.get('relationships', []))}개")
    
    # JSON 저장
    output_file = f"./atomic_notes/{test_note.title.replace('/', '_')}_atomic.json"
    os.makedirs("./atomic_notes", exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n💾 저장됨: {output_file}")
    
    # 마크다운 저장
    agent.save_as_markdown(result)
    print(f"📝 마크다운도 저장됨: ./atomic_notes_md/")

elif choice == "2":
    # 노트 목록 표시 및 선택
    print("\n📄 사용 가능한 노트:")
    print("=" * 60)
    
    # 노트를 크기순으로 정렬
    sorted_notes = sorted(notes, key=lambda n: len(n.content.strip()), reverse=True)
    
    for i, note in enumerate(sorted_notes, 1):
        content_len = len(note.content.strip())
        print(f"{i:3d}. {note.title:50s} ({content_len:6d} 글자)")
    
    print("=" * 60)
    print("\n선택 방법:")
    print("  - 단일 노트: 번호 입력 (예: 3)")
    print("  - 여러 노트: 쉼표로 구분 (예: 1,3,5)")
    print("  - 범위 선택: 하이픈 사용 (예: 1-5)")
    print("  - 혼합 가능: (예: 1,3-5,7)")
    
    selection = input("\n선택: ").strip()
    
    if not selection:
        print("취소됨")
        exit(0)
    
    # 선택 파싱
    selected_indices = set()
    
    for part in selection.split(','):
        part = part.strip()
        if '-' in part:
            # 범위
            try:
                start, end = map(int, part.split('-'))
                selected_indices.update(range(start, end + 1))
            except:
                print(f"⚠️  잘못된 범위: {part}")
        else:
            # 단일 번호
            try:
                selected_indices.add(int(part))
            except:
                print(f"⚠️  잘못된 번호: {part}")
    
    # 선택된 노트 처리
    selected_notes = [sorted_notes[i-1] for i in selected_indices if 1 <= i <= len(sorted_notes)]
    
    if not selected_notes:
        print("❌ 선택된 노트가 없습니다.")
        exit(1)
    
    print(f"\n✅ 선택된 노트: {len(selected_notes)}개")
    print("=" * 60)
    
    for i, note in enumerate(selected_notes, 1):
        print(f"\n[{i}/{len(selected_notes)}] 처리 중: {note.title}")
        
        # 빈 노트 스킵
        if len(note.content.strip()) < 50:
            print("  ⏭️  너무 짧은 노트 - 스킵")
            continue
        
        # JSON 파일 경로
        safe_title = note.title.replace('/', '_').replace('\\', '_')
        output_file = f"./atomic_notes/{safe_title}_atomic.json"
        os.makedirs("./atomic_notes", exist_ok=True)
        
        # 이미 JSON 파일이 존재하는지 확인
        if os.path.exists(output_file):
            print(f"  ♻️  이미 처리됨 - JSON 로드 중...")
            with open(output_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            print(f"  ✅ 로드 완료: {len(result.get('atomic_notes', []))}개 Atomic Notes")
        else:
            # 새로 분해
            print(f"  🔄 Atomic Notes 생성 중...")
            result = agent.decompose_note(note)
            
            # JSON 저장
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ 완료: {len(result.get('atomic_notes', []))}개 생성")
            print(f"  💾 저장: {output_file}")
        
        # 마크다운 저장 (항상 수행)
        print(f"  📝 마크다운 생성 중...")
        agent.save_as_markdown(result)
    
    print("\n✅ 모든 선택된 노트 처리 완료!")

elif choice == "3":
    # 전체 Vault 분해
    print("\n⚠️  경고: 전체 Vault 분해는 시간과 비용이 많이 듭니다!")
    print(f"   총 {len(notes)}개의 노트를 처리합니다.")
    
    # 이미 처리된 파일 확인
    existing_files = []
    new_files = []
    if os.path.exists("./atomic_notes"):
        existing_files = [f for f in os.listdir("./atomic_notes") if f.endswith("_atomic.json")]
    
    if existing_files:
        print(f"\n💡 이미 {len(existing_files)}개의 JSON 파일이 존재합니다.")
        print("   옵션:")
        print("   1. 기존 파일 유지하고 새 노트만 처리")
        print("   2. 모든 파일 재생성 (API 비용 발생)")
        print("   3. 기존 파일로 마크다운만 재생성")
        sub_choice = input("\n선택 (1-3): ").strip()
        
        if sub_choice == "3":
            # 마크다운만 재생성
            print("\n📝 기존 JSON에서 마크다운 생성 중...")
            for json_file in existing_files:
                json_path = os.path.join("./atomic_notes", json_file)
                with open(json_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                agent.save_as_markdown(result)
                print(f"  ✅ {json_file} → 마크다운 생성")
            print("\n✅ 마크다운 재생성 완료!")
            exit(0)
        elif sub_choice == "2":
            skip_existing = False
        else:
            skip_existing = True
    else:
        skip_existing = False
    
    confirm = input("\n계속하시겠습니까? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        results = agent.decompose_vault(VAULT_PATH, skip_existing=skip_existing)
        
        # 마크다운으로도 저장
        print("\n📝 마크다운 형식으로 저장 중...")
        for result in results:
            agent.save_as_markdown(result)
        
        print("\n✅ 전체 Vault 처리 완료!")
        print(f"📊 총 {len(results)}개 파일 처리됨")
    else:
        print("취소됨")

else:
    print("종료")
