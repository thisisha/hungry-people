from flask import Blueprint, request, jsonify
from models.database import DatabaseManager
from services.feature_flags import FeatureFlags
from typing import List, Dict, Any
import sqlite3
import re

event_recommendation_bp = Blueprint('event_recommendation', __name__, url_prefix='/api/event-recommendations')

@event_recommendation_bp.route('/near-event', methods=['GET'])
def get_near_event_recommendations():
    """행사장 근처 추천"""
    try:
        event_location = request.args.get('location', '')
        event_region = request.args.get('region', '')
        budget_category = request.args.get('category', '식비')
        people = int(request.args.get('people', 4))
        limit = int(request.args.get('limit', 10))
        
        if not event_location:
            return jsonify({
                'success': False,
                'error': 'location parameter is required'
            }), 400
        
        # 행사장 근처 업소 검색
        nearby_restaurants = find_nearby_restaurants(
            event_location, event_region, budget_category, people, limit
        )
        
        # 행사 정보도 함께 반환
        event_info = get_event_info(event_location, event_region)
        
        return jsonify({
            'success': True,
            'data': {
                'event_location': event_location,
                'event_region': event_region,
                'event_info': event_info,
                'nearby_restaurants': nearby_restaurants,
                'total_count': len(nearby_restaurants)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@event_recommendation_bp.route('/event/<int:event_id>', methods=['GET'])
def get_event_specific_recommendations(event_id):
    """특정 행사 기반 추천"""
    try:
        db_manager = DatabaseManager()
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # 행사 정보 조회
        cursor.execute('''
            SELECT id, event_name, location, region, start_date, end_date, 
                   host_organization, tech_category
            FROM events WHERE id = ?
        ''', (event_id,))
        
        event = cursor.fetchone()
        if not event:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        # 행사 정보 파싱
        event_data = {
            'id': event[0],
            'event_name': event[1],
            'location': event[2],
            'region': event[3],
            'start_date': event[4],
            'end_date': event[5],
            'host_organization': event[6],
            'tech_category': event[7]
        }
        
        # 행사장 근처 업소 검색
        nearby_restaurants = find_nearby_restaurants(
            event_data['location'], 
            event_data['region'], 
            '식비', 
            4, 
            15
        )
        
        # 행사 유형별 맞춤 추천
        tailored_recommendations = get_tailored_recommendations(
            event_data, nearby_restaurants
        )
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'event': event_data,
                'nearby_restaurants': nearby_restaurants,
                'tailored_recommendations': tailored_recommendations,
                'total_count': len(nearby_restaurants)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def find_nearby_restaurants(
    event_location: str, 
    event_region: str, 
    budget_category: str, 
    people: int, 
    limit: int
) -> List[Dict[str, Any]]:
    """행사장 근처 업소 검색"""
    
    db_manager = DatabaseManager()
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # 위치 키워드 추출
    location_keywords = extract_location_keywords(event_location)
    
    # 기본 쿼리
    query = '''
        SELECT id, name, address, phone, region, business_type, 
               has_private_room, noise_level, max_party_size, 
               tax_invoice_supported, card_payment_supported
        FROM restaurants 
        WHERE 1=1
    '''
    params = []
    
    # 지역 우선 매칭
    if event_region:
        query += ' AND region = ?'
        params.append(event_region)
    
    # 위치 키워드 매칭
    if location_keywords:
        location_conditions = []
        for keyword in location_keywords:
            location_conditions.append('address LIKE ?')
            params.append(f'%{keyword}%')
        
        if location_conditions:
            query += f' AND ({" OR ".join(location_conditions)})'
    
    # 인원수 필터링
    if people > 0:
        query += ' AND max_party_size >= ?'
        params.append(people)
    
    # 예산 카테고리별 필터링
    if budget_category == '회의비':
        query += ' AND (noise_level = "low" OR has_private_room = 1)'
    elif budget_category == '다과비':
        query += ' AND business_type IN ("카페", "베이커리", "디저트")'
    
    query += ' ORDER BY RANDOM() LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    restaurants = cursor.fetchall()
    
    # 결과 포맷팅
    result = []
    for restaurant in restaurants:
        result.append({
            'id': restaurant[0],
            'name': restaurant[1],
            'address': restaurant[2],
            'phone': restaurant[3],
            'region': restaurant[4],
            'business_type': restaurant[5],
            'has_private_room': bool(restaurant[6]),
            'noise_level': restaurant[7],
            'max_party_size': restaurant[8],
            'tax_invoice_supported': bool(restaurant[9]),
            'card_payment_supported': bool(restaurant[10]),
            'distance_estimate': estimate_distance(event_location, restaurant[2])
        })
    
    conn.close()
    return result

def extract_location_keywords(location: str) -> List[str]:
    """위치 문자열에서 키워드 추출"""
    if not location:
        return []
    
    # 괄호 안의 내용 제거
    location = re.sub(r'\([^)]*\)', '', location)
    
    # 쉼표로 분리
    parts = [part.strip() for part in location.split(',')]
    
    # 각 부분에서 주요 키워드 추출
    keywords = []
    for part in parts:
        # 구, 동, 건물명 등 추출
        if any(keyword in part for keyword in ['구', '동', '로', '길', '센터', '빌딩', '타워']):
            keywords.append(part)
        elif len(part) > 2:  # 2글자 이상인 경우만
            keywords.append(part)
    
    return keywords[:3]  # 최대 3개 키워드만 사용

def estimate_distance(location1: str, location2: str) -> str:
    """거리 추정 (간단한 텍스트 매칭 기반)"""
    if not location1 or not location2:
        return "거리 불명"
    
    # 같은 구/동이면 가까움
    if any(keyword in location2 for keyword in location1.split()):
        return "도보 5분 이내"
    
    # 같은 지역이면 중간
    if any(keyword in location2 for keyword in ['서울', '부산', '대구', '인천', '광주', '대전', '울산']):
        return "차량 10-20분"
    
    return "차량 20분 이상"

def get_event_info(location: str, region: str) -> Dict[str, Any]:
    """행사 정보 조회"""
    db_manager = DatabaseManager()
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # 해당 위치의 행사 정보 조회
    cursor.execute('''
        SELECT event_name, start_date, end_date, host_organization, tech_category
        FROM events 
        WHERE location LIKE ? OR region = ?
        ORDER BY start_date DESC
        LIMIT 1
    ''', (f'%{location}%', region))
    
    event = cursor.fetchone()
    conn.close()
    
    if event:
        return {
            'event_name': event[0],
            'start_date': event[1],
            'end_date': event[2],
            'host_organization': event[3],
            'tech_category': event[4]
        }
    
    return None

def get_tailored_recommendations(event_data: Dict, restaurants: List[Dict]) -> Dict[str, List[Dict]]:
    """행사 유형별 맞춤 추천"""
    
    recommendations = {
        'formal_meeting': [],
        'casual_networking': [],
        'quick_meal': []
    }
    
    for restaurant in restaurants:
        # 정식 회의용 (조용하고 개인룸 있는 곳)
        if restaurant['noise_level'] == 'low' or restaurant['has_private_room']:
            recommendations['formal_meeting'].append(restaurant)
        
        # 네트워킹용 (편안한 분위기)
        if restaurant['business_type'] in ['카페', '퓨전', '양식']:
            recommendations['casual_networking'].append(restaurant)
        
        # 빠른 식사용 (패스트푸드, 한식)
        if restaurant['business_type'] in ['패스트푸드', '한식', '중식']:
            recommendations['quick_meal'].append(restaurant)
    
    return recommendations
