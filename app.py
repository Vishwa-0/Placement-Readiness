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
        'skills': ['HTML/CSS', 'JavaScript', 'React/Vue/Angular', 'Node.js/Django', 'Database Management', 'REST APIs', 'Version Control'],
        'description': 'Build modern web applications and services with full-stack development expertise',
        'levels': {
            'beginner': 'Focus on HTML/CSS and basic JavaScript concepts',
            'intermediate': 'Learn frameworks like React and build full-stack applications',
            'advanced': 'Master advanced concepts like WebSockets, PWA, and DevOps'
        },
        'icon': 'fas fa-code',
        'color': '#8b5cf6'  # Violet
    },
    '2': {
        'name': 'Data Science',
        'skills': ['Python', 'Statistics', 'Machine Learning', 'Data Visualization', 'SQL', 'Pandas/Numpy', 'Deep Learning'],
        'description': 'Analyze data and build predictive models using AI and ML algorithms',
        'levels': {
            'beginner': 'Start with Python programming and basic statistics',
            'intermediate': 'Learn machine learning algorithms and data preprocessing',
            'advanced': 'Master deep learning and big data technologies'
        },
        'icon': 'fas fa-chart-line',
        'color': '#10b981'  # Emerald
    },
    '3': {
        'name': 'Mobile Development',
        'skills': ['Java/Kotlin', 'Swift', 'React Native/Flutter', 'REST APIs', 'Mobile UI/UX', 'Firebase', 'App Store Deployment'],
        'description': 'Create responsive and high-performance applications for iOS and Android platforms',
        'levels': {
            'beginner': 'Learn basics of Android/iOS development or cross-platform frameworks',
            'intermediate': 'Build complete mobile apps with backend integration',
            'advanced': 'Master performance optimization and native features'
        },
        'icon': 'fas fa-mobile-alt',
        'color': '#3b82f6'  # Blue
    },
    '4': {
        'name': 'Cybersecurity',
        'skills': ['Networking', 'Cryptography', 'Penetration Testing', 'Security Tools', 'Ethical Hacking', 'Risk Assessment', 'Incident Response'],
        'description': 'Protect systems and networks from cyber threats with advanced security measures',
        'levels': {
            'beginner': 'Learn networking basics and Linux fundamentals',
            'intermediate': 'Study penetration testing methodologies and tools',
            'advanced': 'Master advanced exploitation techniques and defense strategies'
        },
        'icon': 'fas fa-shield-alt',
        'color': '#ef4444'  # Red
    }
}

# Project suggestions based on readiness level
PROJECT_SUGGESTIONS = {
    '0': {  # Not Ready
        '1': [
            'Personal Portfolio Website',
            'To-Do List App with Local Storage',
            'Weather App with API Integration',
            'Simple Calculator',
            'Responsive Blog Website'
        ],
        '2': [
            'Data Analysis with Titanic Dataset',
            'House Price Prediction Model',
            'Iris Flower Classification',
            'Customer Segmentation Analysis',
            'Sales Dashboard Visualization'
        ],
        '3': [
            'BMI Calculator App',
            'Notes Taking App',
            'Currency Converter',
            'Flashlight/Torch App',
            'Simple Quiz App'
        ],
        '4': [
            'Password Strength Checker',
            'Basic Network Scanner',
            'File Integrity Checker',
            'Simple Encryption Tool',
            'Log Analyzer Tool'
        ]
    },
    '1': {  # Ready
        '1': [
            'E-commerce Platform with Payment Gateway',
            'Real-time Chat Application',
            'Project Management Dashboard',
            'Social Media Platform',
            'Online Booking System'
        ],
        '2': [
            'Sentiment Analysis System',
            'Recommendation Engine',
            'Stock Price Prediction Model',
            'Customer Churn Prediction',
            'Image Classification System'
        ],
        '3': [
            'Food Delivery Application',
            'Fitness Tracker with Health Data',
            'E-commerce Mobile App',
            'Social Media Mobile App',
            'Ride-Sharing Application'
        ],
        '4': [
            'Vulnerability Scanner Tool',
            'Intrusion Detection System',
            'Security Dashboard',
            'Password Manager with Encryption',
            'Network Monitoring System'
        ]
    }
}

