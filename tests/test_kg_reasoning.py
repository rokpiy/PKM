"""
Knowledge Graph Reasoning 테스트
Stage 4: Graph 기반 추론 및 Context 검색
"""

import os
import sys
from pathlib import Path

# src 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from kg_reasoning import KGReasoner, create_graph_context_for_llm

# .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print("🔬 Stage 4: Knowledge Graph Reasoning")
print("=" * 60)

# Neo4j 설정
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

print(f"🔧 Neo4j 설정:")
print(f"   URI: {NEO4J_URI}")
print(f"   User: {NEO4J_USER}")
print("=" * 60)

try:
    reasoner = KGReasoner(NEO4J_URI, (NEO4J_USER, NEO4J_PASSWORD))
    
    print("\n📋 테스트 옵션:")
    print("1. 대화형 질문 (직접 입력)")
    print("2. 샘플 질문 테스트")
    print("3. 엔티티 정보 조회")
    print("4. 엔티티 간 경로 탐색")
    print("5. 종료")
    
    choice = input("\n선택 (1-5): ").strip()
    
    if choice == "1":
        # 대화형 질문
        print("\n💬 질문을 입력하세요 (종료: 'quit'):")
        
        while True:
            question = input("\n❓ 질문: ").strip()
            
            if question.lower() in ['quit', 'exit', '종료', 'q']:
                print("종료합니다.")
                break
            
            if not question:
                continue
            
            # 추론 실행
            result = reasoner.reasoning_chain(question, depth=2)
            
            # 결과 출력
            print(f"\n{'=' * 60}")
            print("📊 추론 결과")
            print(f"{'=' * 60}")
            
            if result.get('message'):
                print(f"\n⚠️  {result['message']}")
            else:
                print(f"\n✅ 발견된 엔티티: {', '.join(result['entities'])}")
                print(f"✅ 관련 노트: {len(result['related_notes'])}개")
                print(f"✅ 연결 경로: {len(result['connecting_paths'])}개")
                
                # 관련 노트 출력
                if result['related_notes']:
                    print(f"\n📝 관련 노트:")
                    for i, note in enumerate(result['related_notes'][:3], 1):
                        print(f"\n  {i}. {note['title']}")
                        print(f"     {note['content'][:150]}...")
                
                # 연결 경로 출력
                if result['connecting_paths']:
                    print(f"\n🔗 엔티티 간 연결:")
                    for i, path in enumerate(result['connecting_paths'][:3], 1):
                        # None 값 필터링
                        entity_path = [str(e) for e in path['entity_path'] if e is not None]
                        if entity_path:
                            path_str = " → ".join(entity_path)
                            print(f"  {i}. {path_str}")
                
                # LLM Context 생성
                print(f"\n{'=' * 60}")
                print("💬 LLM에 제공할 Context")
                print(f"{'=' * 60}")
                context = create_graph_context_for_llm(result, max_tokens=1000)
                print(context)
    
    elif choice == "2":
        # 샘플 질문 테스트
        sample_questions = [
            "AI와 머신러닝의 관계는?",
            "스타트업에서 네트워킹이 중요한 이유는?",
            "PKM 시스템은 어떻게 작동하나?",
            "Agentic Reasoning이란 무엇인가?",
            "미국 스타트업 생태계의 특징은?"
        ]
        
        print(f"\n📚 {len(sample_questions)}개 샘플 질문 테스트:")
        
        for i, question in enumerate(sample_questions, 1):
            print(f"\n{'=' * 60}")
            print(f"[{i}/{len(sample_questions)}] {question}")
            print(f"{'=' * 60}")
            
            result = reasoner.reasoning_chain(question, depth=2)
            
            if result.get('message'):
                print(f"⚠️  {result['message']}")
            else:
                print(f"✅ 엔티티: {', '.join(result['entities'][:3])}")
                print(f"✅ 노트: {len(result['related_notes'])}개")
                print(f"✅ 경로: {len(result['connecting_paths'])}개")
                
                if result['related_notes']:
                    print(f"\n📝 대표 노트: {result['related_notes'][0]['title']}")
        
        print(f"\n✅ 샘플 테스트 완료!")
    
    elif choice == "3":
        # 엔티티 정보 조회
        entity_name = input("\n🔍 조회할 엔티티 이름: ").strip()
        
        if entity_name:
            print(f"\n엔티티 '{entity_name}' 조회 중...")
            
            # 엔티티 존재 확인
            if reasoner.entity_exists(entity_name):
                # 요약 정보
                summary = reasoner.get_entity_summary(entity_name)
                print(f"\n📊 엔티티 정보:")
                print(f"  - 이름: {summary['name']}")
                print(f"  - 도메인: {summary.get('domain', 'N/A')}")
                print(f"  - 라벨: {summary.get('label', 'N/A')}")
                print(f"  - 관계 수: {summary['relationships']}개")
                print(f"  - 언급된 노트: {summary['notes']}개")
                
                # 이웃 엔티티
                neighbors = reasoner.find_entity_neighbors(entity_name, hops=1)
                print(f"\n🔗 연결된 엔티티 ({len(neighbors['entities'])}개):")
                for e in neighbors['entities'][:10]:
                    print(f"  - {e.get('name', 'Unknown')}")
                
                # 관련 노트
                notes = reasoner.find_related_notes(entity_name, top_k=5)
                print(f"\n📝 관련 노트 ({len(notes)}개):")
                for note in notes:
                    print(f"  - {note['title']}")
                
                # 유사 엔티티
                similar = reasoner.find_similar_entities(entity_name, top_k=5)
                if similar:
                    print(f"\n🎯 유사한 엔티티:")
                    for s in similar:
                        print(f"  - {s['name']} (연결: {s['connections']}개)")
            else:
                print(f"❌ 엔티티 '{entity_name}'를 찾을 수 없습니다.")
    
    elif choice == "4":
        # 엔티티 간 경로 탐색
        print("\n🔗 두 엔티티 간의 연결 경로를 탐색합니다.")
        entity1 = input("시작 엔티티: ").strip()
        entity2 = input("목표 엔티티: ").strip()
        
        if entity1 and entity2:
            print(f"\n경로 탐색 중: '{entity1}' → '{entity2}'")
            
            paths = reasoner.semantic_path_search(entity1, entity2, max_depth=5)
            
            if paths:
                print(f"\n✅ {len(paths)}개 경로 발견:")
                for i, path in enumerate(paths, 1):
                    # None 값 필터링
                    entity_path = [str(e) for e in path['entity_path'] if e is not None]
                    relationships = [str(r) for r in path['relationships'] if r is not None]
                    
                    if entity_path:
                        path_str = " → ".join(entity_path)
                        print(f"\n  경로 {i} (길이: {path['length']}):")
                        print(f"  {path_str}")
                        if relationships:
                            print(f"  관계: {' → '.join(relationships)}")
            else:
                print(f"\n❌ 경로를 찾지 못했습니다.")
                print(f"   두 엔티티가 Graph에 존재하는지, 연결되어 있는지 확인하세요.")
    
    else:
        print("종료")
    
    # 연결 종료
    reasoner.close()
    print("\n✅ 완료!")

except Exception as e:
    print(f"\n❌ 에러 발생: {e}")
    print("\nNeo4j 서버가 실행 중인지 확인하세요:")
    print("  - Neo4j Desktop에서 Database가 Start 되어 있어야 합니다.")
    print("  - 또는: docker run -d -p 7474:7474 -p 7687:7687 \\")
    print("            -e NEO4J_AUTH=neo4j/password neo4j:latest")
    import traceback
    traceback.print_exc()

