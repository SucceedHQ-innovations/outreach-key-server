import os
import secrets
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
# Note: In production you may want to set this to a persistent path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'access_keys.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models ---

class AccessKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key_value = db.Column(db.String(32), unique=True, nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    
    # Cumulative Stats
    total_leads_processed = db.Column(db.Integer, default=0)
    total_successes = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "key": self.key_value,
            "owner": self.owner_name,
            "total_successes": self.total_successes,
            "total_leads": self.total_leads_processed,
            "last_active": self.last_active.strftime("%Y-%m-%d %H:%M:%S") if self.last_active else "Never",
            "created_at": self.created_at.strftime("%Y-%m-%d")
        }


# --- Web Interface Routes ---

@app.route('/')
def admin_page():
    return render_template('index.html')


# --- REST API For Admin Dashboard ---

@app.route('/api/keys', methods=['GET'])
def list_keys():
    keys = AccessKey.query.all()
    total_leads = db.session.query(db.func.sum(AccessKey.total_leads_processed)).scalar() or 0
    total_success = db.session.query(db.func.sum(AccessKey.total_successes)).scalar() or 0
    
    return jsonify({
        "keys": [k.to_dict() for k in keys],
        "stats": {
            "total_leads": total_leads,
            "total_success": total_success
        }
    })

@app.route('/api/keys', methods=['POST'])
def create_key():
    data = request.json
    owner = data.get('owner', 'Unknown')
    
    # Generate a random 16-character alphanumeric key
    new_key_value = "JUDD-" + secrets.token_hex(6).upper()
    
    new_key = AccessKey(key_value=new_key_value, owner_name=owner)
    db.session.add(new_key)
    db.session.commit()
    
    return jsonify(new_key.to_dict()), 201

@app.route('/api/keys/<key_value>', methods=['DELETE'])
def delete_key(key_value):
    key = AccessKey.query.filter_by(key_value=key_value).first()
    if not key:
        return jsonify({"error": "Key not found"}), 404
        
    db.session.delete(key)
    db.session.commit()
    return jsonify({"success": True})


# --- API Endpoints for the Outreach Script ---

@app.route('/api/validate', methods=['POST'])
def validate_key():
    data = request.json
    key_val = data.get('access_key')
    
    if not key_val:
        return jsonify({"error": "Missing access key"}), 400
        
    access_key = AccessKey.query.filter_by(key_value=key_val).first()
    
    if not access_key:
        return jsonify({"error": "Invalid access key"}), 403

    # Update last active timestamp
    access_key.last_active = datetime.utcnow()
    db.session.commit()

    return jsonify({"status": "authorized", "owner": access_key.owner_name})

@app.route('/api/report', methods=['POST'])
def report_stats():
    data = request.json
    key_val = data.get('access_key')
    
    access_key = AccessKey.query.filter_by(key_value=key_val).first()
    if not access_key:
        return jsonify({"error": "Authorization failed"}), 403
        
    # Update cumulative stats based on report payload
    added_leads = data.get('total', 1) # Assumes 1 if not specified
    added_success = 1 if data.get('status') == 'SUCCESS' else 0
    
    # If the script sends batch reports, process them
    if 'failed' in data or 'success' in data:
         added_success = data.get('success', 0)
         added_leads = data.get('success', 0) + data.get('failed', 0) + data.get('skipped', 0)
         
    access_key.total_successes += added_success
    access_key.total_leads_processed += added_leads
    access_key.last_active = datetime.utcnow()
    
    db.session.commit()
    return jsonify({"status": "received"})


# --- Internal Database Init ---

def init_db():
    with app.app_context():
        db.create_all()
        # Create a test key if none exists
        if not AccessKey.query.first():
            test_key = AccessKey(
                key_value="JUDD-MASTER-KEY",
                owner_name="Admin"
            )
            db.session.add(test_key)
            db.session.commit()
            print("Database initialized with JUDD-MASTER-KEY")

if __name__ == '__main__':
    init_db()
    
    # Check if a port is provided in the environment (Render/Heroku/etc)
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 to enable external access
    app.run(host='0.0.0.0', port=port, debug=False)
