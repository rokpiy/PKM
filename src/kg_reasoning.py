"""
Knowledge Graph Reasoning
Stage 4: Graph 기반 추론 및 Context 검색
"""

from neo4j import GraphDatabase
from typing import Dict, List, Optional
import re


class KGReasoner:
    """Knowledge Graph 추론 엔진"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 auth: tuple = ("neo4j", "password")):
        """
        Args:
            uri: Neo4j 서버 주소
            auth: (username, password) 튜플
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=auth)
            self.driver.verify_connectivity()
            print(f"✅ Neo4j 연결 성공: {uri}")
        except Exception as e:
            print(f"❌ Neo4j 연결 실패: {e}")
            raise
    
    def close(self):
        """연결 종료"""
        if self.driver:
            self.driver.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _get_all_entity_names(self) -> List[str]:
        """Graph에 있는 모든 엔티티 이름 가져오기 (캐싱용)"""
        with self.driver.session() as session:
            result = session.run("MATCH (e:Entity) RETURN e.name as name")
            return [record["name"] for record in result]
    
    def extract_entities_from_text(self, text: str) -> List[str]:
        """
        질문에서 엔티티 추출 (Graph의 실제 엔티티와 매칭)
        
        Args:
            text: 질문 텍스트
            
        Returns:
            Graph에 존재하는 엔티티 목록
        """
        # 불용어 리스트 (일반적인 단어, 조사 등)
        stopwords = {
            # 한글 조사 및 접미사
            '이', '가', '을', '를', '은', '는', '에', '에서', '와', '과', '의', '로', '으로',
            '도', '만', '부터', '까지', '에게', '한테', '께', '보다', '처럼', '같이',
            # 일반적인 단어
            '것', '거', '수', '때', '등', '중', '간', '내', '외', '상', '하', '전', '후',
            '관계', '이유', '방법', '특징', '의미', '정의', '개념', '설명', '내용',
            # 질문 단어
            '무엇', '어디', '언제', '누구', '어떻게', '왜', '어떤', '무슨',
            # 짧은 동사/형용사
            '하다', '되다', '있다', '없다', '이다', '아니다'
        }
        
        # Graph의 모든 엔티티 가져오기
        all_entities = self._get_all_entity_names()
        
        # 질문에 포함된 엔티티 찾기 (대소문자 무시)
        text_lower = text.lower()
        found_entities = []
        
        for entity in all_entities:
            if not entity or len(entity) < 2:  # 너무 짧은 엔티티 제외
                continue
            
            entity_lower = entity.lower()
            
            # 불용어 제외
            if entity_lower in stopwords:
                continue
            
            # 단순 포함이 아닌, 단어 경계 고려
            if entity_lower in text_lower:
                # 길이가 2글자 이상이거나, 영문/숫자가 포함된 경우만
                if len(entity) >= 2 and (
                    len(entity) >= 3 or  # 3글자 이상은 무조건 포함
                    any(c.isalnum() and ord(c) < 128 for c in entity)  # 영문/숫자 포함
                ):
                    found_entities.append(entity)
        
        # 길이순으로 정렬 (긴 엔티티 우선 - "머신러닝" > "머신")
        found_entities.sort(key=len, reverse=True)
        
        return found_entities[:10]  # 최대 10개
    
    def find_entity_neighbors(self, entity_name: str, hops: int = 2) -> Dict:
        """
        엔티티를 중심으로 N-hop 이웃 찾기
        
        Graph RAG의 핵심: 관련된 엔티티를 찾아서 Context 구성
        
        Args:
            entity_name: 검색할 엔티티 이름
            hops: 탐색 깊이 (기본 2)
            
        Returns:
            entities와 relationships 딕셔너리
        """
        with self.driver.session() as session:
            # APOC 없이 구현 (최대 2-hop)
            if hops == 1:
                query = """
                MATCH (e:Entity {name: $entity_name})-[r]-(related)
                RETURN e, related, r
                LIMIT 50
                """
            else:  # hops == 2 or more
                query = """
                MATCH path = (e:Entity {name: $entity_name})-[*1..2]-(related)
                WITH e, related, relationships(path) as rels
                RETURN DISTINCT e, related, rels
                LIMIT 50
                """
            
            result = session.run(query, entity_name=entity_name)
            
            entities = []
            relationships = []
            entity_ids = set()
            
            for record in result:
                # 중심 엔티티
                if record["e"] and record["e"].element_id not in entity_ids:
                    entities.append(dict(record["e"]))
                    entity_ids.add(record["e"].element_id)
                
                # 관련 엔티티
                if record["related"] and record["related"].element_id not in entity_ids:
                    entities.append(dict(record["related"]))
                    entity_ids.add(record["related"].element_id)
                
                # 관계
                if "rels" in record and record["rels"]:
                    for rel in record["rels"]:
                        relationships.append({
                            "type": rel.type,
                            "properties": dict(rel)
                        })
                elif "r" in record and record["r"]:
                    relationships.append({
                        "type": record["r"].type,
                        "properties": dict(record["r"])
                    })
            
            return {
                "entities": entities,
                "relationships": relationships
            }
    
    def semantic_path_search(self, start_entity: str, end_entity: str, 
                           max_depth: int = 5) -> List[Dict]:
        """
        두 엔티티 간의 의미있는 경로 찾기
        
        예: "LLM" → ... → "Agentic Reasoning"
             간에 어떤 경로로 연결되어 있나?
        
        Args:
            start_entity: 시작 엔티티
            end_entity: 목표 엔티티
            max_depth: 최대 경로 길이
            
        Returns:
            경로 리스트
        """
        with self.driver.session() as session:
            query = f"""
            MATCH path = shortestPath(
                (start:Entity {{name: $start_entity}})-[*1..{max_depth}]-(end:Entity {{name: $end_entity}})
            )
            RETURN [node IN nodes(path) | node.name] as entity_path,
                   [rel IN relationships(path) | type(rel)] as relationship_types,
                   length(path) as path_length
            LIMIT 5
            """
            
            results = session.run(query, 
                                 start_entity=start_entity,
                                 end_entity=end_entity)
            
            paths = []
            for record in results:
                paths.append({
                    "entity_path": record["entity_path"],
                    "relationships": record["relationship_types"],
                    "length": record["path_length"]
                })
            
            return paths
    
    def find_related_notes(self, entity_name: str, top_k: int = 5) -> List[Dict]:
        """
        특정 엔티티를 포함하는 Atomic Notes 찾기
        
        Args:
            entity_name: 엔티티 이름
            top_k: 반환할 최대 노트 수
            
        Returns:
            관련 노트 리스트
        """
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity {name: $entity_name})<-[:MENTIONS]-(n:AtomicNote)
            RETURN n.id as id, n.title as title, n.content as content, 
                   n.detailed_content as detailed_content,
                   n.domain as domain
            ORDER BY n.created_at DESC
            LIMIT $top_k
            """
            
            results = session.run(query, 
                                 entity_name=entity_name,
                                 top_k=top_k)
            
            notes = []
            for record in results:
                notes.append({
                    "id": record["id"],
                    "title": record["title"],
                    "content": record["content"],
                    "detailed_content": record.get("detailed_content", ""),
                    "domain": record.get("domain", "general")
                })
            
            return notes
    
    def find_similar_entities(self, entity_name: str, top_k: int = 10) -> List[Dict]:
        """
        유사한 엔티티 찾기 (같은 도메인, 비슷한 관계 패턴)
        
        Args:
            entity_name: 기준 엔티티
            top_k: 반환할 최대 엔티티 수
            
        Returns:
            유사 엔티티 리스트
        """
        with self.driver.session() as session:
            query = """
            MATCH (e1:Entity {name: $entity_name})
            MATCH (e2:Entity)
            WHERE e2.name <> $entity_name 
              AND e2.domain = e1.domain
            WITH e2, COUNT { (e2)-[]->() } as out_degree,
                     COUNT { (e2)<-[]-() } as in_degree
            RETURN e2.name as name, e2.domain as domain, 
                   out_degree + in_degree as connections
            ORDER BY connections DESC
            LIMIT $top_k
            """
            
            results = session.run(query, entity_name=entity_name, top_k=top_k)
            
            similar = []
            for record in results:
                similar.append({
                    "name": record["name"],
                    "domain": record["domain"],
                    "connections": record["connections"]
                })
            
            return similar
    
    def reasoning_chain(self, question: str, depth: int = 2) -> Dict:
        """
        질문 → 엔티티 추출 → Graph 탐색 → Context 구성
        
        Graph RAG의 핵심 워크플로우
        
        Args:
            question: 사용자 질문
            depth: 탐색 깊이
            
        Returns:
            추론 결과 (엔티티, 노트, 경로 등)
        """
        print(f"\n🔍 질문 분석: {question}")
        
        # 1. 질문에서 주요 엔티티 추출 (Graph에 있는 것만)
        existing_entities = self.extract_entities_from_text(question)
        print(f"✅ Graph에서 발견된 엔티티: {existing_entities[:5]}")
        
        if not existing_entities:
            return {
                "question": question,
                "entities": [],
                "entity_contexts": [],
                "related_notes": [],
                "connecting_paths": [],
                "message": "질문에서 Graph에 존재하는 엔티티를 찾지 못했습니다."
            }
        
        # 3. 각 엔티티의 이웃 찾기
        all_context = []
        all_notes = []
        
        for entity in existing_entities[:3]:  # 최대 3개 엔티티
            print(f"\n  📊 '{entity}' 주변 탐색 중...")
            
            neighbors = self.find_entity_neighbors(entity, hops=depth)
            related_notes = self.find_related_notes(entity, top_k=3)
            
            all_context.append({
                "entity": entity,
                "neighbors": neighbors,
                "related_notes_count": len(related_notes)
            })
            
            all_notes.extend(related_notes)
            print(f"     - 연결된 엔티티: {len(neighbors['entities'])}개")
            print(f"     - 관련 노트: {len(related_notes)}개")
        
        # 4. 엔티티 간 경로 찾기
        paths = []
        if len(existing_entities) >= 2:
            print(f"\n  🔗 엔티티 간 경로 탐색...")
            for i in range(min(2, len(existing_entities) - 1)):
                for j in range(i + 1, min(i + 2, len(existing_entities))):
                    e1, e2 = existing_entities[i], existing_entities[j]
                    path = self.semantic_path_search(e1, e2, max_depth=4)
                    if path:
                        paths.extend(path)
                        print(f"     - {e1} ↔ {e2}: {len(path)}개 경로 발견")
        
        return {
            "question": question,
            "entities": existing_entities,
            "entity_contexts": all_context,
            "related_notes": all_notes,
            "connecting_paths": paths
        }
    
    def entity_exists(self, entity_name: str) -> bool:
        """엔티티가 Graph에 존재하는지 확인"""
        with self.driver.session() as session:
            query = "MATCH (e:Entity {name: $name}) RETURN count(e) > 0 as exists"
            result = session.run(query, name=entity_name).single()
            return result["exists"] if result else False
    
    def get_entity_summary(self, entity_name: str) -> Dict:
        """엔티티 요약 정보"""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity {name: $name})
            OPTIONAL MATCH (e)-[r]-()
            OPTIONAL MATCH (e)<-[:MENTIONS]-(n:AtomicNote)
            RETURN e.name as name, 
                   e.domain as domain,
                   e.label as label,
                   COUNT(DISTINCT r) as total_relationships,
                   COUNT(DISTINCT n) as mentioned_in_notes
            """
            
            result = session.run(query, name=entity_name).single()
            
            if result:
                return {
                    "name": result["name"],
                    "domain": result["domain"],
                    "label": result["label"],
                    "relationships": result["total_relationships"],
                    "notes": result["mentioned_in_notes"]
                }
            return {}


