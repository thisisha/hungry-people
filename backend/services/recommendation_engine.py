import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

class RecommendationEngine:
    """추천 엔진 클래스"""
    
    def __init__(self, db_path: str = "hungry_people.db"):
        self.db_path = db_path
    
    def get_location_based_recommendations(self, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """장소 기반 추천 - 행사 장소 근처 백년가게 추천"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 장소명에서 지역 키워드 추출
        location_keywords = self._extract_location_keywords(location)
        
        if not location_keywords:
            conn.close()
            return []
        
        # 키워드로 주소 검색
        recommendations = []
        
        for keyword in location_keywords:
            cursor.execute('''
                SELECT * FROM restaurants 
                WHERE address LIKE ?
                ORDER BY name
                LIMIT ?
            ''', (f'%{keyword}%', limit))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            recommendations.extend(results)
        
        # 중복 제거
        unique_recommendations = {}
        for rec in recommendations:
            if rec['id'] not in unique_recommendations:
                unique_recommendations[rec['id']] = rec
        
        final_recommendations = list(unique_recommendations.values())[:limit]
        
        conn.close()
        return final_recommendations
    
    def get_event_based_recommendations(self, event_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """행사 기반 추천 - 특정 행사 근처 백년가게 추천"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 행사 정보 조회
        cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
        event = cursor.fetchone()
        
        if not event:
            conn.close()
            return []
        
        # 행사 장소로 추천
        event_location = event[5]  # location 컬럼
        recommendations = self.get_location_based_recommendations(event_location, limit)
        
        conn.close()
        return recommendations
    
    def get_region_based_recommendations(self, region: str, limit: int = 10) -> List[Dict[str, Any]]:
        """지역 기반 추천 - 특정 지역의 인기 백년가게 추천"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM restaurants 
            WHERE region = ?
            ORDER BY name
            LIMIT ?
        ''', (region, limit))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_smart_recommendations(self, user_query: str, limit: int = 10) -> Dict[str, Any]:
        """스마트 추천 - 사용자 쿼리 분석하여 최적의 추천 제공"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 쿼리 분석
        query_type = self._analyze_query(user_query)
        
        recommendations = {
            'type': query_type,
            'restaurants': [],
            'events': [],
            'suggestions': []
        }
        
        if query_type == 'location':
            # 장소명으로 추천
            recommendations['restaurants'] = self.get_location_based_recommendations(user_query, limit)
            
            # 관련 행사도 검색
            cursor.execute('''
                SELECT * FROM events 
                WHERE location LIKE ? OR event_name LIKE ?
                LIMIT 5
            ''', (f'%{user_query}%', f'%{user_query}%'))
            
            columns = [description[0] for description in cursor.description]
            recommendations['events'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        elif query_type == 'region':
            # 지역으로 추천
            recommendations['restaurants'] = self.get_region_based_recommendations(user_query, limit)
            
            # 해당 지역 행사 검색
            cursor.execute('''
                SELECT * FROM events 
                WHERE region = ?
                LIMIT 5
            ''', (user_query,))
            
            columns = [description[0] for description in cursor.description]
            recommendations['events'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        else:
            # 일반 검색
            cursor.execute('''
                SELECT * FROM restaurants 
                WHERE name LIKE ? OR address LIKE ?
                LIMIT ?
            ''', (f'%{user_query}%', f'%{user_query}%', limit))
            
            columns = [description[0] for description in cursor.description]
            recommendations['restaurants'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # 추천 제안 생성
        recommendations['suggestions'] = self._generate_suggestions(user_query, query_type)
        
        conn.close()
        return recommendations
    
    def _extract_location_keywords(self, location: str) -> List[str]:
        """장소명에서 지역 키워드 추출"""
        keywords = []
        
        # 주요 지역 키워드
        regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
                  '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주',
                  '대덕특구', '과학벨트', '부산특구', '대구특구', '광주특구', '울산특구']
        
        for region in regions:
            if region in location:
                keywords.append(region)
        
        return keywords
    
    def _analyze_query(self, query: str) -> str:
        """쿼리 분석하여 타입 결정"""
        query_lower = query.lower()
        
        # 지역 키워드 체크
        region_keywords = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
                          '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
        
        for region in region_keywords:
            if region in query:
                return 'region'
        
        # 행사 관련 키워드 체크
        event_keywords = ['회의', '세미나', '컨퍼런스', '포럼', '워크샵', '행사', '이벤트',
                         '심포지움', '설명회', '발표회', '전시회', '박람회']
        
        for keyword in event_keywords:
            if keyword in query:
                return 'event'
        
        # 장소 관련 키워드 체크
        location_keywords = ['센터', '홀', '컨벤션', '대학교', '대학', '연구원', '기업',
                            '아트센터', '문화센터', 'DCC', 'BCC']
        
        for keyword in location_keywords:
            if keyword in query:
                return 'location'
        
        return 'general'
    
    def _generate_suggestions(self, query: str, query_type: str) -> List[str]:
        """추천 제안 생성"""
        suggestions = []
        
        if query_type == 'region':
            suggestions.extend([
                f"{query} 지역의 인기 백년가게",
                f"{query} 근처 행사 일정",
                f"{query} 지역 음식점 추천"
            ])
        elif query_type == 'event':
            suggestions.extend([
                f"{query} 관련 행사 정보",
                f"{query} 장소 근처 백년가게",
                "행사 참석자 추천 식당"
            ])
        elif query_type == 'location':
            suggestions.extend([
                f"{query} 근처 백년가게",
                f"{query} 주변 음식점",
                f"{query} 지역 행사 정보"
            ])
        else:
            suggestions.extend([
                "전국 백년가게 검색",
                "지역별 음식점 추천",
                "행사 일정 확인"
            ])
        
        return suggestions