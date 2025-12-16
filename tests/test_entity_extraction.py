"""
Entity Extraction 테스트 스크립트
Stage 2: Entity & Relationship Extraction 테스트
"""

import os
import sys
import json
from pathlib import Path

# src 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from entity_extraction_simple import SimpleEntityExtractor

# .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print("🔬 Entity & Relationship Extraction 테스트")
print("=" * 60)

# Extractor 초기화
extractor = SimpleEntityExtractor()

# 기존 Atomic Notes JSON 파일 로드 (Stage 1 결과)
atomic_notes_dir = Path(__file__).parent.parent / "atomic_notes"

if not atomic_notes_dir.exists():
    print("❌ atomic_notes 폴더가 없습니다.")
    print("   먼저 Stage 1 (test_atomic_agent.py)를 실행하세요.")
    exit(1)

json_files = list(atomic_notes_dir.glob("*_atomic.json"))

if not json_files:
    print("❌ Atomic Notes JSON 파일이 없습니다.")
    print("   먼저 Stage 1을 실행하세요.")
    exit(1)

print(f"\n📂 발견된 Atomic Notes 파일: {len(json_files)}개")
print("=" * 60)

# 각 파일 처리
total_entities = 0
total_relationships = 0

for json_file in json_files:
    print(f"\n📄 처리 중: {json_file.name}")
    
    # JSON 로드
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    atomic_notes = data.get("atomic_notes", [])
    
    if not atomic_notes:
        print("  ⏭️  Atomic Notes가 없습니다 - 스킵")
        continue
    
    # 각 Atomic Note 개선
    for i, note in enumerate(atomic_notes, 1):
        print(f"\n  [{i}/{len(atomic_notes)}] {note.get('title', 'Untitled')}")
        
        # Entity 개선
        enhanced_note = extractor.enhance_gemini_entities(note)
        
        # 통계
        entities = enhanced_note.get("entities_enhanced", [])
        relationships = enhanced_note.get("relationships_enhanced", [])
        
        print(f"    ✅ 엔티티: {len(entities)}개")
        print(f"    🔗 관계: {len(relationships)}개")
        
        total_entities += len(entities)
        total_relationships += len(relationships)
        
        # 샘플 출력
        if entities:
            print(f"    📝 엔티티 샘플: {entities[:5]}")
        
        if relationships:
            print(f"    📝 관계 샘플:")
            for rel in relationships[:3]:
                print(f"       {rel['from']} --[{rel['type']}]--> {rel['to']}")
    
    # 개선된 결과 저장
    output_file = json_file.parent / f"{json_file.stem}_enhanced.json"
    data["atomic_notes"] = atomic_notes
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n  💾 저장: {output_file.name}")

# 전체 통계
print("\n" + "=" * 60)
print("📊 전체 통계")
print("=" * 60)
print(f"총 엔티티: {total_entities}개")
print(f"총 관계: {total_relationships}개")
print(f"처리된 파일: {len(json_files)}개")
print("\n✅ Stage 2 완료!")

