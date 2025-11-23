# models/transaction.py
from datetime import datetime
from .user import db  # reuse the same db from user.py
from .account import Account

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'deposit', 'withdraw', 'transfer_in', 'transfer_out'
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))

    account = db.relationship("Account", backref=db.backref("transactions", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "type": self.type,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
        }