def create_graph_context_for_llm(reasoning_result: Dict, max_tokens: int = 2000) -> str:
    """
    Graph 추론 결과를 LLM에 최적화된 Context로 변환
    
    Traditional RAG: 긴 문서 청크 → 토큰 낭비
    Graph RAG: 직접 관련된 엔티티와 관계만 → 효율적
    
    Args:
        reasoning_result: reasoning_chain의 결과
        max_tokens: 최대 토큰 수 (대략적)
        
    Returns:
        LLM에 제공할 컨텍스트 문자열
    """
    context = f"""## 🔍 질문 분석
질문: {reasoning_result['question']}
추출된 핵심 개념: {', '.join(reasoning_result['entities'])}

## 📊 관련 지식 그래프

"""
    
    # 엔티티별 컨텍스트
    for entity_ctx in reasoning_result['entity_contexts']:
        context += f"\n### {entity_ctx['entity']}\n"
        
        neighbors = entity_ctx['neighbors']
        if neighbors['entities']:
            entity_names = [e.get('name', str(e)) for e in neighbors['entities'][:5]]
            context += f"관련 개념: {', '.join(entity_names)}\n"
        
        if entity_ctx['related_notes_count'] > 0:
            context += f"관련 노트: {entity_ctx['related_notes_count']}개\n"
    
    # 연결 경로
    if reasoning_result['connecting_paths']:
        context += "\n### 개념 간 연결 경로\n"
        for i, path in enumerate(reasoning_result['connecting_paths'][:3], 1):
            # None 값 필터링
            entity_path = [str(e) for e in path['entity_path'] if e is not None]
            if entity_path:
                path_str = " → ".join(entity_path)
                context += f"{i}. {path_str}\n"
    
    # 관련 노트 내용
    if reasoning_result['related_notes']:
        context += "\n## 📝 관련 노트 내용\n"
        for i, note in enumerate(reasoning_result['related_notes'][:5], 1):
            context += f"\n### {i}. {note['title']}\n"
            context += f"{note['content'][:200]}...\n"
    
    # 토큰 제한 (대략 1 token ≈ 4 characters)
    if len(context) > max_tokens * 4:
        context = context[:max_tokens * 4] + "\n\n... (컨텍스트가 잘렸습니다)"
    
    return context


