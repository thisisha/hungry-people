import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseManager:
    """SQLite 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "hungry_people.db"):
        self.db_path = db_path
        self.init_database()
    
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
        
        # 유관기관 일정 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY,
                start_date TEXT,
                end_date TEXT,
                title TEXT NOT NULL,
                created_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 지역별 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurants_region ON restaurants(region)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_region ON events(region)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_location ON events(location)')
        
        conn.commit()
        conn.close()
    
    def insert_restaurants(self, restaurants: List[Dict[str, Any]]):
        """백년가게 데이터 삽입"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM restaurants')  # 기존 데이터 삭제
        
        for restaurant in restaurants:
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
        
        conn.commit()
        conn.close()
    
    def insert_events(self, events: List[Dict[str, Any]]):
        """행사일정 데이터 삽입"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM events')  # 기존 데이터 삭제
        
        for event in events:
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
        
        conn.commit()
        conn.close()
    
    def insert_schedules(self, schedules: List[Dict[str, Any]]):
        """유관기관 일정 데이터 삽입"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM schedules')  # 기존 데이터 삭제
        
        for schedule in schedules:
            cursor.execute('''
                INSERT INTO schedules (id, start_date, end_date, title, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                schedule['id'],
                schedule['start_date'],
                schedule['end_date'],
                schedule['title'],
                schedule['created_date']
            ))
        
        conn.commit()
        conn.close()
    
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
        
        cursor.execute('''
            SELECT * FROM restaurants 
            WHERE name LIKE ? OR address LIKE ?
        ''', (f'%{keyword}%', f'%{keyword}%'))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_events_by_region(self, region: str) -> List[Dict[str, Any]]:
        """지역별 행사 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM events WHERE region = ?
        ''', (region,))
        
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
        """특정 장소 근처 백년가게 조회 (간단한 키워드 매칭)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 장소명에서 지역 키워드 추출하여 매칭
        location_keywords = self._extract_location_keywords(location)
        
        if not location_keywords:
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
        
        # 구/군 단위 키워드
        districts = ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
                    '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
                    '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구']
        
        for district in districts:
            if district in location:
                keywords.append(district)
        
        return keywords
    
    def get_all_regions(self) -> List[str]:
        """모든 지역 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT region FROM restaurants WHERE region IS NOT NULL AND region != ""')
        regions = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return sorted(regions)

if __name__ == "__main__":
    # 데이터베이스 초기화 및 데이터 로드 테스트
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.data_processor import DataProcessor
    
    db_manager = DatabaseManager()
    processor = DataProcessor()
    
    print("데이터베이스 초기화 완료")
    
    # 데이터 로드 및 삽입
    try:
        print("백년가게 데이터 로드 중...")
        restaurant_data = processor.load_restaurant_data('data/소상공인시장진흥공단_전국 백년가게 지정리스트 현황 정보_20250724.csv')
        db_manager.insert_restaurants(restaurant_data)
        print(f"백년가게 데이터 삽입 완료: {len(restaurant_data)}개")
        
        print("행사일정 데이터 로드 중...")
        event_data = processor.load_event_data('data/(재)연구개발특구진흥재단_행사일정_20250714.csv')
        db_manager.insert_events(event_data)
        print(f"행사일정 데이터 삽입 완료: {len(event_data)}개")
        
        print("유관기관 일정 데이터 로드 중...")
        schedule_data = processor.load_schedule_data('data/(재)연구개발특구진흥재단_재단 유관기관 일정_20250821.csv')
        db_manager.insert_schedules(schedule_data)
        print(f"유관기관 일정 데이터 삽입 완료: {len(schedule_data)}개")
        
        # 테스트 쿼리
        print("\n=== 테스트 쿼리 ===")
        regions = db_manager.get_all_regions()
        print(f"전체 지역: {regions}")
        
        seoul_restaurants = db_manager.get_restaurants_by_region('서울')
        print(f"서울 백년가게: {len(seoul_restaurants)}개")
        
        nearby_restaurants = db_manager.get_nearby_restaurants('대전 DCC')
        print(f"대전 DCC 근처 백년가게: {len(nearby_restaurants)}개")
        
    except Exception as e:
        print(f"데이터 로드 중 오류 발생: {e}")
