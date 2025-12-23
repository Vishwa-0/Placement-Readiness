# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pickle
import numpy as np
import os
import warnings
import traceback
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'vynox-secret-key'

# Try to load the trained model
try:
    with open('PRS.pkl', 'rb') as f:
        model = pickle.load(f)
    print("✓ ML model loaded successfully")
except Exception as e:
    print(f"⚠ Warning: Could not load PRS.pkl: {e}")
    print("⚠ Using overall score calculation instead")
    model = None

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
    },
    '5': {
        'name': 'DevOps',
        'skills': ['Linux', 'Docker/Kubernetes', 'CI/CD', 'Cloud Platforms', 'Infrastructure as Code', 'Monitoring', 'Automation'],
        'description': 'Bridge development and operations with automation, CI/CD, and cloud infrastructure',
        'levels': {
            'beginner': 'Learn Linux basics and version control systems',
            'intermediate': 'Master containerization and CI/CD pipelines',
            'advanced': 'Implement infrastructure as code and cloud architecture'
        },
        'icon': 'fas fa-server',
        'color': '#f59e0b'
    },
    '6': {
        'name': 'Cloud Engineering',
        'skills': ['AWS/Azure/GCP', 'Microservices', 'Serverless', 'Networking', 'Security', 'Cost Optimization', 'Scalability'],
        'description': 'Design, deploy, and maintain cloud infrastructure and services',
        'levels': {
            'beginner': 'Learn cloud fundamentals and basic services',
            'intermediate': 'Master cloud services and architecture patterns',
            'advanced': 'Design enterprise-grade cloud solutions'
        },
        'icon': 'fas fa-cloud',
        'color': '#3b82f6'
    },
    '7': {
        'name': 'Blockchain Development',
        'skills': ['Solidity', 'Smart Contracts', 'Web3.js', 'Ethereum', 'Cryptography', 'DApps', 'Decentralized Finance'],
        'description': 'Build decentralized applications and smart contracts on blockchain platforms',
        'levels': {
            'beginner': 'Learn blockchain fundamentals and cryptography',
            'intermediate': 'Develop smart contracts and basic DApps',
            'advanced': 'Build complex DeFi applications and protocols'
        },
        'icon': 'fas fa-link',
        'color': '#8b5cf6'
    },
    '8': {
        'name': 'Game Development',
        'skills': ['Unity/Unreal Engine', 'C#/C++', '3D Modeling', 'Physics', 'AI in Games', 'Multiplayer', 'Game Design'],
        'description': 'Create interactive games and simulations using game engines and programming',
        'levels': {
            'beginner': 'Learn basic game development concepts and simple games',
            'intermediate': 'Build 2D/3D games with physics and basic AI',
            'advanced': 'Create complex multiplayer games with advanced graphics'
        },
        'icon': 'fas fa-gamepad',
        'color': '#ef4444'
    }
}

PROJECT_SUGGESTIONS = {
    '0': {
        '1': 'Personal Portfolio Website, To-Do List App, Weather App, Calculator, Blog Website',
        '2': 'Titanic Data Analysis, House Price Prediction, Iris Classification, Sales Dashboard',
        '3': 'BMI Calculator, Notes App, Currency Converter, Flashlight App, Quiz App',
        '4': 'Password Checker, Network Scanner, File Integrity Checker, Encryption Tool',
        '5': 'Dockerize a Web App, Basic CI/CD Pipeline, Server Monitoring Script',
        '6': 'Static Website Hosting, Cloud Storage Service, Basic Cloud VM Setup',
        '7': 'Simple Smart Contract, Crypto Wallet, Basic DApp Frontend',
        '8': '2D Platformer Game, Simple Puzzle Game, Character Controller Demo'
    },
    '1': {
        '1': 'E-commerce Platform, Chat App, Project Management Tool, Social Media Dashboard',
        '2': 'Sentiment Analysis, Recommendation Engine, Stock Prediction, Customer Churn Prediction',
        '3': 'Food Delivery App, Fitness Tracker, E-commerce Mobile App, Social Media App',
        '4': 'Vulnerability Scanner, Intrusion Detection System, Security Dashboard, Password Manager',
        '5': 'Microservices Architecture, Kubernetes Cluster, Automated Deployment Pipeline',
        '6': 'Serverless Application, Multi-region Deployment, Auto-scaling System',
        '7': 'DeFi Application, NFT Marketplace, Decentralized Exchange',
        '8': 'Multiplayer Game, VR Experience, Advanced 3D Game with AI'
    }
}

