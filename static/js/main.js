// Main application functionality
console.log('Main.js loaded successfully!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Initializing navigation...');
    
    // Initialize profile data
    initializeProfileData();
    
    // Add click event listener to profile trigger
    const profileTrigger = document.querySelector('.profile-trigger');
    if (profileTrigger) {
        profileTrigger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleProfileDropdown();
        });
    }
    
    // Add navigation button functionality
    const navIcons = document.querySelectorAll('.nav-icon');
    navIcons.forEach(icon => {
        icon.addEventListener('click', function(e) {
            e.preventDefault();
            const iconText = this.textContent;
            
            if (iconText === '🏠') {
                // Home - switch to sell tab
                switchTab('sell');
            } else if (iconText === '🔍') {
                // Search - focus search input
                const searchInput = document.querySelector('.search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            } else if (iconText === '➕') {
                // Add - switch to sell tab
                switchTab('sell');
            } else if (iconText === '❤️') {
                // Favorites - show interested crops
                showFavorites();
            }
        });
    });
    
    // Add story button functionality
    const storyItems = document.querySelectorAll('.story-item');
    storyItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const storyName = this.querySelector('.story-name');
            if (storyName) {
                const courseType = storyName.textContent.toLowerCase();
                if (courseType === 'your story') {
                    // Show user's own courses
                    showMyCourses();
                } else {
                    // Filter courses by type
                    filterCoursesByType(courseType);
                }
            }
        });
    });
    
    // Add tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.id.replace('-tab', '');
            switchTab(tabName);
        });
    });
    
    // Search functionality (removed duplicate - already handled above)

    // Navigation buttons functionality (removed duplicate - already handled above)

    // Like button functionality
    const likeButtons = document.querySelectorAll('.action-btn');
    likeButtons.forEach(btn => {
        if (btn.textContent.includes('❤️')) {
            btn.addEventListener('click', function() {
                this.classList.toggle('liked');
                if (this.classList.contains('liked')) {
                    this.textContent = '❤️';
                    this.style.color = '#e91e63';
                } else {
                    this.textContent = '🤍';
                    this.style.color = '#262626';
                }
            });
        }
    });

    // Story interactions (removed duplicate - already handled above)

    // Bookmark functionality
    const bookmarkButtons = document.querySelectorAll('.action-btn.bookmark');
    bookmarkButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.toggle('bookmarked');
            if (this.classList.contains('bookmarked')) {
                this.textContent = '🔖';
                this.style.color = '#ffa500';
            } else {
                this.textContent = '🔖';
                this.style.color = '#262626';
            }
        });
    });
});

