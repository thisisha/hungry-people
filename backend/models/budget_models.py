from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Dict, Any
import json

db = SQLAlchemy()

class Budget(db.Model):
    """예산 모델"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)  # 원 단위 정수
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    budget_lines = db.relationship('BudgetLine', backref='budget', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'project_name': self.project_name,
            'fiscal_year': self.fiscal_year,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BudgetLine(db.Model):
    """예산 비목 모델"""
    __tablename__ = 'budget_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # 회의비, 다과비, 교통비 등
    allocated_amount = db.Column(db.Integer, nullable=False)  # 원 단위 정수
    spent_amount = db.Column(db.Integer, default=0)  # 원 단위 정수 (denormalized)
    rules_tag = db.Column(db.String(50), nullable=True)  # 정책 규칙 태그
    
    # 관계
    transactions = db.relationship('Transaction', backref='budget_line', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def remaining_amount(self) -> int:
        return self.allocated_amount - self.spent_amount
    
    @property
    def spending_rate(self) -> float:
        if self.allocated_amount == 0:
            return 0.0
        return (self.spent_amount / self.allocated_amount) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'budget_id': self.budget_id,
            'category': self.category,
            'allocated_amount': self.allocated_amount,
            'spent_amount': self.spent_amount,
            'remaining_amount': self.remaining_amount,
            'spending_rate': round(self.spending_rate, 2),
            'rules_tag': self.rules_tag
        }

class Transaction(db.Model):
    """거래 내역 모델"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    budget_line_id = db.Column(db.Integer, db.ForeignKey('budget_lines.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    vendor_name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # 원 단위 정수
    payment_method = db.Column(db.String(20), nullable=False)  # card, tax_invoice, cash
    receipt_type = db.Column(db.String(20), nullable=False)  # card_slip, tax_invoice, none
    memo = db.Column(db.Text, nullable=True)
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'budget_line_id': self.budget_line_id,
            'date': self.date.isoformat() if self.date else None,
            'vendor_name': self.vendor_name,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'receipt_type': self.receipt_type,
            'memo': self.memo,
            'is_valid': self.is_valid,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PolicyRule(db.Model):
    """정책 규칙 모델 (읽기 전용 카탈로그)"""
    __tablename__ = 'policy_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    rule_text = db.Column(db.Text, nullable=False)
    required_receipt_types = db.Column(db.Text, nullable=True)  # JSON 문자열
    allowed_business_types = db.Column(db.Text, nullable=True)  # JSON 문자열
    notes = db.Column(db.Text, nullable=True)
    
    def get_required_receipt_types(self) -> list:
        """JSON 문자열을 리스트로 변환"""
        if not self.required_receipt_types:
            return []
        try:
            return json.loads(self.required_receipt_types)
        except json.JSONDecodeError:
            return []
    
    def get_allowed_business_types(self) -> list:
        """JSON 문자열을 리스트로 변환"""
        if not self.allowed_business_types:
            return []
        try:
            return json.loads(self.allowed_business_types)
        except json.JSONDecodeError:
            return []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'category': self.category,
            'rule_text': self.rule_text,
            'required_receipt_types': self.get_required_receipt_types(),
            'allowed_business_types': self.get_allowed_business_types(),
            'notes': self.notes
        }
