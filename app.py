import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from groq import Groq

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///upcycle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

app.secret_key = 'super_secret_key_change_this_later'

db = SQLAlchemy(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SITE_CONTEXT = """
You are the 'UpCycle Guide', the official AI assistant for UpCycle Connect.
Your mission is to help users turn waste into wealth and track their ecological impact.

### OUR WORKFLOW:
1. Registration: The essential first step where users join the mission by listing surplus materials (wood, plastic, metal, etc.).
2. Search: Accessing our real-time database to find specific upcycling resources nearby.
3. Dashboard: The command center for viewing the 'CO2 Impact Heatmap' and the 'Top Eco-Warriors' leaderboard.
4. Requests: The final step to claim materials and finalize carbon-saving transactions.

### LEADERBOARD & RANKING KNOWLEDGE:
- Top Eco-Warriors: You can identify who is currently in 1st place and their total CO2 offset.
- Personal Ranking: You can tell users their exact position on the leaderboard.
- Progress Tracking: You can calculate how many kilograms of CO2 are needed to climb to the next rank.

### RESPONSE GUIDELINES:
- Tone: Extremely encouraging, professional, and eco-conscious.
- Brevity: Strictly keep answers under 2 sentences.
- Personality: Use emojis like 🌱, ♻️, and 🏆 to keep it engaging.
"""

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")
        
        # Using Llama 3.3, the stable 2026 model on Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SITE_CONTEXT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        return {"reply": completion.choices[0].message.content}
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        # Groq's free tier is generous, but we still handle errors safely
        return {"reply": "My sensors are recalibrating. Please try again in a moment!"}, 500

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    image_filename = db.Column(db.String(300), nullable=True)
    registered_by = db.Column(db.String(200), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Available")

class RequestMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    sender_email = db.Column(db.String(200), nullable=False)
    owner_email = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    reason = db.Column(db.String(500), nullable=True)
    contact_details = db.Column(db.String(200), nullable=True) 
    date_requested = db.Column(db.DateTime, default=datetime.utcnow)

    material = db.relationship('Material', backref='requests')

@app.route("/", methods=['GET', 'POST'])
def upcycle_connect():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = user.email 
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid email or password")
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        c_password = request.form.get('c_password')
        if password != c_password:
            return render_template("register.html", error="Passwords do not match", name=name)
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Email already registered", name=name)
        new_user = User(name=name, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('upcycle_connect'))
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():

    CO2_FACTORS = {
        "Plastic": 1.8, "Metal": 4.5, "Glass": 0.9,
        "Wood": 2.5, "Textile": 3.5, "Paper": 1.2, "Other": 1.5
    }
    
    total_items_count = Material.query.count()
    active_users_count = User.query.count()

    impact_data = {cat: 0 for cat in CO2_FACTORS.keys()}
    total_co2_saved = 0 
    
    accepted_deals = db.session.query(RequestMaterial, Material).\
        join(Material, RequestMaterial.material_id == Material.id).\
        filter(RequestMaterial.status == "Accepted").all()

    for req, mat in accepted_deals:
        factor = CO2_FACTORS.get(mat.category, 1.5)
        try:
            qty = float(mat.quantity) if mat.quantity else 0
        except ValueError:
            qty = 0
            
        calculation = factor * qty
        total_co2_saved += calculation
        
        cat = mat.category if mat.category in impact_data else "Other"
        impact_data[cat] += calculation

    heatmap_labels = list(impact_data.keys())
    heatmap_values = list(impact_data.values())

    warriors_query = db.session.query(
        User.name,
        Material.category,
        func.sum(Material.quantity).label('total_qty')
    ).join(Material, User.email == Material.registered_by)\
     .join(RequestMaterial, Material.id == RequestMaterial.material_id)\
     .filter(RequestMaterial.status == 'Accepted')\
     .group_by(User.name, Material.category).all()

    warrior_results = {}
    for name, cat, qty in warriors_query:
        impact = qty * CO2_FACTORS.get(cat, 1.5)
        warrior_results[name] = warrior_results.get(name, 0) + impact

    top_warriors = sorted(
        [{'name': k, 'total_impact': v} for k, v in warrior_results.items()],
        key=lambda x: x['total_impact'],
        reverse=True
    )[:10]

    return render_template("dashboard.html", 
                           total_co2=total_co2_saved,
                           total_items=total_items_count,
                           active_users=active_users_count,
                           heatmap_labels=heatmap_labels, 
                           heatmap_values=heatmap_values,
                           top_warriors=top_warriors)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('upcycle_connect'))

@app.route("/material", methods=["GET", "POST"])
def material():
    if request.method == "POST":
        lat_raw = request.form.get("latitude")
        lng_raw = request.form.get("longitude")
        file = request.files.get('image')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_material = Material(
            material_name=request.form.get("material_name"),
            category=request.form.get("category"),
            quantity=request.form.get("quantity"),
            unit=request.form.get("unit"),
            condition=request.form.get("condition"),
            location=request.form.get("location"),
            latitude=float(lat_raw) if lat_raw else None,
            longitude=float(lng_raw) if lng_raw else None,
            image_filename=filename,
            registered_by=session.get('email'),
            status="Available"
        )
        db.session.add(new_material)
        db.session.commit()
        return redirect(url_for("search"))
    return render_template("material.html")

@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q")
    category = request.args.get("category")
    condition = request.args.get("condition")
    searched = any([q, category, condition])
    materials = []
    if searched:
        query = Material.query.filter_by(status="Available")
        if q: query = query.filter(Material.material_name.ilike(f"%{q}%"))
        if category: query = query.filter_by(category=category)
        if condition: query = query.filter_by(condition=condition)
        results = query.all()
        materials = [{"id": m.id, "material_name": m.material_name, "category": m.category, "condition": m.condition, "location": m.location, "latitude": m.latitude, "longitude": m.longitude, "image": m.image_filename} for m in results]
    return render_template("search.html", materials=materials, searched=searched)

@app.route("/send_request/<int:material_id>", methods=["POST"])
def send_request(material_id):
    try:
        material = Material.query.get_or_404(material_id)
        current_user_email = session.get('email') 
        if not current_user_email:
            return {"error": "Please log in first"}, 401
        if material.registered_by == current_user_email:
            return {"error": "You cannot request your own material"}, 400

        new_req = RequestMaterial(
            material_id=material.id,
            sender_email=current_user_email,
            owner_email=material.registered_by,
            status="Pending"
        )
        db.session.add(new_req)
        db.session.commit()
        return {"message": "Request sent successfully!"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

@app.route("/respond_request/<int:request_id>", methods=["POST"])
def respond_request(request_id):
    req = RequestMaterial.query.get_or_404(request_id)
    
    new_status = request.form.get("status")
    req.status = new_status
    req.reason = request.form.get("reason")
    
    if new_status == "Accepted":
        material = Material.query.get(req.material_id)
        if material:
            material.status = "Accepted" 
    
    db.session.commit()
    return redirect(url_for('view_requests'))

@app.route("/requests")
def view_requests():
    user_email = session.get('email')
    if not user_email:
        return redirect(url_for('upcycle_connect'))
    
    incoming = RequestMaterial.query.filter_by(owner_email=user_email).all()
    outgoing = RequestMaterial.query.filter_by(sender_email=user_email).all()
    return render_template("requests.html", incoming=incoming, outgoing=outgoing)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)