# 간단한 샘플 데이터로 시작
import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

class DatabaseManager:
    """SQLite 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "hungry_people.db"):
        self.db_path = db_path
        self.init_database()
        self.load_sample_data()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 백년가게 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT,
                region TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 행사일정 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                organization TEXT,
                event_name TEXT NOT NULL,
                host_organization TEXT,
                region TEXT,
                location TEXT,
                tech_category TEXT,
                hashtags TEXT,
                start_date TEXT,
                end_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 지역별 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurants_region ON restaurants(region)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_region ON events(region)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_location ON events(location)')
        
        conn.commit()
        conn.close()
    
    def load_sample_data(self):
        """전체 데이터 로드"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 데이터 삭제
        cursor.execute('DELETE FROM restaurants')
        cursor.execute('DELETE FROM events')
        
        # 전체 백년가게 데이터 로드
        try:
            from services.data_processor import DataProcessor
            processor = DataProcessor()
            
            # 백년가게 데이터 로드
            restaurant_data = processor.load_restaurant_data('data/소상공인시장진흥공단_전국 백년가게 지정리스트 현황 정보_20250724.csv')
            for restaurant in restaurant_data:
                cursor.execute('''
                    INSERT INTO restaurants (id, name, address, phone, region)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    restaurant['id'],
                    restaurant['name'],
                    restaurant['address'],
                    restaurant['phone'],
                    restaurant['region']
                ))
            
            # 행사일정 데이터 로드
            event_data = processor.load_event_data('data/(재)연구개발특구진흥재단_행사일정_20250714.csv')
            for event in event_data:
                cursor.execute('''
                    INSERT INTO events (id, organization, event_name, host_organization, 
                                       region, location, tech_category, hashtags, start_date, end_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event['id'],
                    event['organization'],
                    event['event_name'],
                    event['host_organization'],
                    event['region'],
                    event['location'],
                    event['tech_category'],
                    event['hashtags'],
                    event['start_date'],
                    event['end_date']
                ))
            
            print(f"전체 데이터 로드 완료: 백년가게 {len(restaurant_data)}개, 행사 {len(event_data)}개")
            
        except Exception as e:
            print(f"전체 데이터 로드 실패, 샘플 데이터 사용: {e}")
            # 샘플 데이터로 폴백
            self._load_fallback_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _load_fallback_data(self, cursor):
        """폴백 샘플 데이터"""
        sample_restaurants = [
            (1, '늘채움', '전북 전주시 덕진구 덕진연못3길 6', '', '전북'),
            (2, '대림동삼거리먼지막순대국', '서울 영등포구 시흥대로 185길 11', '', '서울'),
            (3, '만석장', '서울 은평구 대서문길 43-10 2층', '', '서울'),
            (4, '선천집', '서울 종로구 인사동 14길5', '', '서울'),
            (5, '고려회관', '대전 중구 중앙로109번길 30, 2층', '', '대전')
        ]
        
        cursor.executemany('''
            INSERT INTO restaurants (id, name, address, phone, region)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_restaurants)
        
        sample_events = [
            (1, '홍보협력팀', '2023 연구개발특구 신년인사회', '연구개발특구진흥재단', '대덕특구', '대전 DCC', '기타', '#신년인사회', '2023-01-30', '2023-01-30'),
            (2, '연구개발특구진흥재단', '환경기후분야 국내외 R&BD 활성화를 위한 심포지움', '인천대학교 환경공학과', '과학벨트', '경원재 엠배서더(인천 송도)', 'ET,기타', '#환경', '2023-01-12', '2023-01-12')
        ]
        
        cursor.executemany('''
            INSERT INTO events (id, organization, event_name, host_organization, 
                               region, location, tech_category, hashtags, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_events)
    
    def get_restaurants_by_region(self, region: str) -> List[Dict[str, Any]]:
        """지역별 백년가게 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM restaurants WHERE region = ?
        ''', (region,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_restaurants_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """키워드로 백년가게 검색"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if keyword:
            cursor.execute('''
                SELECT * FROM restaurants 
                WHERE name LIKE ? OR address LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%'))
        else:
            cursor.execute('SELECT * FROM restaurants')
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_events_by_region(self, region: str) -> List[Dict[str, Any]]:
        """지역별 행사 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if region:
            cursor.execute('''
                SELECT * FROM events WHERE region = ?
            ''', (region,))
        else:
            cursor.execute('SELECT * FROM events')
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_events_by_location(self, location: str) -> List[Dict[str, Any]]:
        """장소별 행사 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM events WHERE location LIKE ?
        ''', (f'%{location}%',))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_nearby_restaurants(self, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """특정 장소 근처 백년가게 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 장소명에서 지역 키워드 추출
        location_keywords = self._extract_location_keywords(location)
        
        if not location_keywords:
            conn.close()
            return []
        
        # 키워드로 주소 검색
        query = ' OR '.join(['address LIKE ?' for _ in location_keywords])
        params = [f'%{keyword}%' for keyword in location_keywords]
        
        cursor.execute(f'''
            SELECT * FROM restaurants WHERE {query}
            LIMIT ?
        ''', params + [limit])
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
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
    
    def get_all_regions(self) -> List[str]:
        """모든 지역 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT region FROM restaurants WHERE region IS NOT NULL AND region != ""')
        regions = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return sorted(regions)