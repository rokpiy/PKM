"""
Entity & Relationship Extraction (Simple Version)
Gemini API 결과 + Regex 패턴 매칭 기반
spaCy 없이 동작하는 경량 버전
"""

import re
import json
from typing import List, Dict


class SimpleEntityExtractor:
    """간단한 엔티티와 관계 추출기 (Gemini 결과 기반)"""
    
    def __init__(self):
        """초기화"""
        print("✅ Simple Entity Extractor 초기화 완료")
    
    def enhance_gemini_entities(self, atomic_note: Dict) -> Dict:
        """
        Gemini가 추출한 엔티티를 개선하고 추가 관계 추출
        
        Args:
            atomic_note: Atomic Note (Gemini의 extracted_entities 포함)
            
        Returns:
            개선된 Atomic Note
        """
        # Gemini가 이미 추출한 엔티티 가져오기
        gemini_entities = atomic_note.get("extracted_entities", [])
        
        # 텍스트에서 추가 엔티티 추출
        content = atomic_note.get("content", "")
        detailed_content = atomic_note.get("detailed_content", "")
        full_text = f"{content} {detailed_content}"
        
        # 추가 엔티티 추출 (간단한 패턴 기반)
        additional_entities = self._extract_additional_entities(full_text)
        
        # 중복 제거
        all_entities = gemini_entities + additional_entities
        unique_entities = self._deduplicate_entities(all_entities)
        
        # 관계 추출
        gemini_relationships = atomic_note.get("relationships", [])
        additional_relationships = self.extract_relationships(full_text, unique_entities)
        
        # 결과 저장
        atomic_note["entities_enhanced"] = unique_entities
        atomic_note["relationships_enhanced"] = gemini_relationships + additional_relationships
        
        return atomic_note
    
    def _extract_additional_entities(self, text: str) -> List[str]:
        """
        간단한 패턴으로 추가 엔티티 추출
        """
        entities = []
        
        # 대문자로 시작하는 단어 (고유명사 추정)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.extend(proper_nouns)
        
        # 한글 고유명사 패턴 (조사 앞의 명사)
        korean_nouns = re.findall(r'([가-힣]+)(?:이|가|은|는|을|를|의|에|와|과)', text)
        entities.extend(korean_nouns)
        
        # 기술 용어 패턴 (대문자 약어)
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        entities.extend(acronyms)
        
        return list(set(entities))  # 중복 제거
    
    def _deduplicate_entities(self, entities: List[str]) -> List[str]:
        """엔티티 중복 제거 (대소문자 무시)"""
        seen = set()
        unique = []
        
        for entity in entities:
            entity_lower = entity.lower()
            if entity_lower not in seen:
                seen.add(entity_lower)
                unique.append(entity)
        
        return unique
    
    def extract_relationships(self, text: str, entities: List[str]) -> List[Dict]:
        """
        엔티티 간 관계 추출 (패턴 기반)
        
        Args:
            text: 원본 텍스트
            entities: 엔티티 리스트
            
        Returns:
            관계 리스트
        """
        relationships = []
        
        # 한글 관계 패턴
        korean_patterns = {
            "supports": [
                r"({})(?:이|가)\s+({})(?:을|를)\s+지지",
                r"({})(?:은|는)\s+({})(?:을|를)\s+옹호"
            ],
            "contradicts": [
                r"({})(?:이|가)\s+({})(?:와|과)\s+모순",
                r"({})(?:은|는)\s+({})(?:와|과)\s+반대"
            ],
            "is_example_of": [
                r"({})(?:은|는)\s+({})의\s+예시",
                r"({})(?:은|는)\s+({})의\s+사례"
            ],
            "causes": [
                r"({})(?:이|가)\s+({})(?:을|를)\s+야기",
                r"({})(?:은|는)\s+({})(?:을|를)\s+초래"
            ],
            "implements": [
                r"({})(?:이|가)\s+({})(?:을|를)\s+구현",
                r"({})(?:은|는)\s+({})(?:을|를)\s+실현"
            ],
            "uses": [
                r"({})(?:이|가)\s+({})(?:을|를)\s+사용",
                r"({})(?:은|는)\s+({})(?:을|를)\s+활용"
            ],
            "based_on": [
                r"({})(?:은|는)\s+({})에?\s+기반",
                r"({})(?:은|는)\s+({})를?\s+바탕"
            ]
        }
        
        # 영문 관계 패턴
        english_patterns = {
            "supports": [r"({}) supports? ({})"],
            "contradicts": [r"({}) contradicts? ({})"],
            "is_example_of": [r"({}) is an? example of ({})"],
            "causes": [r"({}) causes? ({})"],
            "implements": [r"({}) implements? ({})"],
            "uses": [r"({}) uses? ({})"],
            "based_on": [r"({}) is based on ({})"]
        }
        
        # 엔티티 리스트를 regex 패턴으로 변환
        entity_pattern = "|".join(re.escape(e) for e in entities)
        
        # 모든 패턴 적용
        all_patterns = {**korean_patterns, **english_patterns}
        
        for relation_type, patterns in all_patterns.items():
            for pattern_template in patterns:
                # 엔티티 위치에 실제 엔티티 패턴 삽입
                pattern = pattern_template.format(entity_pattern, entity_pattern)
                
                try:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        relationships.append({
                            "from": match.group(1).strip(),
                            "type": relation_type,
                            "to": match.group(2).strip(),
                            "confidence": 0.7,
                            "method": "pattern_matching"
                        })
                except:
                    pass  # 패턴 매칭 실패 시 무시
        
        return relationships
    
    def process_atomic_notes_batch(self, atomic_notes_results: List[Dict]) -> List[Dict]:
        """
        여러 Atomic Notes 배치 처리
        
        Args:
            atomic_notes_results: Gemini의 Atomic Notes 결과 리스트
            
        Returns:
            개선된 Atomic Notes 리스트
        """
        enhanced_results = []
        
        for result in atomic_notes_results:
            atomic_notes = result.get("atomic_notes", [])
            
            for note in atomic_notes:
                enhanced_note = self.enhance_gemini_entities(note)
                
            result["atomic_notes"] = atomic_notes
            enhanced_results.append(result)
        
        return enhanced_results


