from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User
from werkzeug.security import generate_password_hash
import logging

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Make the first registered user an admin (optional)
        if User.query.count() == 0:
            user.is_admin = True
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@auth_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate input
    if not all([username, email]):
        flash('Username and email are required', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Check if username is taken by someone else
    user_with_username = User.query.filter_by(username=username).first()
    if user_with_username and user_with_username.id != current_user.id:
        flash('Username already exists', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Check if email is taken by someone else
    user_with_email = User.query.filter_by(email=email).first()
    if user_with_email and user_with_email.id != current_user.id:
        flash('Email already registered', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Update user information
    current_user.username = username
    current_user.email = email
    
    # Update password if provided
    if current_password and new_password and confirm_password:
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.profile'))
        
        current_user.set_password(new_password)
    
    try:
        db.session.commit()
        flash('Profile updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Profile update error: {str(e)}")
        flash('An error occurred while updating your profile. Please try again.', 'danger')
    
    return redirect(url_for('auth.profile'))
