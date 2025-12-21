# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)
app.secret_key = 'vynox-secret-key'  # Change this for production

# Load the trained model
with open('PRS.pkl', 'rb') as f:
    model = pickle.load(f)

# Domain information
DOMAINS = {
    'web_dev': {
        'name': 'Web Development',
        'skills': ['HTML/CSS', 'JavaScript', 'React/Vue/Angular', 'Node.js/Python/Django', 'Database Management'],
        'levels': {
            'beginner': 'Focus on HTML/CSS and basic JavaScript',
            'intermediate': 'Learn React/Node.js and build full-stack applications',
            'advanced': 'Master advanced concepts like WebSockets, PWA, and DevOps'
        }
    },
    'data_science': {
        'name': 'Data Science',
        'skills': ['Python', 'Statistics', 'Machine Learning', 'Data Visualization', 'SQL'],
        'levels': {
            'beginner': 'Start with Python and basic statistics',
            'intermediate': 'Learn ML algorithms and data preprocessing',
            'advanced': 'Master deep learning and big data technologies'
        }
    },
    'mobile_dev': {
        'name': 'Mobile Development',
        'skills': ['Java/Kotlin', 'Swift', 'React Native/Flutter', 'REST APIs', 'Mobile UI/UX'],
        'levels': {
            'beginner': 'Learn basics of Android/iOS or cross-platform',
            'intermediate': 'Build complete apps with backend integration',
            'advanced': 'Master performance optimization and native features'
        }
    },
    'cybersecurity': {
        'name': 'Cybersecurity',
        'skills': ['Networking', 'Cryptography', 'Penetration Testing', 'Security Tools', 'Ethical Hacking'],
        'levels': {
            'beginner': 'Learn networking basics and Linux',
            'intermediate': 'Study penetration testing methodologies',
            'advanced': 'Master advanced exploitation and defense techniques'
        }
    }
}

# Project suggestions based on level
PROJECT_SUGGESTIONS = {
    'not_ready': {
        'web_dev': ['To-Do List App', 'Personal Portfolio Website', 'Calculator', 'Weather App'],
        'data_science': ['Data Analysis with Titanic Dataset', 'House Price Prediction', 'Iris Classification'],
        'mobile_dev': ['BMI Calculator', 'Notes App', 'Currency Converter'],
        'cybersecurity': ['Password Strength Checker', 'Network Scanner', 'Basic Encryption Tool']
    },
    'ready': {
        'web_dev': ['E-commerce Platform', 'Real-time Chat App', 'Project Management Tool', 'Social Media Dashboard'],
        'data_science': ['Sentiment Analysis System', 'Recommendation Engine', 'Stock Prediction Model'],
        'mobile_dev': ['Food Delivery App', 'Fitness Tracker', 'E-commerce Mobile App'],
        'cybersecurity': ['Vulnerability Scanner', 'Intrusion Detection System', 'Security Dashboard']
    }
}

def get_level_description(prediction, domain):
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
        # Get form data
        try:
            dsa_level = int(request.form.get('dsa_level', 0))
            problem_count = int(request.form.get('problem_count', 0))
            project_count = int(request.form.get('project_count', 0))
            github_quality = int(request.form.get('github_quality', 0))
            domain_focus = request.form.get('domain_focus', 'web_dev')
            
            # Make prediction
            prediction = model.predict([[dsa_level, problem_count, project_count, github_quality, domain_focus]])
            
            # Get level info
            level_info = get_level_description(prediction[0], domain_focus)
            
            # Store in session for dashboard
            session['assessment_data'] = {
                'dsa_level': dsa_level,
                'problem_count': problem_count,
                'project_count': project_count,
                'github_quality': github_quality,
                'domain_focus': domain_focus,
                'prediction': int(prediction[0]),
                'level_info': level_info,
                'domain_name': DOMAINS[domain_focus]['name']
            }
            
            # Get project suggestions
            readiness_key = 'ready' if prediction[0] == 1 else 'not_ready'
            suggestions = PROJECT_SUGGESTIONS[readiness_key].get(domain_focus, [])
            
            return render_template('results.html',
                                 prediction=prediction[0],
                                 level_info=level_info,
                                 suggestions=suggestions,
                                 domain=DOMAINS[domain_focus],
                                 domain_key=domain_focus)
            
        except Exception as e:
            return render_template('assessment.html', error=str(e))
    
    return render_template('assessment.html', domains=DOMAINS)

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
    suggestions = PROJECT_SUGGESTIONS[readiness_key].get(domain_key, [])
    
    # Get learning resources
    learning_resources = {
        'web_dev': ['MDN Web Docs', 'freeCodeCamp', 'W3Schools', 'Frontend Masters'],
        'data_science': ['Kaggle', 'Coursera ML Course', 'Fast.ai', 'DataCamp'],
        'mobile_dev': ['Android Developers', 'iOS Dev Center', 'Flutter Docs', 'React Native Docs'],
        'cybersecurity': ['Cybrary', 'HackTheBox', 'TryHackMe', 'OWASP']
    }
    
    return render_template('projects.html',
                         suggestions=suggestions,
                         domain=DOMAINS[domain_key],
                         resources=learning_resources.get(domain_key, []),
                         level_info=assessment_data['level_info'])

@app.route('/api/check-readiness', methods=['POST'])
def check_readiness():
    """API endpoint for AJAX readiness check"""
    try:
        data = request.json
        prediction = model.predict([[data['dsa_level'], data['problem_count'], 
                                   data['project_count'], data['github_quality'], 
                                   data['domain_focus']]])
        
        return jsonify({
            'prediction': int(prediction[0]),
            'readiness': 'Placement Ready' if prediction[0] == 1 else 'Not Placement Ready'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