// Logout functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in and show/hide navigation elements
    function updateNavigation() {
        const logoutBtn = document.getElementById('logout-nav-link');
        const loginBtn = document.getElementById('login-nav-link');
        const signupBtn = document.getElementById('signup-nav-link');
        const profileDropdown = document.getElementById('profile-dropdown');
        
        // Check if all required elements exist
        if (!loginBtn || !signupBtn || !profileDropdown) {
            console.error('Missing navigation elements:', {
                loginBtn: !!loginBtn,
                signupBtn: !!signupBtn,
                profileDropdown: !!profileDropdown
            });
            return;
        }
        
        // Check if we're on the booking page or have user data in session
        const bookingPage = document.querySelector('.booking-page');
        const hasUserEmail = sessionStorage.getItem('userEmail');
        const isOnBookingPage = window.location.pathname.includes('/booking');
        const isLoggedIn = bookingPage !== null || hasUserEmail || isOnBookingPage;
        
        if (loginBtn && signupBtn && profileDropdown) {
            // Force show profile dropdown if we're on booking page (user is logged in)
            if (isLoggedIn || window.location.pathname.includes('/booking')) {
                // User is logged in - show profile dropdown and logout, hide login/signup
                profileDropdown.style.display = 'block';
                if (logoutBtn) {
                    logoutBtn.style.display = 'block';
                }
                loginBtn.style.display = 'none';
                signupBtn.style.display = 'none';
                
                // Update profile display
                updateProfileDisplay();
            } else {
                // User is not logged in - show login/signup, hide profile dropdown and logout
                profileDropdown.style.display = 'none';
                if (logoutBtn) {
                    logoutBtn.style.display = 'none';
                }
                loginBtn.style.display = 'block';
                signupBtn.style.display = 'block';
            }
        } else {
            console.log('Some navigation elements not found!');
        }
    }
    
    // Update profile display with current data
    function updateProfileDisplay() {
        const userName = sessionStorage.getItem('userName') || 'User';
        const userEmail = sessionStorage.getItem('userEmail') || 'user@example.com';
        
        // Update profile initials
        const profileInitial = document.getElementById('profile-initial');
        const profileInitialLarge = document.getElementById('profile-initial-large');
        const initial = userName.charAt(0).toUpperCase();
        
        if (profileInitial) {
            profileInitial.textContent = initial;
        }
        if (profileInitialLarge) {
            profileInitialLarge.textContent = initial;
        }
        
        // Update username and email
        const usernameDisplay = document.getElementById('username-display-large');
        const userEmailDisplay = document.getElementById('user-email');
        
        if (usernameDisplay) {
            usernameDisplay.textContent = userName;
        }
        if (userEmailDisplay) {
            userEmailDisplay.textContent = userEmail;
        }
    }
    
    // Profile dropdown functionality
    function toggleProfileDropdown() {
        const profileMenu = document.getElementById('profile-menu');
        const profileTrigger = document.querySelector('.profile-trigger');
        
        if (profileMenu && profileTrigger) {
            profileMenu.classList.toggle('show');
            profileTrigger.classList.toggle('active');
            
            // Update profile display when dropdown opens
            if (profileMenu.classList.contains('show')) {
                updateProfileDisplay();
            }
        }
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const profileDropdown = document.querySelector('.profile-dropdown');
        const profileMenu = document.getElementById('profile-menu');
        const profileTrigger = document.querySelector('.profile-trigger');
        
        if (profileDropdown && !profileDropdown.contains(event.target)) {
            if (profileMenu) profileMenu.classList.remove('show');
            if (profileTrigger) profileTrigger.classList.remove('active');
        }
    });
    
    // Profile Management Functions
    function showProfileSettings() {
        const modal = document.getElementById('profileModal');
        if (modal) {
            // Load current profile data
            loadProfileData();
            modal.style.display = 'flex';
        }
    }

    function closeProfileModal() {
        const modal = document.getElementById('profileModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    function showAccountSettings() {
        const modal = document.getElementById('accountModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    function closeAccountModal() {
        const modal = document.getElementById('accountModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    function showMyListings() {
        const modal = document.getElementById('listingsModal');
        if (modal) {
            loadModalListings();
            modal.style.display = 'flex';
        }
    }

    function closeListingsModal() {
        const modal = document.getElementById('listingsModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    function confirmLogout() {
        if (confirm('Are you sure you want to logout?')) {
            // Clear sessionStorage
            sessionStorage.clear();
            
            // Show loading state
            const logoutBtn = document.querySelector('.logout-button');
            const logoutAction = document.querySelector('.logout-action');
            if (logoutBtn) {
                logoutBtn.textContent = 'Logging out...';
                logoutBtn.disabled = true;
            }
            if (logoutAction) {
                logoutAction.innerHTML = '<span class="action-icon">⏳</span><span>Logging out...</span>';
            }
            
            // Update navigation immediately
            updateNavigation();
            
            // Redirect to logout
            window.location.href = '/logout';
        }
    }

    // Load profile data
    function loadProfileData() {
        // Get user data from session or use defaults
        const profileData = {
            name: sessionStorage.getItem('userName') || 'User',
            email: sessionStorage.getItem('userEmail') || 'user@example.com',
            phone: sessionStorage.getItem('userPhone') || '+91 9876543210',
            location: sessionStorage.getItem('userLocation') || 'India',
            bio: sessionStorage.getItem('userBio') || 'Farming enthusiast'
        };
        
        const nameField = document.getElementById('profile-name');
        const emailField = document.getElementById('profile-email');
        const phoneField = document.getElementById('profile-phone');
        const locationField = document.getElementById('profile-location');
        const bioField = document.getElementById('profile-bio');
        
        if (nameField) nameField.value = profileData.name;
        if (emailField) emailField.value = profileData.email;
        if (phoneField) phoneField.value = profileData.phone;
        if (locationField) locationField.value = profileData.location;
        if (bioField) bioField.value = profileData.bio;
    }

    // Load modal listings with stats
    function loadModalListings() {
        // This would load user's listings in a real app
        const modalGrid = document.getElementById('modal-listings-grid');
        if (modalGrid) {
            modalGrid.innerHTML = '<p>Your listings will appear here.</p>';
        }
    }

    // Market News Functionality
    function showMarketNews() {
        const marketSection = document.getElementById('market-news-section');
        const marketBtn = document.getElementById('market-btn');
        const btnText = marketBtn.querySelector('.btn-text');
        
        if (marketSection && marketBtn && btnText) {
            if (marketSection.style.display === 'none') {
                marketSection.style.display = 'block';
                btnText.textContent = 'Hide Updates';
                marketBtn.classList.add('active');
            } else {
                marketSection.style.display = 'none';
                btnText.textContent = 'Market Updates';
                marketBtn.classList.remove('active');
            }
        }
    }

    // Tab Switching Functionality
    function switchTab(tabName) {
        // Remove active class from all buttons
        const allButtons = document.querySelectorAll('.action-btn');
        allButtons.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to clicked button
        const activeButton = document.getElementById(tabName + '-tab');
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Hide all tab contents
        const sellContent = document.getElementById('sell-content');
        const buyContent = document.getElementById('buy-content');
        
        if (sellContent) sellContent.style.display = 'none';
        if (buyContent) buyContent.style.display = 'none';
        
        // Show selected tab content
        if (tabName === 'sell' && sellContent) {
            sellContent.style.display = 'block';
        } else if (tabName === 'buy' && buyContent) {
            buyContent.style.display = 'block';
        }
    }

    // Make functions globally accessible
    window.toggleProfileDropdown = toggleProfileDropdown;
    window.showProfileSettings = showProfileSettings;
    window.closeProfileModal = closeProfileModal;
    window.showAccountSettings = showAccountSettings;
    window.closeAccountModal = closeAccountModal;
    window.showMyListings = showMyListings;
    window.closeListingsModal = closeListingsModal;
    window.confirmLogout = confirmLogout;
    window.updateNavigation = updateNavigation;
    window.showMarketNews = showMarketNews;
    window.switchTab = switchTab;
    
    // Update navigation on page load
    updateNavigation();
    
    // Also update navigation when returning from logout
    if (window.location.pathname === '/' && !sessionStorage.getItem('userEmail')) {
        // User is on home page and not logged in, ensure navigation is correct
        updateNavigation();
    }
    
    // Also update navigation after a short delay to ensure user data is loaded
    setTimeout(() => {
        updateNavigation();
    }, 100);
    
    // Force profile dropdown to show on booking page after a longer delay
    setTimeout(() => {
        if (window.location.pathname.includes('/booking')) {
            const profileDropdown = document.getElementById('profile-dropdown');
            const loginBtn = document.getElementById('login-nav-link');
            const signupBtn = document.getElementById('signup-nav-link');
            
            if (profileDropdown && loginBtn && signupBtn) {
                profileDropdown.style.display = 'block';
                loginBtn.style.display = 'none';
                signupBtn.style.display = 'none';
                updateProfileDisplay();
            }
        }
    }, 500);
    
    // Add logout confirmation
    const logoutBtn = document.getElementById('logout-nav-link');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (confirm('Are you sure you want to logout?')) {
                // Clear sessionStorage
                sessionStorage.clear();
                
                // Show loading state
                this.textContent = 'Logging out...';
                this.style.pointerEvents = 'none';
                
                // Update navigation immediately
                updateNavigation();
                
                // Redirect to logout
                window.location.href = '/logout';
            }
        });
    }
    
    // Update navigation when page changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                updateNavigation();
            }
        });
    });
    
    // Observe changes to page elements
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        observer.observe(page, { attributes: true, attributeFilter: ['class'] });
    });
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href && href !== '#' && href.startsWith('#')) {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// Add hover effects to navigation links
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });

    // Add animation to feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 25px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 5px 20px rgba(0,0,0,0.1)';
        });
    });
});

