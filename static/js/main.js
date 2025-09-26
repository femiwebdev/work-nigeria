// This file contains the JavaScript code for the website's frontend functionality.

// Function to handle user registration
function registerUser(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    fetch('/accounts/register/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Registration successful!');
            window.location.href = '/';
        } else {
            alert('Registration failed: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to handle user login
function loginUser(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    fetch('/accounts/login/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Login successful!');
            window.location.href = '/';
        } else {
            alert('Login failed: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to load projects dynamically
function loadProjects() {
    fetch('/projects/')
    .then(response => response.json())
    .then(data => {
        const projectsContainer = document.getElementById('projects-container');
        projectsContainer.innerHTML = '';
        data.projects.forEach(project => {
            const projectElement = document.createElement('div');
            projectElement.className = 'project';
            projectElement.innerHTML = `
                <h3>${project.title}</h3>
                <p>${project.description}</p>
                <a href="/projects/${project.id}/">View Details</a>
            `;
            projectsContainer.appendChild(projectElement);
        });
    })
    .catch(error => console.error('Error loading projects:', error));
}

// Event listeners for forms
document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', registerUser);
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', loginUser);
    }

    loadProjects();
});

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const preview = this.parentNode.querySelector('.file-preview');
                if (preview) {
                    preview.textContent = file.name;
                }
            }
        });
    });

    // Search functionality
    const searchForm = document.querySelector('#search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[type="search"]');
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 3) {
                    // Perform search (you can implement AJAX here)
                    console.log('Searching for:', this.value);
                }
            }, 500);
        });
    }

    // Price range slider
    const priceRangeSlider = document.querySelector('#price-range');
    if (priceRangeSlider) {
        priceRangeSlider.addEventListener('input', function() {
            const priceDisplay = document.querySelector('#price-display');
            if (priceDisplay) {
                priceDisplay.textContent = `₦${parseInt(this.value).toLocaleString()}`;
            }
        });
    }

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const textToCopy = targetElement.textContent || targetElement.value;
                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Show success message
                    this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        this.innerHTML = '<i class="fas fa-copy"></i> Copy';
                    }, 2000);
                });
            }
        });
    });

    // Infinite scroll for listings
    let loading = false;
    const loadMoreBtn = document.querySelector('#load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            if (loading) return;
            
            loading = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            
            // Simulate loading (replace with actual AJAX call)
            setTimeout(() => {
                loading = false;
                this.innerHTML = 'Load More';
                // Add new items to the list
            }, 1000);
        });
    }

    // Rating stars interaction
    const ratingStars = document.querySelectorAll('.rating-stars .star');
    ratingStars.forEach((star, index) => {
        star.addEventListener('click', function() {
            const rating = index + 1;
            const container = this.closest('.rating-stars');
            const hiddenInput = container.querySelector('input[type="hidden"]');
            
            if (hiddenInput) {
                hiddenInput.value = rating;
            }
            
            // Update visual state
            container.querySelectorAll('.star').forEach((s, i) => {
                if (i < rating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
        
        star.addEventListener('mouseenter', function() {
            const index = Array.from(this.parentNode.children).indexOf(this);
            this.parentNode.querySelectorAll('.star').forEach((s, i) => {
                if (i <= index) {
                    s.classList.add('hover');
                } else {
                    s.classList.remove('hover');
                }
            });
        });
        
        star.parentNode.addEventListener('mouseleave', function() {
            this.querySelectorAll('.star').forEach(s => {
                s.classList.remove('hover');
            });
        });
    });

    // Auto-save draft functionality
    const draftForms = document.querySelectorAll('.auto-save-form');
    draftForms.forEach(form => {
        const formId = form.getAttribute('data-form-id');
        let saveTimeout;
        
        // Load saved draft
        const savedDraft = localStorage.getItem(`draft_${formId}`);
        if (savedDraft) {
            const draftData = JSON.parse(savedDraft);
            Object.keys(draftData).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = draftData[key];
                }
            });
        }
        
        // Save draft on input
        form.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                const formData = new FormData(form);
                const draftData = {};
                for (let [key, value] of formData.entries()) {
                    draftData[key] = value;
                }
                localStorage.setItem(`draft_${formId}`, JSON.stringify(draftData));
                
                // Show save indicator
                const saveIndicator = document.querySelector('#save-indicator');
                if (saveIndicator) {
                    saveIndicator.textContent = 'Draft saved';
                    saveIndicator.classList.add('show');
                    setTimeout(() => {
                        saveIndicator.classList.remove('show');
                    }, 2000);
                }
            }, 1000);
        });
        
        // Clear draft on successful submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(`draft_${formId}`);
        });
    });

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    // Make notification function globally available
    window.showNotification = showNotification;
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: 'NGN'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-NG', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

function timeAgo(date) {
    const now = new Date();
    const diffTime = Math.abs(now - new Date(date));
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        return 'Today';
    } else if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else if (diffDays < 30) {
        const weeks = Math.floor(diffDays / 7);
        return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    } else {
        const months = Math.floor(diffDays / 30);
        return `${months} month${months > 1 ? 's' : ''} ago`;
    }
}

// Make utility functions globally available
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.timeAgo = timeAgo;