# Learning resources for each domain
LEARNING_RESOURCES = {
    '1': [
        {'name': 'MDN Web Docs', 'url': 'https://developer.mozilla.org', 'type': 'Documentation'},
        {'name': 'freeCodeCamp', 'url': 'https://freecodecamp.org', 'type': 'Tutorials'},
        {'name': 'Frontend Masters', 'url': 'https://frontendmasters.com', 'type': 'Courses'},
        {'name': 'Codecademy Web Dev', 'url': 'https://codecademy.com', 'type': 'Interactive'},
        {'name': 'W3Schools', 'url': 'https://w3schools.com', 'type': 'Reference'}
    ],
    '2': [
        {'name': 'Kaggle Learn', 'url': 'https://kaggle.com/learn', 'type': 'Practice'},
        {'name': 'Coursera ML Course', 'url': 'https://coursera.org', 'type': 'Course'},
        {'name': 'Fast.ai', 'url': 'https://fast.ai', 'type': 'Practical AI'},
        {'name': 'DataCamp', 'url': 'https://datacamp.com', 'type': 'Interactive'},
        {'name': 'Towards Data Science', 'url': 'https://towardsdatascience.com', 'type': 'Articles'}
    ],
    '3': [
        {'name': 'Android Developers', 'url': 'https://developer.android.com', 'type': 'Documentation'},
        {'name': 'iOS Dev Center', 'url': 'https://developer.apple.com', 'type': 'Documentation'},
        {'name': 'Flutter Docs', 'url': 'https://flutter.dev', 'type': 'Framework'},
        {'name': 'React Native Docs', 'url': 'https://reactnative.dev', 'type': 'Framework'},
        {'name': 'Raywenderlich', 'url': 'https://raywenderlich.com', 'type': 'Tutorials'}
    ],
    '4': [
        {'name': 'Cybrary', 'url': 'https://cybrary.it', 'type': 'Courses'},
        {'name': 'HackTheBox', 'url': 'https://hackthebox.com', 'type': 'Practice'},
        {'name': 'TryHackMe', 'url': 'https://tryhackme.com', 'type': 'Learning'},
        {'name': 'OWASP', 'url': 'https://owasp.org', 'type': 'Security'},
        {'name': 'SecurityTube', 'url': 'https://securitytube.net', 'type': 'Videos'}
    ]
}

# Company information
COMPANY_INFO = {
    'name': 'VYNOX',
    'tagline': 'Placement Readiness Assessment System',
    'description': 'AI-powered platform for skill assessment and career guidance',
    'contact_email': 'contact@vynox.com',
    'contact_phone': '+1 (234) 567-8900',
    'address': 'Tech Innovation Hub, Bangalore, India'
}

def get_level_description(prediction):
    """Get level description based on prediction"""
    if prediction == 0:
        return {
            'level': 'Beginner',
            'description': 'You need to focus on building foundational skills. Start with basic projects and gradually increase complexity.',
            'color': 'warning',
            'bg_color': '#f59e0b',
            'readiness': 'Not Placement Ready',
            'icon': 'fas fa-seedling',
            'advice': 'Focus on completing at least 100 coding problems and 2-3 basic projects in your chosen domain.'
        }
    else:
        return {
            'level': 'Advanced',
            'description': 'You have strong technical skills. Focus on advanced projects and interview preparation.',
            'color': 'success',
            'bg_color': '#10b981',
            'readiness': 'Placement Ready',
            'icon': 'fas fa-trophy',
            'advice': 'Prepare for technical interviews and work on complex projects to showcase your expertise.'
        }

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html', 
                         domains=DOMAINS, 
                         company=COMPANY_INFO)