// Responsive form centering and window resize handling
function centerForms() {
    const loginPage = document.querySelector('.login-page');
    const signupPage = document.querySelector('.signup-page');
    const forms = [loginPage, signupPage];
    
    forms.forEach(page => {
        if (page) {
            const formContainer = page.querySelector('.form-container');
            if (formContainer) {
                // Reset any inline styles
                formContainer.style.margin = '0 auto';
                formContainer.style.transform = 'translateY(0)';
                
                // Ensure proper centering
                page.style.display = 'flex';
                page.style.alignItems = 'center';
                page.style.justifyContent = 'center';
                page.style.minHeight = '100vh';
            }
        }
    });
}

// Handle window resize events
function handleResize() {
    centerForms();
    
    // Add smooth transition during resize
    const forms = document.querySelectorAll('.form-container');
    forms.forEach(form => {
        form.style.transition = 'all 0.3s ease';
    });
    
    // Remove transition after resize is complete
    setTimeout(() => {
        forms.forEach(form => {
            form.style.transition = '';
        });
    }, 300);
}

// Initialize responsive behavior
document.addEventListener('DOMContentLoaded', function() {
    centerForms();
    
    // Add resize event listener with debouncing
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 100);
    });
    
    // Handle orientation change on mobile devices
    window.addEventListener('orientationchange', function() {
        setTimeout(handleResize, 500);
    });
});

// Ensure forms are centered on page load
window.addEventListener('load', centerForms);
