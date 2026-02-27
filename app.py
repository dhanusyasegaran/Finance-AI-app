from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import pandas as pd
import plotly
import plotly.express as px
import json
from config import Config
from utils.classifier import classifier
from utils.predictor import predict_next_month_expense
from utils.insights import get_ai_suggestions
from utils.report_generator import generate_pdf_report

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    transactions = db.relationship('Transaction', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True)
    description = db.Column(db.String(255))
    amount = db.Column(db.Float)
    category = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monthly_limit = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('budget', uselist=False))

class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    target_amount = db.Column(db.Float)
    current_amount = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('goals', lazy='dynamic'))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Routes
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth_login.html', title='Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('auth_login.html', title='Sign In')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('auth_register.html', title='Register')

@app.route('/dashboard')
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    if not transactions:
        return render_template('dashboard.html', title='Dashboard', has_data=False)
    
    df = pd.DataFrame([{
        'date': t.date,
        'amount': t.amount,
        'category': t.category,
        'description': t.description
    } for t in transactions])
    
    # Analytics
    total_spending = df['amount'].sum()
    category_totals = df.groupby('category')['amount'].sum().to_dict()
    
    # Plotly Charts
    common_layout = {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': '#e2e8f0'},
        'xaxis': {'gridcolor': 'rgba(255,255,255,0.05)'},
        'yaxis': {'gridcolor': 'rgba(255,255,255,0.05)'}
    }

    fig_pie = px.pie(df, values='amount', names='category', 
                     title='Spending by Category',
                     color_discrete_sequence=px.colors.sequential.Electric)
    fig_pie.update_layout(common_layout)
    graph_pie = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)
    
    df_monthly = df.set_index('date').resample('M')['amount'].sum().reset_index()
    fig_bar = px.bar(df_monthly, x='date', y='amount', 
                     title='Monthly Spending Trend',
                     color_discrete_sequence=['#00f2ff'])
    fig_bar.update_layout(common_layout)
    graph_bar = json.dumps(fig_bar, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Prediction
    monthly_sums = df_monthly['amount'].tolist()
    next_month_pred = predict_next_month_expense(monthly_sums)
    
    # Budget Stats
    budget = Budget.query.filter_by(user_id=current_user.id).first()
    budget_limit = budget.monthly_limit if budget else 0.0
    
    # Calculate current month spending
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_month_spending = df[
        (df['date'].dt.month == current_month) & 
        (df['date'].dt.year == current_year)
    ]['amount'].sum()
    
    budget_percent = (current_month_spending / budget_limit * 100) if budget_limit > 0 else 0
    budget_remaining = max(0.0, float(budget_limit - current_month_spending))

    # Savings Goals
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
    
    # AI Suggestions
    suggestions = get_ai_suggestions(category_totals, total_spending, budget_limit, current_month_spending)
    
    return render_template('dashboard.html', title='Dashboard', 
                           has_data=True,
                           total_spending=total_spending,
                           graph_pie=graph_pie,
                           graph_bar=graph_bar,
                           prediction=next_month_pred,
                           suggestions=suggestions,
                           budget_limit=budget_limit,
                           budget_percent=budget_percent,
                           budget_remaining=budget_remaining,
                           goals=goals)

@app.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    amount = float(request.form.get('budget_amount', 0))
    budget = Budget.query.filter_by(user_id=current_user.id).first()
    if budget:
        budget.monthly_limit = amount
    else:
        budget = Budget(monthly_limit=amount, user_id=current_user.id)
        db.session.add(budget)
    db.session.commit()
    flash(f'Monthly budget updated to ₹{amount:,.2f}')
    return redirect(url_for('dashboard'))

@app.route('/transactions')
@login_required
def transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', title='Transactions', transactions=transactions)

@app.route('/delete_transaction/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    t = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(t)
    db.session.commit()
    flash('Transaction deleted successfully.')
    return redirect(url_for('transactions'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process CSV
            try:
                df = pd.read_csv(filepath)
                # Expecting columns: date, description, amount
                for _, row in df.iterrows():
                    cat = classifier.predict(row['description'])
                    date_val = pd.to_datetime(row['date'])
                    t = Transaction(
                        date=date_val,
                        description=row['description'],
                        amount=float(row['amount']),
                        category=cat,
                        user_id=current_user.id
                    )
                    db.session.add(t)
                db.session.commit()
                flash('File uploaded and processed successfully!')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
    return render_template('upload.html', title='Upload Statements')

@app.route('/goals')
@login_required
def goals():
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
    return render_template('goals.html', title='Savings Goals', goals=goals)

@app.route('/add_goal', methods=['POST'])
@login_required
def add_goal():
    name = request.form.get('name')
    target = float(request.form.get('target_amount', 0))
    current = float(request.form.get('current_amount', 0))
    goal = SavingsGoal(name=name, target_amount=target, current_amount=current, user_id=current_user.id)
    db.session.add(goal)
    db.session.commit()
    flash('Savings goal created!')
    return redirect(url_for('goals'))

@app.route('/update_goal/<int:id>', methods=['POST'])
@login_required
def update_goal(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    add_amount = float(request.form.get('add_amount', 0))
    goal.current_amount += add_amount
    db.session.commit()
    flash(f'Updated savings for {goal.name}.')
    return redirect(url_for('goals'))

@app.route('/delete_goal/<int:id>', methods=['POST'])
@login_required
def delete_goal(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Savings goal deleted.')
    return redirect(url_for('goals'))

@app.route('/download_report')
@login_required
def download_report():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    if not transactions:
        flash("No data available to generate report.")
        return redirect(url_for('dashboard'))
    
    # Calculate budget stats for suggestions
    budget = Budget.query.filter_by(user_id=current_user.id).first()
    budget_limit = budget.monthly_limit if budget else 0.0
    
    current_month_spending = 0
    if transactions:
        df_full = pd.DataFrame([{
            'date': t.date,
            'category': t.category,
            'amount': t.amount
        } for t in transactions])
        
        total_spending = df_full['amount'].sum()
        category_totals = df_full.groupby('category')['amount'].sum().to_dict()
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_month_spending = df_full[
            (df_full['date'].dt.month == current_month) & 
            (df_full['date'].dt.year == current_year)
        ]['amount'].sum()
    else:
        total_spending = 0
        category_totals = {}

    suggestions = get_ai_suggestions(category_totals, total_spending, budget_limit, current_month_spending)
    
    pdf_buffer = generate_pdf_report(current_user, total_spending, category_totals, suggestions)
    return send_file(pdf_buffer, as_attachment=True, download_name='Finance_Report.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
