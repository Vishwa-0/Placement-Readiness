# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pickle
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')  # Suppress warnings in production

app = Flask(__name__)
app.secret_key = 'vynox-secret-key'  # Change this for production

# Try to load the trained model, fallback to dummy model if not found
try:
    with open('PRS.pkl', 'rb') as f:
        model = pickle.load(f)
    print("✓ ML model loaded successfully")
except Exception as e:
    print(f"⚠ Warning: Could not load PRS.pkl: {e}")
    print("⚠ Using dummy model for testing")
    # Create a simple dummy model
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(random_state=42)
    # Train on minimal dummy data
    X_dummy = np.array([[5, 50, 3, 5, 1] for _ in range(10)])
    y_dummy = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    model.fit(X_dummy, y_dummy)

# Domain information - Using numerical keys as your model expects
DOMAINS = {
    '1': {
        'name': 'Web Development',
        'skills': ['HTML/CSS', 'JavaScript', 'React/Vue/Angular', 'Node.js/Django', 'Database Management'],
        'description': 'Build modern web applications and services',
        'levels': {
            'beginner': 'Focus on HTML/CSS and basic JavaScript concepts',
            'intermediate': 'Learn frameworks like React and build full-stack applications',
            'advanced': 'Master advanced concepts like WebSockets, PWA, and DevOps'
        }
    },
    '2': {
        'name': 'Data Science',
        'skills': ['Python', 'Statistics', 'Machine Learning', 'Data Visualization', 'SQL'],
        'description': 'Analyze data and build predictive models',
        'levels': {
            'beginner': 'Start with Python programming and basic statistics',
            'intermediate': 'Learn machine learning algorithms and data preprocessing',
            'advanced': 'Master deep learning and big data technologies'
        }
    },
    '3': {
        'name': 'Mobile Development',
        'skills': ['Java/Kotlin', 'Swift', 'React Native/Flutter', 'REST APIs', 'Mobile UI/UX'],
        'description': 'Create applications for iOS and Android',
        'levels': {
            'beginner': 'Learn basics of Android/iOS development or cross-platform frameworks',
            'intermediate': 'Build complete mobile apps with backend integration',
            'advanced': 'Master performance optimization and native features'
        }
    },
    '4': {
        'name': 'Cybersecurity',
        'skills': ['Networking', 'Cryptography', 'Penetration Testing', 'Security Tools', 'Ethical Hacking'],
        'description': 'Protect systems and networks from cyber threats',
        'levels': {
            'beginner': 'Learn networking basics and Linux fundamentals',
            'intermediate': 'Study penetration testing methodologies and tools',
            'advanced': 'Master advanced exploitation techniques and defense strategies'
        }
    }
}

# Project suggestions based on readiness level
PROJECT_SUGGESTIONS = {
    '0': {  # Not Ready
        '1': ['To-Do List App', 'Personal Portfolio Website', 'Calculator App', 'Weather App', 'Blog Website'],
        '2': ['Data Analysis with Titanic Dataset', 'House Price Prediction', 'Iris Classification', 'Sales Dashboard'],
        '3': ['BMI Calculator', 'Notes App', 'Currency Converter', 'Flashlight App'],
        '4': ['Password Strength Checker', 'Network Scanner', 'Basic Encryption Tool', 'File Integrity Checker']
    },
    '1': {  # Ready
        '1': ['E-commerce Platform', 'Real-time Chat App', 'Project Management Tool', 'Social Media Dashboard', 'Booking System'],
        '2': ['Sentiment Analysis System', 'Recommendation Engine', 'Stock Prediction Model', 'Customer Churn Prediction'],
        '3': ['Food Delivery App', 'Fitness Tracker', 'E-commerce Mobile App', 'Social Media App'],
        '4': ['Vulnerability Scanner', 'Intrusion Detection System', 'Security Dashboard', 'Password Manager']
    }
}

# Learning resources for each domain
LEARNING_RESOURCES = {
    '1': ['MDN Web Docs', 'freeCodeCamp', 'W3Schools', 'Frontend Masters', 'Codecademy'],
    '2': ['Kaggle', 'Coursera ML Course', 'Fast.ai', 'DataCamp', 'Towards Data Science'],
    '3': ['Android Developers', 'iOS Dev Center', 'Flutter Docs', 'React Native Docs', 'Raywenderlich'],
    '4': ['Cybrary', 'HackTheBox', 'TryHackMe', 'OWASP', 'SecurityTube']
}

def get_level_description(prediction):
    """Get level description based on prediction"""
    if prediction == 0:
        return {
            'level': 'Beginner',
            'description': 'You need to improve your skills in key areas. Focus on building projects and solving problems.',
            'color': 'warning',
            'readiness': 'Not Placement Ready',
            'icon': 'fas fa-seedling'
        }
    else:
        return {
            'level': 'Advanced',
            'description': 'You have strong skills for placement. Keep enhancing your expertise and portfolio.',
            'color': 'success',
            'readiness': 'Placement Ready',
            'icon': 'fas fa-trophy'
        }

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html', domains=DOMAINS)

