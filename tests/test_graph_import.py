"""
Graph DB Import 테스트 스크립트
Stage 3: Atomic Notes → Neo4j Graph DB
"""

import os
import sys
import json
from pathlib import Path

# src 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from graph_db import GraphDBManager

# .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print("🚀 Stage 3: Atomic Notes → Neo4j Graph DB")
print("=" * 60)

# Neo4j 설정 (환경변수 또는 기본값)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

print(f"🔧 Neo4j 설정:")
print(f"   URI: {NEO4J_URI}")
print(f"   User: {NEO4J_USER}")
print("=" * 60)

# Enhanced JSON 파일 로드 (Stage 2 결과)
atomic_notes_dir = Path(__file__).parent.parent / "atomic_notes"

if not atomic_notes_dir.exists():
    print("❌ atomic_notes 폴더가 없습니다.")
    print("   먼저 Stage 1과 2를 실행하세요.")
    exit(1)

# Enhanced 파일 우선, 없으면 일반 파일 사용
enhanced_files = list(atomic_notes_dir.glob("*_enhanced.json"))
regular_files = list(atomic_notes_dir.glob("*_atomic.json"))

json_files = enhanced_files if enhanced_files else regular_files

if not json_files:
    print("❌ Atomic Notes JSON 파일이 없습니다.")
    print("   먼저 Stage 1을 실행하세요.")
    exit(1)

print(f"\n📂 발견된 파일: {len(json_files)}개")
if enhanced_files:
    print("   (Enhanced 파일 사용 - Stage 2 완료)")
else:
    print("   (일반 파일 사용 - Stage 2 미완료)")
print("=" * 60)

try:
    # Graph DB 연결
    graph = GraphDBManager(NEO4J_URI, (NEO4J_USER, NEO4J_PASSWORD))
    
    # 스키마 생성
    graph.create_schema()
    
    # 사용자 선택
    print("\n처리 옵션:")
    print("1. 기존 데이터 유지하고 추가")
    print("2. 모든 데이터 삭제 후 새로 시작")
    print("3. 종료")
    
    choice = input("\n선택 (1-3): ").strip()
    
    if choice == "2":
        confirm = input("⚠️  정말 모든 데이터를 삭제하시겠습니까? (yes/no): ").strip().lower()
        if confirm == "yes":
            graph.clear_all()
        else:
            print("취소됨")
            exit(0)
    elif choice == "3":
        print("종료")
        exit(0)
    
    # 통계
    total_notes = 0
    total_entities = 0
    total_relationships = 0
    
    # 각 파일 처리
    for json_file in json_files:
        print(f"\n📄 처리 중: {json_file.name}")
        
        # JSON 로드
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        atomic_notes = data.get("atomic_notes", [])
        source_note = data.get("source_note", {})
        
        if not atomic_notes:
            print("  ⏭️  Atomic Notes가 없습니다 - 스킵")
            continue
        
        # 각 Atomic Note 처리
        for i, note in enumerate(atomic_notes, 1):
            note_id = note.get("id", f"note_{i}")
            note_title = note.get("title", "Untitled")
            
            print(f"\n  [{i}/{len(atomic_notes)}] {note_title}")
            
            # 1. Atomic Note 노드 생성
            note_data = {
                "id": note_id,
                "title": note_title,
                "content": note.get("content", ""),
                "detailed_content": note.get("detailed_content", ""),
                "domain": note.get("domain", "general"),
                "confidence": note.get("confidence", "medium"),
                "source_note": source_note.get("title", "")
            }
            
            graph.create_atomic_note_node(note_data)
            total_notes += 1
            
            # 2. Entity 노드 생성 및 연결
            # Enhanced 엔티티 우선 사용
            entities = note.get("entities_enhanced", note.get("extracted_entities", []))
            
            created_entities = set()
            for entity in entities:
                if isinstance(entity, dict):
                    entity_name = entity.get("text", "")
                    entity_data = {
                        "label": entity.get("label", "CONCEPT"),
                        "domain": note.get("domain", "general"),
                        "confidence": entity.get("confidence", 1.0)
                    }
                else:
                    entity_name = str(entity)
                    entity_data = {"domain": note.get("domain", "general")}
                
                if entity_name and entity_name not in created_entities:
                    graph.create_entity_node(entity_name, entity_data)
                    graph.link_note_to_entity(note_id, entity_name)
                    created_entities.add(entity_name)
                    total_entities += 1
            
            # 3. Entity 간 관계 생성
            # Enhanced 관계 우선 사용
            relationships = note.get("relationships_enhanced", note.get("relationships", []))
            
            for rel in relationships:
                from_entity = rel.get("from", "")
                to_entity = rel.get("to", "")
                rel_type = rel.get("type", "relates_to")
                confidence = rel.get("confidence", 0.7)
                
                if from_entity and to_entity:
                    # 엔티티가 생성되어 있는지 확인
                    if from_entity in created_entities or to_entity in created_entities:
                        # 필요시 엔티티 생성
                        if from_entity not in created_entities:
                            graph.create_entity_node(from_entity)
                            created_entities.add(from_entity)
                        if to_entity not in created_entities:
                            graph.create_entity_node(to_entity)
                            created_entities.add(to_entity)
                        
                        graph.create_relationship(
                            from_entity, rel_type, to_entity, 
                            confidence, 
                            {"method": rel.get("method", "extracted")}
                        )
                        total_relationships += 1
            
            print(f"    ✅ 노트: 1개, 엔티티: {len(created_entities)}개, 관계: {len(relationships)}개")
        
        print(f"\n  💾 파일 완료: {len(atomic_notes)}개 노트 처리")
    
    # 최종 통계
    print("\n" + "=" * 60)
    print("📊 Import 통계")
    print("=" * 60)
    print(f"처리된 파일: {len(json_files)}개")
    print(f"생성된 Atomic Notes: {total_notes}개")
    print(f"생성된 Entities: {total_entities}개")
    print(f"생성된 Relationships: {total_relationships}개")
    
    # Graph DB 통계
    print("\n📊 Graph DB 통계:")
    stats = graph.get_graph_stats()
    print(f"총 노드: {stats['total_nodes']}개")
    print(f"총 관계: {stats['total_relationships']}개")
    print(f"노드 타입별:")
    for node_type, count in stats['nodes'].items():
        print(f"  - {node_type}: {count}개")
    print(f"관계 타입별:")
    for rel_type, count in stats['relationships'].items():
        print(f"  - {rel_type}: {count}개")
    
    print("\n✅ Stage 3 완료!")
    print(f"🌐 Neo4j Browser: http://localhost:7474")
    print(f"   (Username: {NEO4J_USER}, Password: {NEO4J_PASSWORD})")
    
    # 연결 종료
    graph.close()

except Exception as e:
    print(f"\n❌ 에러 발생: {e}")
    print("\nNeo4j 서버가 실행 중인지 확인하세요:")
    print("docker run -d -p 7474:7474 -p 7687:7687 \\")
    print("  -e NEO4J_AUTH=neo4j/password \\")
    print("  --name neo4j-pkm \\")
    print("  neo4j:latest")
    import traceback
    traceback.print_exc()
