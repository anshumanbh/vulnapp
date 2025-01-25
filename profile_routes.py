from flask import Blueprint, request, jsonify, session
from database import get_db
from auth import login_required

profile = Blueprint('profile', __name__)

@profile.route('/api/profile/<int:user_id>', methods=['GET'])
@login_required
def get_profile(user_id):
    # Vulnerable: No authorization check for user_id
    db = get_db()
    user = db.execute(
        'SELECT id, username, email, phone, address FROM users WHERE id = ?', 
        (user_id,)
    ).fetchone()
    
    if user:
        return jsonify({
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "phone": user['phone'],
            "address": user['address']
        })
    return jsonify({"error": "Profile not found"}), 404

@profile.route('/api/profile/<int:user_id>/update', methods=['POST'])
@login_required
def update_profile(user_id):
    # Vulnerable: No authorization check - any authenticated user can update any profile
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    
    db = get_db()
    db.execute(
        'UPDATE users SET email = ?, phone = ?, address = ? WHERE id = ?',
        (email, phone, address, user_id)
    )
    db.commit()
    
    return jsonify({"message": "Profile updated successfully"})
