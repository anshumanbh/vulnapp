from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from profile_routes import profile
from database import init_db, get_db
from auth import login_required, admin_required
import hashlib

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Vulnerable: Hard-coded secret key
app.register_blueprint(profile)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if user and user['password'] == hashlib.md5(password.encode()).hexdigest():
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    users = db.execute('SELECT id, username, role FROM users').fetchall()
    return render_template('dashboard.html', users=users, current_role=session['role'])

@app.route('/api/user/<int:user_id>')
@login_required
def get_user_details(user_id):
    # Vulnerable: No authorization check for user_id
    db = get_db()
    user = db.execute(
        'SELECT id, username, role, email, phone, address FROM users WHERE id = ?', 
        (user_id,)
    ).fetchone()
    
    if user:
        return jsonify({
            "id": user['id'],
            "username": user['username'],
            "role": user['role'],
            "email": user['email'],
            "phone": user['phone'],
            "address": user['address']
        })
    return jsonify({"error": "User not found"}), 404

@app.route('/update_role', methods=['POST'])
@login_required  # Vulnerable: Missing admin check
def update_role():
    user_id = request.form.get('user_id')
    new_role = request.form.get('role')
    
    db = get_db()
    db.execute(
        'UPDATE users SET role = ? WHERE id = ?',
        (new_role, user_id)
    )
    db.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)  # Vulnerable: Debug mode enabled in production
