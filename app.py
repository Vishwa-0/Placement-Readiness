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
    print("⚠ Using overall score calculation instead")
    model = None

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
        'color': '#8b5cf6'
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
        'color': '#10b981'
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
        'color': '#3b82f6'
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
        'color': '#ef4444'
    }
}

# Project suggestions based on readiness level - SIMPLIFIED
PROJECT_SUGGESTIONS = {
    '0': {  # Not Ready (Overall Score < 60%)
        '1': 'Personal Portfolio Website, To-Do List App, Weather App, Calculator, Blog Website',
        '2': 'Titanic Data Analysis, House Price Prediction, Iris Classification, Sales Dashboard',
        '3': 'BMI Calculator, Notes App, Currency Converter, Flashlight App, Quiz App',
        '4': 'Password Checker, Network Scanner, File Integrity Checker, Encryption Tool'
    },
    '1': {  # Ready (Overall Score >= 60%)
        '1': 'E-commerce Platform, Chat App, Project Management Tool, Social Media Dashboard',
        '2': 'Sentiment Analysis, Recommendation Engine, Stock Prediction, Customer Churn Prediction',
        '3': 'Food Delivery App, Fitness Tracker, E-commerce Mobile App, Social Media App',
        '4': 'Vulnerability Scanner, Intrusion Detection System, Security Dashboard, Password Manager'
    }
}

