// Profile management functionality
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

// Make function globally accessible
window.toggleProfileDropdown = toggleProfileDropdown;

// Update profile display with current data
function updateProfileDisplay() {
    const userName = sessionStorage.getItem('userName') || 'Student';
    const userEmail = sessionStorage.getItem('userEmail') || 'student@example.com';
    
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

// Update profile initials
function updateProfileInitials(username) {
    const initials = username ? username.charAt(0).toUpperCase() : 'U';
    const profileInitials = document.querySelectorAll('#profile-initial, #profile-initial-large');
    profileInitials.forEach(el => {
        if (el) el.textContent = initials;
    });
    
    // Update username and email displays
    const usernameDisplay = document.getElementById('username-display-large');
    const userEmail = document.getElementById('user-email');
    
    if (usernameDisplay) {
        usernameDisplay.textContent = username || 'User';
    }
    if (userEmail) {
        userEmail.textContent = sessionStorage.getItem('userEmail') || 'user@example.com';
    }
}

// Initialize profile data
function initializeProfileData() {
    // Check if user is logged in (has session data)
    const isLoggedIn = document.body.classList.contains('logged-in') || 
                      sessionStorage.getItem('userEmail') || 
                      window.location.pathname.includes('/booking');
    
    if (isLoggedIn) {
        // Update profile display
        const userName = sessionStorage.getItem('userName') || 'Farmer';
        const userEmail = sessionStorage.getItem('userEmail') || 'farmer@example.com';
        
        updateProfileInitials(userName);
        
        // Store in session storage if not already there
        if (!sessionStorage.getItem('userEmail')) {
            sessionStorage.setItem('userEmail', userEmail);
            sessionStorage.setItem('userName', userName);
        }
    }
}

// Logout functionality
function confirmLogout() {
    if (confirm('Are you sure you want to logout?')) {
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
        
        // Redirect to logout
        window.location.href = '/logout';
    }
}

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

// Make functions globally accessible
window.showProfileSettings = showProfileSettings;
window.closeProfileModal = closeProfileModal;
window.showAccountSettings = showAccountSettings;
window.closeAccountModal = closeAccountModal;
window.showMyListings = showMyListings;
window.closeListingsModal = closeListingsModal;
window.confirmLogout = confirmLogout;

// Load profile data
function loadProfileData() {
    // Get user data from session or use defaults
    const profileData = {
        name: sessionStorage.getItem('userName') || 'Farmer',
        email: sessionStorage.getItem('userEmail') || 'user@example.com',
        phone: sessionStorage.getItem('userPhone') || '+91 9876543210',
        location: sessionStorage.getItem('userLocation') || 'India',
        bio: sessionStorage.getItem('userBio') || 'Farming enthusiast'
    };
    
    document.getElementById('profile-name').value = profileData.name;
    document.getElementById('profile-email').value = profileData.email;
    document.getElementById('profile-phone').value = profileData.phone;
    document.getElementById('profile-location').value = profileData.location;
    document.getElementById('profile-bio').value = profileData.bio;
}

// Load modal listings with stats
function loadModalListings() {
    const myCrops = sampleCrops.filter(crop => crop.seller === 'You');
    const modalGrid = document.getElementById('modal-listings-grid');
    
    // Update stats
    document.getElementById('total-listings').textContent = myCrops.length;
    document.getElementById('active-listings').textContent = myCrops.length;
    document.getElementById('total-value').textContent = `₹${myCrops.reduce((sum, crop) => sum + crop.totalPrice, 0).toLocaleString()}`;
    
    // Clear and populate grid
    modalGrid.innerHTML = '';
    myCrops.forEach(crop => {
        const listingCard = createMyListingCard(crop);
        modalGrid.appendChild(listingCard);
    });
}

// Profile form submission
document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('profile-name').value,
                email: document.getElementById('profile-email').value,
                phone: document.getElementById('profile-phone').value,
                location: document.getElementById('profile-location').value,
                bio: document.getElementById('profile-bio').value
            };
            
            // In a real app, this would send to backend
            console.log('Profile updated:', formData);
            alert('Profile updated successfully!');
            closeProfileModal();
        });
    }
    
    // Account form submission
    const accountForm = document.getElementById('accountForm');
    if (accountForm) {
        accountForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-new-password').value;
            
            if (newPassword !== confirmPassword) {
                alert('New passwords do not match!');
                return;
            }
            
            if (newPassword.length < 6) {
                alert('New password must be at least 6 characters long!');
                return;
            }
            
            // In a real app, this would send to backend
            console.log('Password updated');
            alert('Password updated successfully!');
            closeAccountModal();
            
            // Clear form
            accountForm.reset();
        });
    }
    
    // Close modals when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
});
