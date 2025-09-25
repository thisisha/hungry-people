import sqlite3
import os
from typing import List, Dict, Any

class RestaurantDataEnhancer:
    """업소 데이터 확장 클래스"""
    
    def __init__(self, db_path='hungry_people.db'):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', db_path)
    
    def enhance_restaurant_data(self):
        """업소 데이터에 정책 규칙 매칭 필드 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 새로운 컬럼 추가
        try:
            cursor.execute('ALTER TABLE restaurants ADD COLUMN business_type TEXT')
            cursor.execute('ALTER TABLE restaurants ADD COLUMN has_private_room INTEGER DEFAULT 0')
            cursor.execute('ALTER TABLE restaurants ADD COLUMN noise_level TEXT DEFAULT "mid"')
            cursor.execute('ALTER TABLE restaurants ADD COLUMN max_party_size INTEGER DEFAULT 4')
            cursor.execute('ALTER TABLE restaurants ADD COLUMN tax_invoice_supported INTEGER DEFAULT 0')
            cursor.execute('ALTER TABLE restaurants ADD COLUMN card_payment_supported INTEGER DEFAULT 1')
            print("업소 테이블에 새로운 컬럼이 추가되었습니다.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("컬럼이 이미 존재합니다.")
            else:
                print(f"컬럼 추가 오류: {e}")
        
        # 업소 데이터 분류 및 태그 추가
        self._classify_restaurants(cursor)
        
        conn.commit()
        conn.close()
        print("업소 데이터 확장이 완료되었습니다.")
    
    def _classify_restaurants(self, cursor):
        """업소명과 주소를 기반으로 업종 분류"""
        
        # 업종 분류 키워드
        business_keywords = {
            '카페': ['카페', '커피', '스타벅스', '투썸', '이디야', '커피빈', '카페베네'],
            '베이커리': ['베이커리', '빵집', '제과', '제빵', '도넛', '케이크'],
            '디저트': ['디저트', '아이스크림', '젤라토', '마카롱', '타르트'],
            '한식': ['한식', '김치찌개', '된장찌개', '비빔밥', '불고기', '삼겹살', '갈비'],
            '중식': ['중식', '짜장면', '짬뽕', '탕수육', '중화요리', '만두'],
            '일식': ['일식', '초밥', '라멘', '우동', '돈카츠', '회'],
            '양식': ['양식', '스테이크', '파스타', '피자', '햄버거', '샐러드'],
            '퓨전': ['퓨전', '모던', '크리에이티브'],
            '패스트푸드': ['맥도날드', '버거킹', '롯데리아', 'KFC', '서브웨이']
        }
        
        # 개인룸 보유 키워드
        private_room_keywords = ['룸', '방', '개인실', 'VIP', '단체실', '회의실']
        
        # 조용한 환경 키워드
        quiet_keywords = ['조용', '한적', '아늑', '편안', '고요']
        
        # 업소 데이터 조회 및 업데이트
        cursor.execute('SELECT id, name, address FROM restaurants')
        restaurants = cursor.fetchall()
        
        for restaurant_id, name, address in restaurants:
            business_type = self._classify_business_type(name, business_keywords)
            has_private_room = 1 if any(keyword in name for keyword in private_room_keywords) else 0
            noise_level = 'low' if any(keyword in name for keyword in quiet_keywords) else 'mid'
            tax_invoice_supported = 1  # 백년가게는 대부분 세금계산서 발행 가능
            
            cursor.execute('''
                UPDATE restaurants 
                SET business_type = ?, has_private_room = ?, noise_level = ?, 
                    tax_invoice_supported = ?
                WHERE id = ?
            ''', (business_type, has_private_room, noise_level, tax_invoice_supported, restaurant_id))
        
        print(f"{len(restaurants)}개 업소의 데이터가 분류되었습니다.")
    
    def _classify_business_type(self, name: str, keywords: Dict[str, List[str]]) -> str:
        """업소명을 기반으로 업종 분류"""
        name_lower = name.lower()
        
        for business_type, keyword_list in keywords.items():
            if any(keyword in name_lower for keyword in keyword_list):
                return business_type
        
        return '기타'

if __name__ == '__main__':
    enhancer = RestaurantDataEnhancer()
    enhancer.enhance_restaurant_data()