# Learning resources for each domain - SIMPLIFIED
LEARNING_RESOURCES = {
    '1': 'MDN Web Docs, freeCodeCamp, W3Schools, Frontend Masters, Codecademy',
    '2': 'Kaggle, Coursera ML Course, Fast.ai, DataCamp, Towards Data Science',
    '3': 'Android Developers, iOS Dev Center, Flutter Docs, React Native Docs',
    '4': 'Cybrary, HackTheBox, TryHackMe, OWASP, SecurityTube'
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

def get_level_description(overall_score):
    """Get level description based on overall score (0-100%)"""
    if overall_score >= 60:
        return {
            'level': 'Advanced',
            'description': 'You have strong technical skills. Focus on advanced projects and interview preparation.',
            'color': 'success',
            'bg_color': '#10b981',
            'readiness': 'Placement Ready',
            'icon': 'fas fa-trophy',
            'advice': 'Prepare for technical interviews and work on complex projects to showcase your expertise.'
        }
    elif overall_score >= 40:
        return {
            'level': 'Intermediate',
            'description': 'You have good foundational skills. Focus on building intermediate projects and solving more problems.',
            'color': 'info',
            'bg_color': '#3b82f6',
            'readiness': 'Getting There',
            'icon': 'fas fa-chart-line',
            'advice': 'Build 2-3 intermediate projects and solve 100+ coding problems.'
        }
    else:
        return {
            'level': 'Beginner',
            'description': 'You need to focus on building foundational skills. Start with basic projects.',
            'color': 'warning',
            'bg_color': '#f59e0b',
            'readiness': 'Needs Improvement',
            'icon': 'fas fa-seedling',
            'advice': 'Focus on completing basic projects and solving fundamental coding problems.'
        }

def calculate_overall_score(dsa_level, problem_count, project_count, github_quality):
    """Calculate overall readiness score based on all factors"""
    # Define realistic maximums
    max_dsa = 10
    max_problems = 200  # Realistic target for placement
    max_projects = 10   # Realistic target for placement
    max_github = 10
    
    # Calculate percentages
    dsa_percentage = (dsa_level / max_dsa) * 100
    problems_percentage = min(100, (problem_count / max_problems) * 100)
    projects_percentage = min(100, (project_count / max_projects) * 100)
    github_percentage = (github_quality / max_github) * 100
    
    # Weighted scoring (more weight to DSA and Projects)
    overall_score = (
        dsa_percentage * 0.35 +      # DSA is most important (35%)
        problems_percentage * 0.25 +  # Problem solving (25%)
        projects_percentage * 0.25 +  # Project experience (25%)
        github_percentage * 0.15      # GitHub profile (15%)
    )
    
    return min(100, round(overall_score, 1))

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
            'role': 'Team Lead',
            'skills': 'Project Management, System Architecture, Leadership',
            'bio': 'Oversees project execution and team coordination. Ensures seamless integration of all system components.',
            'avatar': 'SW',
            'color': '#8b5cf6'
        },
        {
            'name': 'Santhosh',
            'role': 'Creative Lead',
            'skills': 'UI/UX Design, Brand Identity, Visual Design',
            'bio': 'Designs intuitive user interfaces and creates engaging visual experiences. Focuses on user-centered design.',
            'avatar': 'SA',
            'color': '#10b981'
        },
        {
            'name': 'Vishwa',
            'role': 'Tech Lead',
            'skills': 'Full-Stack Development, Technical Strategy, Code Quality',
            'bio': 'Leads technical development and ensures code quality. Implements best practices and mentors team members.',
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
            
            print(f"Assessment inputs: DSA={dsa_level}, Problems={problem_count}, Projects={project_count}, GitHub={github_quality}, Domain={domain_focus}")
            
            # Calculate overall readiness score (our primary metric)
            overall_score = calculate_overall_score(dsa_level, problem_count, project_count, github_quality)
            print(f"Calculated Overall Score: {overall_score}%")
            
            # Determine readiness based on overall score (60% threshold)
            is_ready = 1 if overall_score >= 60 else 0
            print(f"Readiness Decision: {'READY' if is_ready == 1 else 'NOT READY'} (Threshold: 60%)")
            
            # Get level info based on overall score
            level_info = get_level_description(overall_score)
            
            # Store in session
            session['assessment_data'] = {
                'dsa_level': dsa_level,
                'problem_count': problem_count,
                'project_count': project_count,
                'github_quality': github_quality,
                'domain_focus': domain_focus,
                'prediction': is_ready,  # 1 if ready, 0 if not ready
                'overall_score': overall_score,
                'level_info': level_info,
                'domain_name': DOMAINS[domain_focus]['name'],
                'domain_info': DOMAINS[domain_focus]
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
    prediction = assessment_data['prediction']  # 0 or 1 based on 60% threshold
    overall_score = assessment_data['overall_score']
    
    # Get project suggestions based on readiness (0 or 1)
    suggestions_str = PROJECT_SUGGESTIONS.get(str(prediction), {}).get(domain_key, 'No suggestions available')
    suggestions = [s.strip() for s in suggestions_str.split(',')]
    
    # Get resources
    resources_str = LEARNING_RESOURCES.get(domain_key, 'No resources available')
    resources = [r.strip() for r in resources_str.split(',')]
    
    domain_info = DOMAINS.get(domain_key, DOMAINS['1'])
    
    return render_template('results.html',
                         assessment_data=assessment_data,
                         suggestions=suggestions[:5],
                         resources=resources[:5],
                         domain=domain_info,
                         domain_key=domain_key,
                         company=COMPANY_INFO,
                         overall_score=overall_score)

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'assessment_data' not in session:
        return redirect(url_for('assessment'))
    
    assessment_data = session['assessment_data']
    overall_score = assessment_data['overall_score']
    
    # Define realistic maximums for calculations
    max_values = {
        'dsa_level': 10,
        'problem_count': 200,  # Realistic max: 200 problems
        'project_count': 10,   # Realistic max: 10 projects
        'github_quality': 10
    }
    
    # Calculate skill percentages with realistic max values
    skill_data = {}
    
    # DSA Level
    dsa_percentage = min(100, int((assessment_data['dsa_level'] / max_values['dsa_level']) * 100))
    skill_data['dsa_level'] = {
        'value': assessment_data['dsa_level'],
        'percentage': dsa_percentage,
        'max': max_values['dsa_level'],
        'label': 'DSA Proficiency',
        'color': '#8b5cf6',
        'level': 'Beginner' if dsa_percentage < 40 else 'Intermediate' if dsa_percentage < 70 else 'Advanced'
    }
    
    # Problems Solved
    prob_percentage = min(100, int((assessment_data['problem_count'] / max_values['problem_count']) * 100))
    skill_data['problem_count'] = {
        'value': assessment_data['problem_count'],
        'percentage': prob_percentage,
        'max': max_values['problem_count'],
        'label': 'Problems Solved',
        'color': '#10b981',
        'level': 'Beginner' if prob_percentage < 40 else 'Intermediate' if prob_percentage < 70 else 'Advanced'
    }
    
    # Projects Completed
    proj_percentage = min(100, int((assessment_data['project_count'] / max_values['project_count']) * 100))
    skill_data['project_count'] = {
        'value': assessment_data['project_count'],
        'percentage': proj_percentage,
        'max': max_values['project_count'],
        'label': 'Projects Completed',
        'color': '#3b82f6',
        'level': 'Beginner' if proj_percentage < 40 else 'Intermediate' if proj_percentage < 70 else 'Advanced'
    }
    
    # GitHub Quality
    git_percentage = min(100, int((assessment_data['github_quality'] / max_values['github_quality']) * 100))
    skill_data['github_quality'] = {
        'value': assessment_data['github_quality'],
        'percentage': git_percentage,
        'max': max_values['github_quality'],
        'label': 'GitHub Quality',
        'color': '#ef4444',
        'level': 'Beginner' if git_percentage < 40 else 'Intermediate' if git_percentage < 70 else 'Advanced'
    }
    
    # Get improvement tips based on actual scores
    improvement_tips = []
    
    if assessment_data['dsa_level'] < 6:
        improvement_tips.append(f'Improve DSA skills: Current {assessment_data["dsa_level"]}/10 (Target: 7+)')
    
    if assessment_data['problem_count'] < 100:
        improvement_tips.append(f'Solve more problems: Current {assessment_data["problem_count"]} (Target: 150+)')
    
    if assessment_data['project_count'] < 3:
        improvement_tips.append(f'Build more projects: Current {assessment_data["project_count"]} (Target: 5+)')
    
    if assessment_data['github_quality'] < 6:
        improvement_tips.append(f'Improve GitHub profile: Current {assessment_data["github_quality"]}/10 (Target: 7+)')
    
    # If no specific tips, add general ones
    if not improvement_tips:
        if overall_score >= 60:
            improvement_tips.append('Prepare for technical interviews with mock sessions')
            improvement_tips.append('Contribute to open-source projects')
            improvement_tips.append('Build advanced projects to showcase expertise')
        else:
            improvement_tips.append('Focus on building a strong foundation with basic projects')
            improvement_tips.append('Solve at least 100 coding problems regularly')
            improvement_tips.append('Complete 3-5 meaningful projects for your portfolio')
    
    return render_template('dashboard.html',
                         assessment_data=assessment_data,
                         skill_data=skill_data,
                         improvement_tips=improvement_tips,
                         overall_score=int(overall_score),
                         company=COMPANY_INFO)

@app.route('/projects')
def projects():
    """Project suggestions page"""
    if 'assessment_data' not in session:
        return redirect(url_for('assessment'))
    
    assessment_data = session['assessment_data']
    domain_key = assessment_data['domain_focus']
    prediction = assessment_data['prediction']
    
    # Get project suggestions
    suggestions_str = PROJECT_SUGGESTIONS.get(str(prediction), {}).get(domain_key, 'No suggestions available')
    suggestions = [s.strip() for s in suggestions_str.split(',')]
    
    # Get resources
    resources_str = LEARNING_RESOURCES.get(domain_key, 'No resources available')
    resources = [r.strip() for r in resources_str.split(',')]
    
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
        'uses_overall_score': True
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
