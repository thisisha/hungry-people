import json
from models.budget_models import db, PolicyRule

def seed_policy_rules():
    """정책 규칙 시드 데이터 추가"""
    
    # 기존 데이터 삭제
    PolicyRule.query.delete()
    
    policy_rules = [
        {
            'category': '다과비',
            'rule_text': '다과비는 카페, 베이커리, 디저트 전문점에서만 사용 가능',
            'required_receipt_types': json.dumps(['card_slip', 'tax_invoice']),
            'allowed_business_types': json.dumps(['카페', '베이커리', '디저트', '커피전문점']),
            'notes': '카드전표 또는 세금계산서 필수'
        },
        {
            'category': '회의비',
            'rule_text': '회의비는 조용한 환경의 업소에서 사용 가능',
            'required_receipt_types': json.dumps(['card_slip', 'tax_invoice']),
            'allowed_business_types': json.dumps(['한식', '중식', '일식', '양식', '퓨전']),
            'notes': '개인룸 보유 또는 조용한 환경 필요'
        },
        {
            'category': '교통비',
            'rule_text': '교통비는 대중교통, 택시, 주차비 등에 사용',
            'required_receipt_types': json.dumps(['card_slip', 'tax_invoice', 'none']),
            'allowed_business_types': json.dumps(['교통', '주차', '택시']),
            'notes': '교통 관련 비용만 인정'
        },
        {
            'category': '식비',
            'rule_text': '식비는 일반 음식점에서 사용 가능',
            'required_receipt_types': json.dumps(['card_slip', 'tax_invoice']),
            'allowed_business_types': json.dumps(['한식', '중식', '일식', '양식', '퓨전', '패스트푸드']),
            'notes': '음식점에서의 식사 비용'
        }
    ]
    
    for rule_data in policy_rules:
        rule = PolicyRule(**rule_data)
        db.session.add(rule)
    
    db.session.commit()
    print(f"정책 규칙 {len(policy_rules)}개가 추가되었습니다.")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        seed_policy_rules()