# CLI 인터페이스
if __name__ == "__main__":
    print("🔬 Simple Entity Extraction 테스트")
    print("=" * 60)
    
    # 테스트용 Atomic Note (Gemini 결과 시뮬레이션)
    sample_note = {
        "id": "note_test_001",
        "title": "AI와 머신러닝",
        "content": "인공지능(AI)은 머신러닝을 사용하여 문제를 해결합니다.",
        "detailed_content": "딥러닝은 머신러닝의 한 예시입니다. 구글과 오픈AI는 AI 연구를 선도합니다.",
        "extracted_entities": ["AI", "머신러닝", "딥러닝"],
        "relationships": [
            {"from": "AI", "type": "uses", "to": "머신러닝"}
        ]
    }
    
    # Extractor 초기화
    extractor = SimpleEntityExtractor()
    
    # 개선
    enhanced_note = extractor.enhance_gemini_entities(sample_note)
    
    print(f"\n📝 원본 엔티티: {sample_note['extracted_entities']}")
    print(f"✅ 개선된 엔티티: {enhanced_note.get('entities_enhanced', [])}")
    
    print(f"\n📝 원본 관계: {len(sample_note['relationships'])}개")
    print(f"✅ 개선된 관계: {len(enhanced_note.get('relationships_enhanced', []))}개")
    
    for i, rel in enumerate(enhanced_note.get('relationships_enhanced', [])[:5], 1):
        print(f"  [{i}] {rel['from']:15s} --[{rel['type']}]--> {rel['to']:15s}")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")

