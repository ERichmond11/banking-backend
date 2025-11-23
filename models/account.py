from models.user import db

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), nullable=False, unique = True)
    account_type = db.Column(db.String(20), nullable=False)  # "chequing", "savings"
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "account_number": self.account_number,
            "account_type": self.account_type,
            "balance": self.balance
        }