@app.route('/about')
def about():
    """About page"""
    team_members = [
        {'name': 'Swathi', 'role': 'Backend Developer', 'skills': 'Python, Flask, Database'},
        {'name': 'Santhosh', 'role': 'ML Engineer', 'skills': 'Machine Learning, AI, Data Science'},
        {'name': 'Vishwa', 'role': 'Frontend Developer', 'skills': 'HTML/CSS, JavaScript, React'}
    ]
    return render_template('about.html', team=team_members)

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    """Assessment page"""
    if request.method == 'POST':
        try:
            # Get form data with defaults and validation
            dsa_level = int(request.form.get('dsa_level', 5))
            problem_count = int(request.form.get('problem_count', 50))
            project_count = int(request.form.get('project_count', 3))
            github_quality = int(request.form.get('github_quality', 5))
            domain_focus = request.form.get('domain_focus', '1')
            
            # Validate inputs
            dsa_level = max(1, min(10, dsa_level))
            problem_count = max(0, min(500, problem_count))  # Increased max
            project_count = max(0, min(50, project_count))   # Increased max
            github_quality = max(1, min(10, github_quality))
            
            # Ensure domain is valid
            if domain_focus not in DOMAINS:
                domain_focus = '1'
            
            print(f"Making prediction with: {dsa_level}, {problem_count}, {project_count}, {github_quality}, {domain_focus}")
            
            # Prepare input for prediction
            # Note: domain_focus should be converted to int since your model was trained with numerical values
            input_data = [[
                dsa_level, 
                problem_count, 
                project_count, 
                github_quality, 
                int(domain_focus)  # Convert to int
            ]]
            
            # Make prediction
            prediction = model.predict(input_data)[0]
            print(f"Prediction result: {prediction}")
            
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
                'domain_name': DOMAINS[domain_focus]['name']
            }
            
            return redirect(url_for('results'))
            
        except Exception as e:
            print(f"Error during assessment: {e}")
            return render_template('assessment.html', 
                                 domains=DOMAINS, 
                                 error="Please check your inputs and try again.")
    
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
    suggestions = PROJECT_SUGGESTIONS.get(str(prediction), {}).get(domain_key, [])
    resources = LEARNING_RESOURCES.get(domain_key, [])
    domain_info = DOMAINS.get(domain_key, {'name': 'Unknown', 'skills': [], 'description': ''})
    
    return render_template('results.html',
                         assessment_data=assessment_data,
                         suggestions=suggestions[:5],  # Limit to 5 suggestions
                         resources=resources[:5],      # Limit to 5 resources
                         domain=domain_info,
                         domain_key=domain_key)

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'assessment_data' not in session:
        return redirect(url_for('assessment'))
    
    assessment_data = session['assessment_data']
    
    # Calculate skill percentages
    max_values = {
        'dsa_level': 10, 
        'problem_count': 500,  # Updated max
        'project_count': 50,   # Updated max
        'github_quality': 10
    }
    
    skill_data = {}
    for key in ['dsa_level', 'problem_count', 'project_count', 'github_quality']:
        max_val = max_values[key]
        current = assessment_data[key]
        percentage = min(100, int((current / max_val) * 100))
        skill_data[key] = {
            'value': current,
            'percentage': percentage,
            'max': max_val,
            'label': key.replace('_', ' ').title()
        }
    
    # Calculate overall score
    overall_score = (
        skill_data['dsa_level']['percentage'] * 0.3 +
        skill_data['problem_count']['percentage'] * 0.25 +
        skill_data['project_count']['percentage'] * 0.25 +
        skill_data['github_quality']['percentage'] * 0.2
    )
    
    return render_template('dashboard.html',
                         assessment_data=assessment_data,
                         skill_data=skill_data,
                         overall_score=int(overall_score))

@app.route('/projects')
def projects():
    """Project suggestions page"""
    if 'assessment_data' not in session:
        return redirect(url_for('assessment'))
    
    assessment_data = session['assessment_data']
    domain_key = assessment_data['domain_focus']
    prediction = assessment_data['prediction']
    
    suggestions = PROJECT_SUGGESTIONS.get(str(prediction), {}).get(domain_key, [])
    resources = LEARNING_RESOURCES.get(domain_key, [])
    
    return render_template('projects.html',
                         suggestions=suggestions,
                         resources=resources,
                         domain=DOMAINS.get(domain_key, {'name': 'Unknown', 'skills': []}),
                         assessment_data=assessment_data)

@app.route('/reset')
def reset():
    """Reset session and start over"""
    session.clear()
    return redirect(url_for('assessment'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'service': 'placement-readiness'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
