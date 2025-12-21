// Placement Readiness System - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Dynamic range slider value display
    const rangeSliders = document.querySelectorAll('input[type="range"]');
    rangeSliders.forEach(slider => {
        const valueDisplay = document.getElementById(slider.id + '_value');
        if (valueDisplay) {
            // Update value display
            slider.addEventListener('input', function() {
                valueDisplay.textContent = this.value;
            });
            
            // Initialize display
            valueDisplay.textContent = slider.value;
        }
    });

    // Skill level indicators
    updateSkillIndicators();
    
    // AJAX readiness check (if on assessment page)
    const quickCheckBtn = document.getElementById('quick-check-btn');
    if (quickCheckBtn) {
        quickCheckBtn.addEventListener('click', performQuickCheck);
    }

    // Dashboard progress animation
    animateProgressBars();

    // Theme toggle functionality
    setupThemeToggle();

    // Back to top button
    setupBackToTop();

    // Mobile navigation enhancement
    enhanceMobileNav();
});

// Function to update skill indicators
function updateSkillIndicators() {
    const indicators = document.querySelectorAll('.skill-indicator');
    indicators.forEach(indicator => {
        const level = parseInt(indicator.getAttribute('data-level'));
        let color = 'danger';
        
        if (level >= 8) color = 'success';
        else if (level >= 5) color = 'warning';
        
        indicator.classList.add(`bg-${color}`);
    });
}

// Perform quick readiness check via AJAX
function performQuickCheck() {
    const dsaLevel = document.getElementById('dsa_level').value;
    const problemCount = document.getElementById('problem_count').value;
    const projectCount = document.getElementById('project_count').value;
    const githubQuality = document.getElementById('github_quality').value;
    const domainFocus = document.getElementById('domain_focus').value;
    
    // Show loading state
    const quickCheckBtn = document.getElementById('quick-check-btn');
    const originalText = quickCheckBtn.innerHTML;
    quickCheckBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Checking...';
    quickCheckBtn.disabled = true;
    
    fetch('/api/check-readiness', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            dsa_level: parseInt(dsaLevel),
            problem_count: parseInt(problemCount),
            project_count: parseInt(projectCount),
            github_quality: parseInt(githubQuality),
            domain_focus: domainFocus
        })
    })
    .then(response => response.json())
    .then(data => {
        // Restore button
        quickCheckBtn.innerHTML = originalText;
        quickCheckBtn.disabled = false;
        
        // Show result
        if (data.error) {
            showAlert('Error: ' + data.error, 'danger');
        } else {
            const resultDiv = document.getElementById('quick-result');
            if (resultDiv) {
                const badgeClass = data.prediction === 1 ? 'success' : 'warning';
                resultDiv.innerHTML = `
                    <div class="alert alert-${badgeClass}">
                        <h5>Quick Assessment Result</h5>
                        <p>You are: <span class="badge bg-${badgeClass}">${data.readiness}</span></p>
                        <small>For detailed analysis and personalized recommendations, submit the full assessment.</small>
                    </div>
                `;
                resultDiv.scrollIntoView({ behavior: 'smooth' });
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        quickCheckBtn.innerHTML = originalText;
        quickCheckBtn.disabled = false;
        showAlert('Network error. Please try again.', 'danger');
    });
}

// Animate progress bars in dashboard
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1.5s ease-in-out';
            bar.style.width = targetWidth;
        }, 100);
    });
}

// Setup theme toggle
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update icon
            const icon = this.querySelector('i');
            if (newTheme === 'dark') {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
            
            showAlert(`Theme changed to ${newTheme} mode`, 'info', 2000);
        });
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        
        // Set initial icon
        const icon = themeToggle.querySelector('i');
        if (savedTheme === 'dark') {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }
}

// Setup back to top button
function setupBackToTop() {
    const backToTopBtn = document.createElement('button');
    backToTopBtn.id = 'back-to-top';
    backToTopBtn.className = 'btn btn-primary rounded-circle';
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopBtn.style.position = 'fixed';
    backToTopBtn.style.bottom = '20px';
    backToTopBtn.style.right = '20px';
    backToTopBtn.style.zIndex = '1000';
    backToTopBtn.style.display = 'none';
    
    document.body.appendChild(backToTopBtn);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });
    
    // Scroll to top when clicked
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Enhance mobile navigation
function enhanceMobileNav() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                bsCollapse.hide();
            }
        });
    });
}

// Utility function to show alerts
function showAlert(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '1050';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, duration);
    }
}

// Export data function for dashboard
function exportDashboardData(format = 'json') {
    const assessmentData = JSON.parse(sessionStorage.getItem('assessmentData') || '{}');
    
    if (Object.keys(assessmentData).length === 0) {
        showAlert('No assessment data available to export', 'warning');
        return;
    }
    
    let dataStr, fileName, mimeType;
    
    if (format === 'json') {
        dataStr = JSON.stringify(assessmentData, null, 2);
        fileName = 'vynox-assessment-data.json';
        mimeType = 'application/json';
    } else if (format === 'csv') {
        // Convert to CSV
        const headers = Object.keys(assessmentData);
        const values = Object.values(assessmentData);
        dataStr = headers.join(',') + '\n' + values.join(',');
        fileName = 'vynox-assessment-data.csv';
        mimeType = 'text/csv';
    }
    
    // Create download link
    const blob = new Blob([dataStr], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    showAlert(`Data exported as ${format.toUpperCase()}`, 'success');
}

// Print dashboard function
function printDashboard() {
    window.print();
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + P to print dashboard
    if ((e.ctrlKey || e.metaKey) && e.key === 'p' && window.location.pathname.includes('/dashboard')) {
        e.preventDefault();
        printDashboard();
    }
    
    // Ctrl/Cmd + E to export data
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        exportDashboardData('json');
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
});
