import random
import string
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.account import Account
from models.user import User, db
from models.transaction import Transaction


account_blueprint = Blueprint('account', __name__)

def generate_account_number():
    return ''.join(random.choices(string.digits, k=12))
    

@account_blueprint.route('/account/create', methods=['POST'])
@jwt_required()

def create_account():
    user_id = get_jwt_identity()
    data = request.get_json()

    account_type = data.get("account_type")
    if not account_type:
        return jsonify({"error": "Account type is required"}), 400

    # Generate 12-digit account number
    account_number = str(random.randint(10**11, 10**12 - 1))

    new_account = Account(
        account_number=account_number,
        account_type=account_type,
        user_id=user_id,
        balance=0.0
    )

    db.session.add(new_account)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "account_id": new_account.id,
        "account_number": new_account.account_number,
        "account_type": new_account.account_type
    }), 201



# -------------------------------
# 2. DEPOSIT
# -------------------------------
@account_blueprint.route('/account/deposit', methods=['POST'])
@jwt_required()
def deposit():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    account_id = data.get("account_id")
    raw_amount = data.get("amount")

    # Validate amount
    try:
        amount = float(raw_amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be a number"}), 400

    if amount <= 0:
        return jsonify({"error": "Deposit amount must be a positive number"}), 400

    account = Account.query.get(account_id)

    if not account:
        return jsonify({"error": "Account not found"}), 404

    # Ownership check
    if account.user_id != user_id:
        return jsonify({"error": "You do not own this account"}), 403

    # Apply deposit
    account.balance += amount

    # Log transaction
    txn = Transaction(
        account_id=account.id,
        type="deposit",
        amount=amount,
        description=f"Deposit to account {account.account_number}",
    )
    db.session.add(txn)

    db.session.commit()

    return jsonify({
        "message": "Deposit successful",
        "new_balance": account.balance
    })




# -------------------------------
# 3. WITHDRAW
# -------------------------------
@account_blueprint.route('/account/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    account_id = data.get("account_id")
    raw_amount = data.get("amount")

    # Validate amount
    try:
        amount = float(raw_amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be a number"}), 400

    if amount <= 0:
        return jsonify({"error": "Withdraw amount must be positive"}), 400

    account = Account.query.get(account_id)

    if not account:
        return jsonify({"error": "Account not found"}), 404

    # Ownership check
    if account.user_id != user_id:
        return jsonify({"error": "You do not own this account"}), 403

    if account.balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    # Apply withdrawal
    account.balance -= amount

    # Log transaction
    txn = Transaction(
        account_id=account.id,
        type="withdraw",
        amount=amount,
        description=f"Withdrawal from account {account.account_number}",
    )
    db.session.add(txn)

    db.session.commit()

    return jsonify({
        "message": "Withdraw successful",
        "new_balance": account.balance
    })



# -------------------------------
# 4. TRANSFER
# -------------------------------
@account_blueprint.route('/account/transfer', methods=['POST'])
@jwt_required()
def transfer():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    from_id = data.get("from_account")
    to_id = data.get("to_account")
    raw_amount = data.get("amount")

    # Validate amount
    try:
        amount = float(raw_amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be a number"}), 400

    if amount <= 0:
        return jsonify({"error": "Transfer amount must be positive"}), 400

    sender = Account.query.get(from_id)
    receiver = Account.query.get(to_id)

    if not sender or not receiver:
        return jsonify({"error": "One or both accounts do not exist"}), 404

    # Ownership check for sender
    if sender.user_id != user_id:
        return jsonify({"error": "You do not own the sender account"}), 403

    # Prevent self-transfer
    if sender.id == receiver.id:
        return jsonify({"error": "Cannot transfer to the same account"}), 400

    if sender.balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    # Apply transfer
    sender.balance -= amount
    receiver.balance += amount

    # Log outgoing transaction
    txn_out = Transaction(
        account_id=sender.id,
        type="transfer_out",
        amount=amount,
        description=f"Transfer to account {receiver.account_number}",
    )

    # Log incoming transaction
    txn_in = Transaction(
        account_id=receiver.id,
        type="transfer_in",
        amount=amount,
        description=f"Transfer from account {sender.account_number}",
    )

    db.session.add(txn_out)
    db.session.add(txn_in)
    db.session.commit()

    return jsonify({
        "message": "Transfer successful",
        "sender_new_balance": sender.balance,
        "receiver_new_balance": receiver.balance
    })



# -------------------------------
# 5. BALANCE CHECK
# -------------------------------
@account_blueprint.route('/account/balance/<int:account_id>', methods=['GET'])
@jwt_required()
def balance(account_id):
    account = Account.query.get(account_id)

    if not account:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({"balance": account.balance})


@account_blueprint.route('/account/transactions/<int:account_id>', methods=['GET'])
@jwt_required()
def get_transactions(account_id):
    user_id = int(get_jwt_identity())

    account = Account.query.get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    # Ownership check
    if account.user_id != user_id:
        return jsonify({"error": "You do not own this account"}), 403

    transactions = (
        Transaction.query
        .filter_by(account_id=account_id)
        .order_by(Transaction.timestamp.desc())
        .all()
    )

    return jsonify({
        "account_id": account_id,
        "transactions": [t.to_dict() for t in transactions]
    })

@account_blueprint.route('/account/list', methods=['GET'])
@jwt_required()
def list_accounts():
    user_id = get_jwt_identity()
    accounts = Account.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "account_id": acc.id,
            "account_number": acc.account_number,
            "account_type": acc.account_type,
            "balance": acc.balance
        }
        for acc in accounts
    ])