LEARNING_RESOURCES = {
    '1': [
        {'name': 'MDN Web Docs', 'url': 'https://developer.mozilla.org', 'type': 'Documentation'},
        {'name': 'freeCodeCamp', 'url': 'https://freecodecamp.org', 'type': 'Free Courses'},
        {'name': 'W3Schools', 'url': 'https://w3schools.com', 'type': 'Tutorials'},
        {'name': 'Frontend Masters', 'url': 'https://frontendmasters.com', 'type': 'Paid Courses'},
        {'name': 'Codecademy', 'url': 'https://codecademy.com', 'type': 'Interactive'},
        {'name': 'The Odin Project', 'url': 'https://theodinproject.com', 'type': 'Full Curriculum'}
    ],
    '2': [
        {'name': 'Kaggle Learn', 'url': 'https://kaggle.com/learn', 'type': 'Practice'},
        {'name': 'Coursera ML Course', 'url': 'https://coursera.org/learn/machine-learning', 'type': 'Course'},
        {'name': 'Fast.ai', 'url': 'https://fast.ai', 'type': 'Practical AI'},
        {'name': 'DataCamp', 'url': 'https://datacamp.com', 'type': 'Interactive'},
        {'name': 'Towards Data Science', 'url': 'https://towardsdatascience.com', 'type': 'Articles'},
        {'name': 'Google AI', 'url': 'https://ai.google/education', 'type': 'Resources'}
    ],
    '3': [
        {'name': 'Android Developers', 'url': 'https://developer.android.com', 'type': 'Documentation'},
        {'name': 'iOS Dev Center', 'url': 'https://developer.apple.com', 'type': 'Documentation'},
        {'name': 'Flutter Docs', 'url': 'https://flutter.dev/docs', 'type': 'Framework'},
        {'name': 'React Native Docs', 'url': 'https://reactnative.dev/docs', 'type': 'Framework'},
        {'name': 'Raywenderlich', 'url': 'https://raywenderlich.com', 'type': 'Tutorials'},
        {'name': 'Expo Docs', 'url': 'https://docs.expo.dev', 'type': 'Tools'}
    ],
    '4': [
        {'name': 'Cybrary', 'url': 'https://cybrary.it', 'type': 'Courses'},
        {'name': 'HackTheBox', 'url': 'https://hackthebox.com', 'type': 'Practice'},
        {'name': 'TryHackMe', 'url': 'https://tryhackme.com', 'type': 'Learning'},
        {'name': 'OWASP', 'url': 'https://owasp.org', 'type': 'Security'},
        {'name': 'SecurityTube', 'url': 'https://securitytube.net', 'type': 'Videos'},
        {'name': 'PentesterLab', 'url': 'https://pentesterlab.com', 'type': 'Exercises'}
    ],
    '5': [
        {'name': 'Docker Docs', 'url': 'https://docs.docker.com', 'type': 'Documentation'},
        {'name': 'Kubernetes Docs', 'url': 'https://kubernetes.io/docs', 'type': 'Documentation'},
        {'name': 'DevOps Roadmap', 'url': 'https://roadmap.sh/devops', 'type': 'Learning Path'},
        {'name': 'AWS DevOps', 'url': 'https://aws.amazon.com/devops', 'type': 'Cloud'},
        {'name': 'Google Cloud DevOps', 'url': 'https://cloud.google.com/devops', 'type': 'Cloud'},
        {'name': 'Jenkins', 'url': 'https://jenkins.io/doc', 'type': 'CI/CD'}
    ],
    '6': [
        {'name': 'AWS Training', 'url': 'https://aws.amazon.com/training', 'type': 'Training'},
        {'name': 'Azure Learn', 'url': 'https://learn.microsoft.com/azure', 'type': 'Learning'},
        {'name': 'Google Cloud Skills', 'url': 'https://cloud.google.com/training', 'type': 'Training'},
        {'name': 'Cloud Academy', 'url': 'https://cloudacademy.com', 'type': 'Courses'},
        {'name': 'A Cloud Guru', 'url': 'https://acloudguru.com', 'type': 'Learning'},
        {'name': 'Linux Academy', 'url': 'https://linuxacademy.com', 'type': 'Training'}
    ],
    '7': [
        {'name': 'Ethereum Docs', 'url': 'https://ethereum.org/developers', 'type': 'Documentation'},
        {'name': 'Solidity Docs', 'url': 'https://docs.soliditylang.org', 'type': 'Language'},
        {'name': 'OpenZeppelin', 'url': 'https://openzeppelin.com', 'type': 'Security'},
        {'name': 'CryptoZombies', 'url': 'https://cryptozombies.io', 'type': 'Interactive'},
        {'name': 'Buildspace', 'url': 'https://buildspace.so', 'type': 'Projects'},
        {'name': 'Web3 University', 'url': 'https://web3.university', 'type': 'Learning'}
    ],
    '8': [
        {'name': 'Unity Learn', 'url': 'https://learn.unity.com', 'type': 'Official'},
        {'name': 'Unreal Engine Docs', 'url': 'https://docs.unrealengine.com', 'type': 'Documentation'},
        {'name': 'GameDev.net', 'url': 'https://gamedev.net', 'type': 'Community'},
        {'name': 'Gamasutra', 'url': 'https://gamasutra.com', 'type': 'Articles'},
        {'name': 'Brackeys YouTube', 'url': 'https://youtube.com/c/Brackeys', 'type': 'Tutorials'},
        {'name': 'r/gamedev', 'url': 'https://reddit.com/r/gamedev', 'type': 'Community'}
    ]
}