@app.route('/about')
def about():
    """About page"""
    team_members = [
        {
            'name': 'Swathi',
            'role': 'Backend Developer & System Architect',
            'skills': 'Python, Flask, Database Design, API Development',
            'bio': 'Specializes in backend systems and database architecture. Ensures system reliability and scalability.',
            'avatar': 'SW',
            'color': '#8b5cf6'
        },
        {
            'name': 'Santhosh',
            'role': 'ML Engineer & Data Scientist',
            'skills': 'Machine Learning, AI Algorithms, Data Analysis, Predictive Modeling',
            'bio': 'Expert in machine learning algorithms and data analysis. Designs the predictive models powering our assessments.',
            'avatar': 'SA',
            'color': '#10b981'
        },
        {
            'name': 'Vishwa',
            'role': 'Frontend Developer & UI/UX Designer',
            'skills': 'HTML/CSS, JavaScript, React, User Experience Design',
            'bio': 'Creates intuitive user interfaces and seamless experiences. Focuses on making complex data easy to understand.',
            'avatar': 'VI',
            'color': '#3b82f6'
        }
    ]
    return render_template('about.html', 
                         team=team_members, 
                         company=COMPANY_INFO)

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
            problem_count = max(0, min(500, problem_count))
            project_count = max(0, min(50, project_count))
            github_quality = max(1, min(10, github_quality))
            
            # Ensure domain is valid
            if domain_focus not in DOMAINS:
                domain_focus = '1'
            
            print(f"Making prediction with: {dsa_level}, {problem_count}, {project_count}, {github_quality}, {domain_focus}")
            
            # Prepare input for prediction
            input_data = [[
                dsa_level, 
                problem_count, 
                project_count, 
                github_quality, 
                int(domain_focus)
            ]]
            
            # Make prediction
            prediction = model.predict(input_data)[0]
            print(f"Prediction result: {prediction}")
            
            # Get level info
            level_info = get_level_description(prediction)
            
            # Calculate skill scores
            skill_scores = {
                'dsa': min(100, (dsa_level / 10) * 100),
                'problems': min(100, (problem_count / 500) * 100),
                'projects': min(100, (project_count / 50) * 100),
                'github': min(100, (github_quality / 10) * 100)
            }
            
            # Calculate overall score
            overall_score = (
                skill_scores['dsa'] * 0.3 +
                skill_scores['problems'] * 0.25 +
                skill_scores['projects'] * 0.25 +
                skill_scores['github'] * 0.2
            )
            
            # Store in session
            session['assessment_data'] = {
                'dsa_level': dsa_level,
                'problem_count': problem_count,
                'project_count': project_count,
                'github_quality': github_quality,
                'domain_focus': domain_focus,
                'prediction': int(prediction),
                'level_info': level_info,
                'domain_name': DOMAINS[domain_focus]['name'],
                'skill_scores': skill_scores,
                'overall_score': round(overall_score, 1),
                'timestamp': os.times().elapsed
            }
            
            return redirect(url_for('results'))
            
        except Exception as e:
            print(f"Error during assessment: {e}")
            return render_template('assessment.html', 
                                 domains=DOMAINS, 
                                 company=COMPANY_INFO,
                                 error="Please check your inputs and try again.")
    
    return render_template('assessment.html', 
                         domains=DOMAINS, 
                         company=COMPANY_INFO)

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
    domain_info = DOMAINS.get(domain_key, DOMAINS['1'])
    
    return render_template('results.html',
                         assessment_data=assessment_data,
                         suggestions=suggestions[:5],
                         resources=resources[:5],
                         domain=domain_info,
                         domain_key=domain_key,
                         company=COMPANY_INFO)

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'assessment_data' not in session:
        return redirect(url_for('assessment'))
    
    assessment_data = session['assessment_data']
    
    # Calculate skill percentages
    skill_data = {}
    skills = [
        ('dsa_level', 'DSA Proficiency', 10, '#8b5cf6'),
        ('problem_count', 'Problems Solved', 500, '#10b981'),
        ('project_count', 'Projects Completed', 50, '#3b82f6'),
        ('github_quality', 'GitHub Quality', 10, '#ef4444')
    ]
    
    for key, label, max_val, color in skills:
        current = assessment_data[key]
        percentage = min(100, int((current / max_val) * 100))
        skill_data[key] = {
            'value': current,
            'percentage': percentage,
            'max': max_val,
            'label': label,
            'color': color
        }
    
    # Get improvement tips
    improvement_tips = []
    if assessment_data['dsa_level'] < 6:
        improvement_tips.append('Solve more DSA problems (target: 100+ problems)')
    if assessment_data['problem_count'] < 100:
        improvement_tips.append('Increase coding practice on platforms like LeetCode')
    if assessment_data['project_count'] < 5:
        improvement_tips.append('Build more complete projects for your portfolio')
    if assessment_data['github_quality'] < 6:
        improvement_tips.append('Improve GitHub profile with better documentation')
    
    return render_template('dashboard.html',
                         assessment_data=assessment_data,
                         skill_data=skill_data,
                         improvement_tips=improvement_tips,
                         company=COMPANY_INFO)

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
    domain_info = DOMAINS.get(domain_key, DOMAINS['1'])
    
    return render_template('projects.html',
                         suggestions=suggestions,
                         resources=resources,
                         domain=domain_info,
                         assessment_data=assessment_data,
                         company=COMPANY_INFO)

@app.route('/reset')
def reset():
    """Reset session and start over"""
    session.clear()
    return redirect(url_for('assessment'))

@app.route('/api/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy', 
        'service': 'placement-readiness',
        'version': '1.0.0',
        'model_loaded': True
    })

@app.route('/api/assessment-data')
def get_assessment_data():
    """API endpoint to get current assessment data"""
    if 'assessment_data' not in session:
        return jsonify({'error': 'No assessment data found'}), 404
    
    return jsonify(session['assessment_data'])

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', company=COMPANY_INFO), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', company=COMPANY_INFO), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
