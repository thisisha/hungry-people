from flask import Blueprint, request, jsonify
from models.budget_models import db, Budget, BudgetLine, Transaction, PolicyRule
from services.feature_flags import FeatureFlags
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError

budget_bp = Blueprint('budget', __name__, url_prefix='/api/budgets')

@budget_bp.route('', methods=['POST'])
@FeatureFlags.require_budget_ledger
def create_budget():
    """예산 생성"""
    try:
        data = request.get_json()
        
        # 유효성 검사
        if not data or not data.get('project_name') or not data.get('fiscal_year') or not data.get('total_amount'):
            return jsonify({
                'success': False,
                'error': 'project_name, fiscal_year, total_amount are required'
            }), 400
        
        if data['total_amount'] <= 0:
            return jsonify({
                'success': False,
                'error': 'total_amount must be positive'
            }), 400
        
        # 예산 생성
        budget = Budget(
            project_name=data['project_name'],
            fiscal_year=data['fiscal_year'],
            total_amount=data['total_amount']
        )
        
        db.session.add(budget)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': budget.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@budget_bp.route('/<int:budget_id>', methods=['GET'])
@FeatureFlags.require_budget_ledger
def get_budget(budget_id):
    """예산 조회"""
    try:
        budget = Budget.query.get_or_404(budget_id)
        
        # 비목별 집계 정보 포함
        budget_data = budget.to_dict()
        budget_data['budget_lines'] = [line.to_dict() for line in budget.budget_lines]
        
        return jsonify({
            'success': True,
            'data': budget_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@budget_bp.route('/<int:budget_id>/lines', methods=['POST'])
@FeatureFlags.require_budget_ledger
def create_budget_line(budget_id):
    """예산 비목 생성"""
    try:
        budget = Budget.query.get_or_404(budget_id)
        data = request.get_json()
        
        # 유효성 검사
        if not data or not data.get('category') or not data.get('allocated_amount'):
            return jsonify({
                'success': False,
                'error': 'category and allocated_amount are required'
            }), 400
        
        if data['allocated_amount'] <= 0:
            return jsonify({
                'success': False,
                'error': 'allocated_amount must be positive'
            }), 400
        
        # 비목 생성
        budget_line = BudgetLine(
            budget_id=budget_id,
            category=data['category'],
            allocated_amount=data['allocated_amount'],
            rules_tag=data.get('rules_tag')
        )
        
        db.session.add(budget_line)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': budget_line.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@budget_bp.route('/lines/<int:line_id>/transactions', methods=['POST'])
@FeatureFlags.require_budget_ledger
def create_transaction(line_id):
    """거래 내역 생성"""
    try:
        budget_line = BudgetLine.query.get_or_404(line_id)
        data = request.get_json()
        
        # 유효성 검사
        required_fields = ['vendor_name', 'amount', 'payment_method', 'receipt_type']
        if not data or not all(data.get(field) for field in required_fields):
            return jsonify({
                'success': False,
                'error': f'Required fields: {", ".join(required_fields)}'
            }), 400
        
        if data['amount'] <= 0:
            return jsonify({
                'success': False,
                'error': 'amount must be positive'
            }), 400
        
        # 초과 지출 검사
        new_spent_amount = budget_line.spent_amount + data['amount']
        if new_spent_amount > budget_line.allocated_amount:
            return jsonify({
                'success': False,
                'error': f'Transaction would exceed allocated amount. Remaining: {budget_line.remaining_amount}'
            }), 400
        
        # 거래 생성
        transaction = Transaction(
            budget_line_id=line_id,
            date=datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
            vendor_name=data['vendor_name'],
            amount=data['amount'],
            payment_method=data['payment_method'],
            receipt_type=data['receipt_type'],
            memo=data.get('memo')
        )
        
        db.session.add(transaction)
        
        # spent_amount 업데이트 (denormalized)
        budget_line.spent_amount = new_spent_amount
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': transaction.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid date format. Use YYYY-MM-DD'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@budget_bp.route('/lines/<int:line_id>/summary', methods=['GET'])
@FeatureFlags.require_budget_ledger
def get_line_summary(line_id):
    """비목별 집계 정보 조회"""
    try:
        budget_line = BudgetLine.query.get_or_404(line_id)
        
        # 거래 내역 조회
        transactions = Transaction.query.filter_by(budget_line_id=line_id, is_valid=True).all()
        
        summary = {
            'budget_line': budget_line.to_dict(),
            'transactions': [t.to_dict() for t in transactions],
            'transaction_count': len(transactions),
            'total_spent': budget_line.spent_amount,
            'remaining_amount': budget_line.remaining_amount,
            'spending_rate': round(budget_line.spending_rate, 2)
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@budget_bp.route('', methods=['GET'])
@FeatureFlags.require_budget_ledger
def list_budgets():
    """예산 목록 조회"""
    try:
        budgets = Budget.query.order_by(Budget.created_at.desc()).all()
        budget_list = []
        
        for budget in budgets:
            budget_data = budget.to_dict()
            # 각 예산의 비목별 집계 정보 포함
            budget_lines = BudgetLine.query.filter_by(budget_id=budget.id).all()
            budget_data['budget_lines'] = [line.to_dict() for line in budget_lines]
            budget_data['total_allocated'] = sum(line.allocated_amount for line in budget_lines)
            budget_data['total_spent'] = sum(line.spent_amount for line in budget_lines)
            budget_data['total_remaining'] = budget_data['total_allocated'] - budget_data['total_spent']
            budget_list.append(budget_data)
        
        return jsonify({
            'success': True,
            'data': budget_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@budget_bp.route('/feature-status', methods=['GET'])
def get_feature_status():
    """Feature Flag 상태 조회"""
    return jsonify({
        'success': True,
        'data': FeatureFlags.get_feature_status()
    })