COMPANY_INFO = {
    'name': 'VYNOX',
    'tagline': 'Placement Readiness Assessment System',
    'description': 'AI-powered platform for skill assessment and career guidance',
    'contact_email': 'contact@vynox.com',
    'contact_phone': '+1 (234) 567-8900',
    'address': 'Tech Innovation Hub, Bangalore, India'
}

def get_level_description(overall_score):
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
    max_dsa = 10
    max_problems = 200
    max_projects = 10
    max_github = 10
    
    dsa_percentage = (dsa_level / max_dsa) * 100
    problems_percentage = min(100, (problem_count / max_problems) * 100)
    projects_percentage = min(100, (project_count / max_projects) * 100)
    github_percentage = (github_quality / max_github) * 100
    
    overall_score = (
        dsa_percentage * 0.35 +
        problems_percentage * 0.25 +
        projects_percentage * 0.25 +
        github_percentage * 0.15
    )
    
    return min(100, round(overall_score, 1))

@app.route('/')
def home():
    return render_template('index.html', domains=DOMAINS, company=COMPANY_INFO)

@app.route('/about')
def about():
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
    return render_template('about.html', team=team_members, company=COMPANY_INFO)

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if request.method == 'POST':
        try:
            dsa_level = int(request.form.get('dsa_level', 5))
            problem_count = int(request.form.get('problem_count', 50))
            project_count = int(request.form.get('project_count', 3))
            github_quality = int(request.form.get('github_quality', 5))
            domain_focus = request.form.get('domain_focus', '1')
            
            dsa_level = max(1, min(10, dsa_level))
            problem_count = max(0, min(500, problem_count))
            project_count = max(0, min(50, project_count))
            github_quality = max(1, min(10, github_quality))
            
            if domain_focus not in DOMAINS:
                domain_focus = '1'
            
            print(f"Assessment inputs: DSA={dsa_level}, Problems={problem_count}, Projects={project_count}, GitHub={github_quality}, Domain={domain_focus}")
            
            overall_score = calculate_overall_score(dsa_level, problem_count, project_count, github_quality)
            print(f"Calculated Overall Score: {overall_score}%")
            
            is_ready = 1 if overall_score >= 60 else 0
            print(f"Readiness Decision: {'READY' if is_ready == 1 else 'NOT READY'} (Threshold: 60%)")
            
            level_info = get_level_description(overall_score)
            
            session['assessment_data'] = {
                'dsa_level': dsa_level,
                'problem_count': problem_count,
                'project_count': project_count,
                'github_quality': github_quality,
                'domain_focus': domain_focus,
                'prediction': is_ready,
                'overall_score': overall_score,
                'level_info': level_info,
                'domain_name': DOMAINS[domain_focus]['name'],
                'domain_info': DOMAINS[domain_focus]
            }
            
            print(f"Session data stored: {session['assessment_data']}")
            
            return redirect(url_for('results'))
            
        except Exception as e:
            print(f"Error during assessment: {e}")
            print(traceback.format_exc())
            return render_template('assessment.html', 
                                 domains=DOMAINS, 
                                 company=COMPANY_INFO,
                                 error=f"Please check your inputs and try again. Error: {str(e)}")
    
    return render_template('assessment.html', domains=DOMAINS, company=COMPANY_INFO)

