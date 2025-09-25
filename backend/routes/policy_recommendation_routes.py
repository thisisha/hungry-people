from flask import Blueprint, request, jsonify
from models.budget_models import db, PolicyRule, BudgetLine
from models.database import DatabaseManager
from services.feature_flags import FeatureFlags
from typing import List, Dict, Any
import sqlite3

policy_recommendation_bp = Blueprint('policy_recommendation', __name__, url_prefix='/api/policy-recommendations')

@policy_recommendation_bp.route('', methods=['GET'])
@FeatureFlags.require_budget_ledger
def get_policy_based_recommendations():
    """정책 규칙 기반 추천"""
    try:
        category = request.args.get('category')
        location = request.args.get('location', '')
        people = int(request.args.get('people', 4))
        budget_per_head = int(request.args.get('budget_per_head', 0))
        limit = int(request.args.get('limit', 10))
        
        if not category:
            return jsonify({
                'success': False,
                'error': 'category parameter is required'
            }), 400
        
        # 정책 규칙 조회
        policy_rule = PolicyRule.query.filter_by(category=category).first()
        if not policy_rule:
            return jsonify({
                'success': False,
                'error': f'No policy rule found for category: {category}'
            }), 404
        
        # 규칙에 맞는 업소 필터링
        filtered_restaurants = filter_restaurants_by_policy(
            policy_rule, location, people, budget_per_head, limit
        )
        
        return jsonify({
            'success': True,
            'data': {
                'category': category,
                'policy_rule': policy_rule.to_dict(),
                'restaurants': filtered_restaurants,
                'total_count': len(filtered_restaurants)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@policy_recommendation_bp.route('/budget-line/<int:budget_line_id>', methods=['GET'])
@FeatureFlags.require_budget_ledger
def get_budget_line_recommendations(budget_line_id):
    """비목 기반 추천"""
    try:
        budget_line = BudgetLine.query.get_or_404(budget_line_id)
        location = request.args.get('location', '')
        people = int(request.args.get('people', 4))
        limit = int(request.args.get('limit', 10))
        
        # 비목의 카테고리로 정책 규칙 조회
        policy_rule = PolicyRule.query.filter_by(category=budget_line.category).first()
        if not policy_rule:
            return jsonify({
                'success': False,
                'error': f'No policy rule found for category: {budget_line.category}'
            }), 404
        
        # 잔액 기반 1인당 예산 계산
        remaining_amount = budget_line.remaining_amount
        budget_per_head = remaining_amount // people if people > 0 else remaining_amount
        
        # 규칙에 맞는 업소 필터링
        filtered_restaurants = filter_restaurants_by_policy(
            policy_rule, location, people, budget_per_head, limit
        )
        
        return jsonify({
            'success': True,
            'data': {
                'budget_line': budget_line.to_dict(),
                'policy_rule': policy_rule.to_dict(),
                'budget_per_head': budget_per_head,
                'restaurants': filtered_restaurants,
                'total_count': len(filtered_restaurants)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def filter_restaurants_by_policy(
    policy_rule: PolicyRule, 
    location: str, 
    people: int, 
    budget_per_head: int, 
    limit: int
) -> List[Dict[str, Any]]:
    """정책 규칙에 따라 업소 필터링"""
    
    db_manager = DatabaseManager()
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # 기본 쿼리
    query = '''
        SELECT id, name, address, phone, region, business_type, 
               has_private_room, noise_level, max_party_size, 
               tax_invoice_supported, card_payment_supported
        FROM restaurants 
        WHERE 1=1
    '''
    params = []
    
    # 업종 필터링
    allowed_business_types = policy_rule.get_allowed_business_types()
    if allowed_business_types:
        placeholders = ','.join(['?' for _ in allowed_business_types])
        query += f' AND business_type IN ({placeholders})'
        params.extend(allowed_business_types)
    
    # 위치 필터링 (간단한 지역명 매칭)
    if location:
        query += ' AND (address LIKE ? OR region LIKE ?)'
        params.extend([f'%{location}%', f'%{location}%'])
    
    # 인원수 필터링
    if people > 0:
        query += ' AND max_party_size >= ?'
        params.append(people)
    
    # 정책별 특수 조건
    if policy_rule.category == '회의비':
        # 조용한 환경 또는 개인룸 필요
        query += ' AND (noise_level = "low" OR has_private_room = 1)'
    
    # 증빙 요구사항 확인
    required_receipt_types = policy_rule.get_required_receipt_types()
    if 'tax_invoice' in required_receipt_types:
        query += ' AND tax_invoice_supported = 1'
    if 'card_slip' in required_receipt_types:
        query += ' AND card_payment_supported = 1'
    
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
            'estimated_cost_per_person': estimate_cost_per_person(restaurant[5], budget_per_head)
        })
    
    conn.close()
    return result

def estimate_cost_per_person(business_type: str, budget_per_head: int) -> int:
    """업종별 예상 1인당 비용 추정"""
    cost_ranges = {
        '카페': 5000,
        '베이커리': 3000,
        '디저트': 8000,
        '한식': 15000,
        '중식': 12000,
        '일식': 20000,
        '양식': 25000,
        '퓨전': 30000,
        '패스트푸드': 8000,
        '기타': 15000
    }
    
    base_cost = cost_ranges.get(business_type, 15000)
    
    # 예산이 있으면 그에 맞춰 조정
    if budget_per_head > 0:
        return min(base_cost, budget_per_head)
    
    return base_cost
