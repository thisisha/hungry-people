import os
from functools import wraps
from flask import jsonify, request

class FeatureFlags:
    """Feature Flag 관리 클래스"""
    
    @staticmethod
    def is_budget_ledger_enabled() -> bool:
        """예산 관리 기능 활성화 여부 확인"""
        return os.environ.get('BUDGET_LEDGER_ENABLED', 'false').lower() == 'true'
    
    @staticmethod
    def require_budget_ledger(f):
        """예산 관리 기능이 활성화되어야만 접근 가능한 데코레이터"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not FeatureFlags.is_budget_ledger_enabled():
                return jsonify({
                    'success': False,
                    'error': 'Budget ledger feature is not enabled'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def get_feature_status() -> dict:
        """모든 Feature Flag 상태 반환"""
        return {
            'budget_ledger_enabled': FeatureFlags.is_budget_ledger_enabled()
        }