@app.route('/results')
def results():
    try:
        if 'assessment_data' not in session:
            print("No assessment data in session, redirecting to assessment")
            return redirect(url_for('assessment'))
        
        assessment_data = session['assessment_data']
        domain_key = str(assessment_data['domain_focus'])
        prediction = assessment_data['prediction']
        overall_score = assessment_data['overall_score']
        
        print(f"Results page - Domain Key: {domain_key}, Prediction: {prediction}, Score: {overall_score}")
        
        suggestions_key = str(prediction)
        suggestions_str = PROJECT_SUGGESTIONS.get(suggestions_key, {}).get(domain_key, 'No suggestions available')
        
        if suggestions_str == 'No suggestions available':
            print(f"Warning: No project suggestions found for prediction={suggestions_key}, domain={domain_key}")
            suggestions_str = PROJECT_SUGGESTIONS.get('0', {}).get(domain_key, 'Personal Portfolio, To-Do List App, Weather App')
        
        suggestions = [s.strip() for s in suggestions_str.split(',')]
        
        resources = LEARNING_RESOURCES.get(domain_key, [])
        domain_info = DOMAINS.get(domain_key, DOMAINS['1'])
        
        print(f"Loaded {len(resources)} resources for domain {domain_key}")
        
        return render_template('results.html',
                             assessment_data=assessment_data,
                             suggestions=suggestions[:5],
                             resources=resources[:6],
                             domain=domain_info,
                             domain_key=domain_key,
                             company=COMPANY_INFO,
                             overall_score=overall_score)
    
    except Exception as e:
        print(f"Error in results route: {e}")
        print(traceback.format_exc())
        return render_template('500.html', error=str(e), company=COMPANY_INFO), 500

@app.route('/dashboard')
def dashboard():
    try:
        if 'assessment_data' not in session:
            return redirect(url_for('assessment'))
        
        assessment_data = session['assessment_data']
        overall_score = assessment_data['overall_score']
        
        max_values = {
            'dsa_level': 10,
            'problem_count': 200,
            'project_count': 10,
            'github_quality': 10
        }
        
        skill_data = {}
        
        dsa_percentage = min(100, int((assessment_data['dsa_level'] / max_values['dsa_level']) * 100))
        skill_data['dsa_level'] = {
            'value': assessment_data['dsa_level'],
            'percentage': dsa_percentage,
            'max': max_values['dsa_level'],
            'label': 'DSA Proficiency',
            'color': '#8b5cf6',
            'level': 'Beginner' if dsa_percentage < 40 else 'Intermediate' if dsa_percentage < 70 else 'Advanced'
        }
        
        prob_percentage = min(100, int((assessment_data['problem_count'] / max_values['problem_count']) * 100))
        skill_data['problem_count'] = {
            'value': assessment_data['problem_count'],
            'percentage': prob_percentage,
            'max': max_values['problem_count'],
            'label': 'Problems Solved',
            'color': '#10b981',
            'level': 'Beginner' if prob_percentage < 40 else 'Intermediate' if prob_percentage < 70 else 'Advanced'
        }
        
        proj_percentage = min(100, int((assessment_data['project_count'] / max_values['project_count']) * 100))
        skill_data['project_count'] = {
            'value': assessment_data['project_count'],
            'percentage': proj_percentage,
            'max': max_values['project_count'],
            'label': 'Projects Completed',
            'color': '#3b82f6',
            'level': 'Beginner' if proj_percentage < 40 else 'Intermediate' if proj_percentage < 70 else 'Advanced'
        }
        
        git_percentage = min(100, int((assessment_data['github_quality'] / max_values['github_quality']) * 100))
        skill_data['github_quality'] = {
            'value': assessment_data['github_quality'],
            'percentage': git_percentage,
            'max': max_values['github_quality'],
            'label': 'GitHub Quality',
            'color': '#ef4444',
            'level': 'Beginner' if git_percentage < 40 else 'Intermediate' if git_percentage < 70 else 'Advanced'
        }
        
        improvement_tips = []
        
        if assessment_data['dsa_level'] < 6:
            improvement_tips.append(f'Improve DSA skills: Current {assessment_data["dsa_level"]}/10 (Target: 7+)')
        
        if assessment_data['problem_count'] < 100:
            improvement_tips.append(f'Solve more problems: Current {assessment_data["problem_count"]} (Target: 150+)')
        
        if assessment_data['project_count'] < 3:
            improvement_tips.append(f'Build more projects: Current {assessment_data["project_count"]} (Target: 5+)')
        
        if assessment_data['github_quality'] < 6:
            improvement_tips.append(f'Improve GitHub profile: Current {assessment_data["github_quality"]}/10 (Target: 7+)')
        
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
    
    except Exception as e:
        print(f"Error in dashboard route: {e}")
        print(traceback.format_exc())
        return render_template('500.html', error=str(e), company=COMPANY_INFO), 500