# CLI 인터페이스
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # 환경변수에서 Neo4j 설정 가져오기
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    print("🔬 Knowledge Graph Reasoning 테스트")
    print("=" * 60)
    
    try:
        with KGReasoner(NEO4J_URI, (NEO4J_USER, NEO4J_PASSWORD)) as reasoner:
            # 테스트 질문
            test_questions = [
                "AI와 머신러닝의 관계는?",
                "스타트업에서 네트워킹이 중요한 이유는?",
                "PKM 시스템은 어떻게 작동하나?"
            ]
            
            for question in test_questions:
                print(f"\n{'=' * 60}")
                result = reasoner.reasoning_chain(question, depth=2)
                
                print(f"\n📋 추론 결과:")
                print(f"  - 발견된 엔티티: {len(result['entities'])}개")
                print(f"  - 관련 노트: {len(result['related_notes'])}개")
                print(f"  - 연결 경로: {len(result['connecting_paths'])}개")
                
                # LLM Context 생성
                context = create_graph_context_for_llm(result, max_tokens=500)
                print(f"\n💬 LLM Context (처음 300자):")
                print(context[:300] + "...")
            
            print("\n✅ 테스트 완료!")
    
    except Exception as e:
        print(f"\n❌ 에러: {e}")
        import traceback
        traceback.print_exc()

