# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pickle
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')  # Suppress warnings in production

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this for production

# Load the trained model
try:
    with open('PRS.pkl', 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("Warning: PRS.pkl not found. Using dummy model.")
    # Create a dummy model for testing
    from sklearn.linear_model import LogisticRegression
    import numpy as np
    model = LogisticRegression()
    # Train on dummy data
    X_dummy = np.array([[5, 50, 3, 5, 1] for _ in range(10)])
    y_dummy = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    model.fit(X_dummy, y_dummy)

# Domain information (same as before)
DOMAINS = {
    '1': {'name': 'Web Development', 'skills': ['HTML/CSS', 'JavaScript', 'React/Vue/Angular']},
    '2': {'name': 'Data Science', 'skills': ['Python', 'Statistics', 'Machine Learning']},
    '3': {'name': 'Mobile Development', 'skills': ['Java/Kotlin', 'Swift', 'React Native/Flutter']},
    '4': {'name': 'Cybersecurity', 'skills': ['Networking', 'Cryptography', 'Security Tools']}
}

# Project suggestions (same as before)
PROJECT_SUGGESTIONS = {
    'not_ready': {
        '1': ['To-Do List App', 'Personal Portfolio Website'],
        '2': ['Data Analysis with Titanic Dataset', 'House Price Prediction'],
        '3': ['BMI Calculator', 'Notes App'],
        '4': ['Password Strength Checker', 'Network Scanner']
    },
    'ready': {
        '1': ['E-commerce Platform', 'Real-time Chat App'],
        '2': ['Sentiment Analysis System', 'Recommendation Engine'],
        '3': ['Food Delivery App', 'Fitness Tracker'],
        '4': ['Vulnerability Scanner', 'Intrusion Detection System']
    }
}

def get_level_description(prediction):
    """Get level description based on prediction"""
    if prediction == 0:
        return {
            'level': 'Beginner',
            'description': 'You need to improve your skills in key areas',
            'color': 'danger',
            'readiness': 'Not Placement Ready'
        }
    else:
        return {
            'level': 'Advanced',
            'description': 'You have strong skills for placement',
            'color': 'success',
            'readiness': 'Placement Ready'
        }

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html', domains=DOMAINS)

@app.route('/about')
def about():
    """About page"""
    team_members = [
        {'name': 'Swathi', 'role': 'Backend Developer'},
        {'name': 'Santhosh', 'role': 'ML Engineer'},
        {'name': 'Vishwa', 'role': 'Frontend Developer'}
    ]
    return render_template('about.html', team=team_members)

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    """Assessment page"""
    if request.method == 'POST':
        try:
            # Get form data with defaults
            dsa_level = int(request.form.get('dsa_level', 5))
            problem_count = int(request.form.get('problem_count', 50))
            project_count = int(request.form.get('project_count', 3))
            github_quality = int(request.form.get('github_quality', 5))
            domain_focus = request.form.get('domain_focus', '1')
            
            # Validate inputs
            dsa_level = max(1, min(10, dsa_level))
            problem_count = max(0, min(200, problem_count))
            project_count = max(0, min(20, project_count))
            github_quality = max(1, min(10, github_quality))
            
            # Prepare input for prediction (as 2D array)
            input_data = [[dsa_level, problem_count, project_count, github_quality, int(domain_focus)]]
            
            # Make prediction
            prediction = model.predict(input_data)[0]
            
            # Get level info
            level_info = get_level_description(prediction)
            
            # Store in session
            session['assessment_data'] = {
                'dsa_level': dsa_level,
                'problem_count': problem_count,
                'project_count': project_count,
                'github_quality': github_quality,
                'domain_focus': domain_focus,
                'prediction': int(prediction),
                'level_info': level_info,
                'domain_name': DOMAINS.get(domain_focus, {}).get('name', 'Unknown')
            }
            
            return redirect(url_for('results'))
            
        except Exception as e:
            print(f"Error: {e}")
            return render_template('assessment.html', 
                                 domains=DOMAINS, 
                                 error="An error occurred. Please check your inputs.")
    
    return render_template('assessment.html', domains=DOMAINS)

@app.route('/results')
def results():
    """Results page"""
    if 'assessment_data' not in session:
        return redirect(url_for('assessment'))
    
    assessment_data = session['assessment_data']
    domain_key = assessment_data['domain_focus']
    prediction = assessment_data['prediction']
    
    # Get project suggestions
    readiness_key = 'ready' if prediction == 1 else 'not_ready'
    suggestions = PROJECT_SUGGESTIONS.get(readiness_key, {}).get(domain_key, [])
    
    domain_info = DOMAINS.get(domain_key, {'name': 'Unknown', 'skills': []})
    
    return render_template('results.html',
                         assessment_data=assessment_data,
                         suggestions=suggestions,
                         domain=domain_info,
                         domain_key=domain_key)

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'assessment_data' not in session:
        return redirect(url_for('assessment'))
    
    assessment_data = session['assessment_data']
    
    # Calculate skill percentages
    max_values = {'dsa_level': 10, 'problem_count': 200, 'project_count': 20, 'github_quality': 10}
    skill_data = {}
    
    for key in ['dsa_level', 'problem_count', 'project_count', 'github_quality']:
        max_val = max_values[key]
        current = assessment_data[key]
        percentage = min(100, int((current / max_val) * 100))
        skill_data[key] = {
            'value': current,
            'percentage': percentage,
            'label': key.replace('_', ' ').title()
        }
    
    return render_template('dashboard.html',
                         assessment_data=assessment_data,
                         skill_data=skill_data)

@app.route('/projects')
def projects():
    """Project suggestions page"""
    if 'assessment_data' not in session:
        return redirect(url_for('assessment'))
    
    assessment_data = session['assessment_data']
    domain_key = assessment_data['domain_focus']
    prediction = assessment_data['prediction']
    
    readiness_key = 'ready' if prediction == 1 else 'not_ready'
    suggestions = PROJECT_SUGGESTIONS.get(readiness_key, {}).get(domain_key, [])
    
    return render_template('projects.html',
                         suggestions=suggestions,
                         domain=DOMAINS.get(domain_key, {'name': 'Unknown', 'skills': []}),
                         assessment_data=assessment_data)

# Add error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