@app.route('/projects')
def projects():
    """Project suggestions page"""
    try:
        if 'assessment_data' not in session:
            return redirect(url_for('assessment'))
        
        assessment_data = session['assessment_data']
        domain_key = str(assessment_data['domain_focus'])
        prediction = assessment_data['prediction']
        
        print(f"Projects page - Domain Key: {domain_key}, Prediction: {prediction}")
        
        # Get project suggestions - Handle missing keys
        suggestions_key = str(prediction)
        suggestions_str = PROJECT_SUGGESTIONS.get(suggestions_key, {}).get(domain_key, '')
        
        if not suggestions_str:
            # Fallback to beginner projects if no suggestions found
            suggestions_str = PROJECT_SUGGESTIONS.get('0', {}).get(domain_key, 
                'Personal Portfolio Website, To-Do List App, Weather App, Calculator, Blog Website')
        
        # Clean and split the suggestions
        suggestions = [s.strip() for s in suggestions_str.split(',') if s.strip()]
        
        # Get resources
        resources = LEARNING_RESOURCES.get(domain_key, [])
        domain_info = DOMAINS.get(domain_key, DOMAINS['1'])
        
        return render_template('projects.html',
                             suggestions=suggestions,
                             resources=resources,
                             domain=domain_info,
                             assessment_data=assessment_data,
                             company=COMPANY_INFO)
    
    except Exception as e:
        print(f"Error in projects route: {e}")
        print(traceback.format_exc())
        return render_template('500.html', 
                             error="Unable to load project recommendations. Please try again.",
                             company=COMPANY_INFO), 500

@app.route('/learning-resources')
def learning_resources():
    """Learning resources page - Accessible to everyone"""
    try:
        personalized = False
        
        if 'assessment_data' in session:
            assessment_data = session['assessment_data']
            domain_key = str(assessment_data['domain_focus'])
            resources = LEARNING_RESOURCES.get(domain_key, [])
            domain_info = DOMAINS.get(domain_key, DOMAINS['1'])
            personalized = True
        else:
            assessment_data = None
            domain_info = DOMAINS['1']
            
            # Show top resources from all domains
            all_resources = []
            for domain_key in LEARNING_RESOURCES:
                all_resources.extend(LEARNING_RESOURCES[domain_key][:2])
            
            # Remove duplicates
            seen = set()
            resources = []
            for resource in all_resources:
                if resource['name'] not in seen:
                    seen.add(resource['name'])
                    resources.append(resource)
            
            personalized = False
        
        print(f"Learning Resources page - Personalized: {personalized}, Resources: {len(resources)}")
        
        return render_template('learning_resources.html',
                             resources=resources,
                             domain=domain_info,
                             assessment_data=assessment_data,
                             personalized=personalized,
                             company=COMPANY_INFO)
    
    except Exception as e:
        print(f"Error in learning_resources route: {e}")
        print(traceback.format_exc())
        return render_template('500.html', error=str(e), company=COMPANY_INFO), 500

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('assessment'))

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'placement-readiness',
        'version': '1.0.0',
        'uses_overall_score': True
    })

@app.route('/api/assessment-data')
def get_assessment_data():
    if 'assessment_data' not in session:
        return jsonify({'error': 'No assessment data found'}), 404
    
    return jsonify(session['assessment_data'])

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', company=COMPANY_INFO), 404

@app.errorhandler(500)
def internal_server_error(e):
    print(f"500 Error: {e}")
    print(traceback.format_exc())
    return render_template('500.html', 
                         error=str(e) if app.debug else 'Internal Server Error',
                         company=COMPANY_INFO), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    print(f"Starting Flask app on port {port} with debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)
