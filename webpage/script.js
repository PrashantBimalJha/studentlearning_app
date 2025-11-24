// Main application script - imports all modules
// This file serves as the main entry point for all JavaScript functionality

// Import validation functions
// (These are defined in validation.js but included here for compatibility)

// Enhanced password validation functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isStrongPassword(password) {
    // At least 6 characters, one uppercase, one lowercase, one number
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasMinimumLength = password.length >= 6;
    
    return hasUpperCase && hasLowerCase && hasNumbers && hasMinimumLength;
}

// Function to show error messages
function showError(message) {
    // Remove any existing error messages
    clearErrorMessages();
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = 'color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; margin: 10px 0; border-radius: 4px; text-align: center;';
    errorDiv.textContent = message;
    
    // Insert error message after the form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
    signupForm.parentNode.insertBefore(errorDiv, signupForm.nextSibling);
    }
}

// Function to clear error messages
function clearErrorMessages() {
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(error => error.remove());
}

// Function to show success messages
function showSuccess(message) {
    // Remove any existing messages
    clearErrorMessages();
    clearSuccessMessages();
    
    // Create success message element
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.style.cssText = 'color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; margin: 10px 0; border-radius: 4px; text-align: center; font-weight: bold;';
    successDiv.textContent = message;
    
    // Insert success message after the form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.parentNode.insertBefore(successDiv, signupForm.nextSibling);
    }
}

// Function to clear success messages
function clearSuccessMessages() {
    const existingSuccess = document.querySelectorAll('.success-message');
    existingSuccess.forEach(success => success.remove());
}

// Sample crops data
const sampleCrops = [
    {
        id: 1,
        name: 'Wheat',
        emoji: '🌾',
        type: 'wheat',
        quantity: 500,
        pricePerKg: 25,
        totalPrice: 12500,
        location: 'Punjab, India',
        description: 'High quality wheat, freshly harvested. Organic learning methods used.',
        contact: '+91 98765 43210',
        harvestDate: '2024-01-15',
        seller: 'Farmer Singh'
    },
    {
        id: 2,
        name: 'Tomatoes',
        emoji: '🍅',
        type: 'tomatoes',
        quantity: 200,
        pricePerKg: 40,
        totalPrice: 8000,
        location: 'Maharashtra, India',
        description: 'Fresh red tomatoes, perfect for cooking and salads.',
        contact: '+91 98765 43211',
        harvestDate: '2024-01-20',
        seller: 'Green Farm Co.'
    },
    {
        id: 3,
        name: 'Rice',
        emoji: '🌾',
        type: 'rice',
        quantity: 300,
        pricePerKg: 35,
        totalPrice: 10500,
        location: 'West Bengal, India',
        description: 'Premium basmati rice, long grain variety.',
        contact: '+91 98765 43212',
        harvestDate: '2024-01-18',
        seller: 'Rice Fields Ltd.'
    },
    {
        id: 4,
        name: 'Carrots',
        emoji: '🥕',
        type: 'carrots',
        quantity: 150,
        pricePerKg: 30,
        totalPrice: 4500,
        location: 'Himachal Pradesh, India',
        description: 'Fresh organic carrots, rich in vitamins.',
        contact: '+91 98765 43213',
        harvestDate: '2024-01-22',
        seller: 'Mountain Fresh'
    },
    {
        id: 5,
        name: 'Corn',
        emoji: '🌽',
        type: 'corn',
        quantity: 400,
        pricePerKg: 20,
        totalPrice: 8000,
        location: 'Karnataka, India',
        description: 'Sweet corn, perfect for roasting or boiling.',
        contact: '+91 98765 43214',
        harvestDate: '2024-01-25',
        seller: 'Corn King'
    },
    {
        id: 6,
        name: 'Potatoes',
        emoji: '🥔',
        type: 'potatoes',
        quantity: 600,
        pricePerKg: 15,
        totalPrice: 9000,
        location: 'Uttar Pradesh, India',
        description: 'Fresh potatoes, great for all cooking purposes.',
        contact: '+91 98765 43215',
        harvestDate: '2024-01-28',
        seller: 'Potato Paradise'
    }
];

// Tab Switching Functionality
function switchTab(tabName) {
    // Update tab buttons
    const sellTab = document.getElementById('sell-tab');
    const buyTab = document.getElementById('buy-tab');
    const sellContent = document.getElementById('sell-content');
    const buyContent = document.getElementById('buy-content');
    
    if (tabName === 'sell') {
        sellTab.classList.add('active');
        buyTab.classList.remove('active');
        sellContent.classList.remove('hidden');
        buyContent.classList.add('hidden');
        
        // Load user's listings when switching to sell tab
        loadMyListings();
    } else if (tabName === 'buy') {
        buyTab.classList.add('active');
        sellTab.classList.remove('active');
        buyContent.classList.remove('hidden');
        sellContent.classList.add('hidden');
        
        // Load crops when switching to buy tab
        loadCrops();
    }
}

// Load crops for buy tab
function loadCrops() {
    const cropsGrid = document.getElementById('crops-grid');
    if (!cropsGrid) return;
    
    cropsGrid.innerHTML = '';
    
    sampleCrops.forEach(crop => {
        const cropCard = createCropCard(crop);
        cropsGrid.appendChild(cropCard);
    });
    
    // Re-attach event listeners for new crop cards
    attachEventListeners();
}

// Create crop card element
function createCropCard(crop) {
    const card = document.createElement('div');
    card.className = 'crop-card';
    card.innerHTML = `
        <div class="crop-image ${crop.type}">
            <div class="crop-emoji">${crop.emoji}</div>
        </div>
        <div class="crop-info">
            <div class="crop-name">${crop.name}</div>
            <div class="crop-details">
                <span class="crop-price">₹${crop.totalPrice.toLocaleString()}</span>
                <span class="crop-quantity">${crop.quantity} kg</span>
            </div>
            <div class="crop-location">📍 ${crop.location}</div>
            <div class="crop-description">${crop.description}</div>
            <div class="crop-actions">
                <button class="contact-btn" onclick="contactSeller('${crop.contact}', '${crop.name}')">
                    📞 Contact
                </button>
                <button class="interest-btn" onclick="toggleInterest(this)">
                    ❤️ Interested
                </button>
            </div>
        </div>
    `;
    return card;
}

// Contact seller function
function contactSeller(contact, cropName) {
    const message = `Hi! I'm interested in buying your ${cropName}. Please contact me back.`;
    const whatsappUrl = `https://wa.me/${contact.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(message)}`;
    
    // Try to open WhatsApp, fallback to alert
    if (confirm(`Contact ${cropName} seller?\n\nPhone: ${contact}\n\nOpen WhatsApp?`)) {
        window.open(whatsappUrl, '_blank');
    }
}

// Toggle interest function
function toggleInterest(button) {
    button.classList.toggle('interested');
    if (button.classList.contains('interested')) {
        button.textContent = '❤️ Interested';
        button.style.background = '#28a745';
        button.style.color = 'white';
        
        // Add to favorites
        const cropCard = button.closest('.crop-card');
        const cropName = cropCard.querySelector('.crop-name').textContent;
        addToFavorites(cropName);
    } else {
        button.textContent = '🤍 Interested';
        button.style.background = '#f8f9fa';
        button.style.color = '#28a745';
        
        // Remove from favorites
        const cropCard = button.closest('.crop-card');
        const cropName = cropCard.querySelector('.crop-name').textContent;
        removeFromFavorites(cropName);
    }
}

// Filter crops based on search term
function filterCrops(searchTerm) {
    const cropCards = document.querySelectorAll('.crop-card');
    cropCards.forEach(card => {
        const cropName = card.querySelector('.crop-name').textContent.toLowerCase();
        const cropDescription = card.querySelector('.crop-description').textContent.toLowerCase();
        const cropLocation = card.querySelector('.crop-location').textContent.toLowerCase();
        
        const matches = cropName.includes(searchTerm) || 
                      cropDescription.includes(searchTerm) || 
                      cropLocation.includes(searchTerm);
        
        card.style.display = matches ? 'block' : 'none';
    });
}

// Show favorites
function showFavorites() {
    const interestedCrops = document.querySelectorAll('.interest-btn.interested');
    if (interestedCrops.length === 0) {
        alert('You haven\'t marked any crops as interested yet!');
        return;
    }
    
    const favoriteNames = Array.from(interestedCrops).map(btn => {
        const cropCard = btn.closest('.crop-card');
        return cropCard.querySelector('.crop-name').textContent;
    });
    
    alert(`Your interested crops:\n\n${favoriteNames.join('\n')}`);
}

// Add to favorites (local storage)
function addToFavorites(cropName) {
    let favorites = JSON.parse(localStorage.getItem('cropFavorites') || '[]');
    if (!favorites.includes(cropName)) {
        favorites.push(cropName);
        localStorage.setItem('cropFavorites', JSON.stringify(favorites));
    }
}

// Remove from favorites
function removeFromFavorites(cropName) {
    let favorites = JSON.parse(localStorage.getItem('cropFavorites') || '[]');
    favorites = favorites.filter(name => name !== cropName);
    localStorage.setItem('cropFavorites', JSON.stringify(favorites));
}

// Filter crops by type
function filterCropsByType(cropType) {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.value = cropType;
        filterCrops(cropType);
    }
}

// Load user's own listings
function loadMyListings() {
    const myListingsGrid = document.getElementById('my-listings-grid');
    const noListings = document.getElementById('no-listings');
    
    if (!myListingsGrid || !noListings) return;
    
    // Filter crops where seller is 'You'
    const myCrops = sampleCrops.filter(crop => crop.seller === 'You');
    
    if (myCrops.length === 0) {
        myListingsGrid.style.display = 'none';
        noListings.style.display = 'block';
        return;
    }
    
    myListingsGrid.style.display = 'grid';
    noListings.style.display = 'none';
    myListingsGrid.innerHTML = '';
    
    myCrops.forEach(crop => {
        const listingCard = createMyListingCard(crop);
        myListingsGrid.appendChild(listingCard);
    });
    
    // Re-attach event listeners for new listing cards
    attachEventListeners();
}

// Create my listing card
function createMyListingCard(crop) {
    const card = document.createElement('div');
    card.className = 'my-listing-card';
    card.innerHTML = `
        <div class="my-listing-header">
            <div class="my-listing-name">${crop.emoji} ${crop.name}</div>
            <div class="my-listing-status">Active</div>
        </div>
        <div class="my-listing-details">
            <span class="my-listing-price">₹${crop.totalPrice.toLocaleString()}</span>
            <span class="my-listing-quantity">${crop.quantity} kg</span>
        </div>
        <div class="my-listing-location">📍 ${crop.location}</div>
        <div class="my-listing-actions">
            <button class="edit-btn" onclick="editListing(${crop.id})">✏️ Edit</button>
            <button class="delete-btn" onclick="deleteListing(${crop.id})">🗑️ Delete</button>
        </div>
    `;
    return card;
}

// Refresh my listings
function refreshMyListings() {
    loadMyListings();
    alert('Listings refreshed!');
}

// Edit listing
function editListing(cropId) {
    const crop = sampleCrops.find(c => c.id === cropId);
    if (!crop) return;
    
    const newPrice = prompt(`Edit price per kg for ${crop.name} (current: ₹${crop.pricePerKg}):`, crop.pricePerKg);
    if (newPrice && !isNaN(newPrice) && newPrice > 0) {
        crop.pricePerKg = parseInt(newPrice);
        crop.totalPrice = crop.quantity * crop.pricePerKg;
        
        // Refresh both my listings and buy tab
        loadMyListings();
        if (document.getElementById('buy-content').classList.contains('hidden') === false) {
            loadCrops();
        }
        
        alert('Listing updated successfully!');
    }
}

// Delete listing
function deleteListing(cropId) {
    if (confirm('Are you sure you want to delete this listing?')) {
        const index = sampleCrops.findIndex(c => c.id === cropId);
        if (index > -1) {
            sampleCrops.splice(index, 1);
            
            // Refresh both my listings and buy tab
            loadMyListings();
            if (document.getElementById('buy-content').classList.contains('hidden') === false) {
                loadCrops();
            }
            
            alert('Listing deleted successfully!');
        }
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
        bio: sessionStorage.getItem('userBio') || 'Learning enthusiast'
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
    const userName = sessionStorage.getItem('userName') || 'Farmer';
    const userEmail = sessionStorage.getItem('userEmail') || 'farmer@example.com';
    
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

// Function to re-attach event listeners for dynamically loaded content
function attachEventListeners() {
    // Add crop action buttons functionality
    const contactButtons = document.querySelectorAll('.contact-btn');
    contactButtons.forEach(btn => {
        btn.removeEventListener('click', handleContactClick);
        btn.addEventListener('click', handleContactClick);
    });
    
    const interestButtons = document.querySelectorAll('.interest-btn');
    interestButtons.forEach(btn => {
        btn.removeEventListener('click', handleInterestClick);
        btn.addEventListener('click', handleInterestClick);
    });
    
    // Add edit and delete buttons functionality
    const editButtons = document.querySelectorAll('.edit-btn');
    editButtons.forEach(btn => {
        btn.removeEventListener('click', handleEditClick);
        btn.addEventListener('click', handleEditClick);
    });
    
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(btn => {
        btn.removeEventListener('click', handleDeleteClick);
        btn.addEventListener('click', handleDeleteClick);
    });
}

// Event handler functions
function handleContactClick(e) {
    e.preventDefault();
    e.stopPropagation();
    const cropCard = this.closest('.crop-card');
    const cropName = cropCard.querySelector('.crop-name').textContent;
    const contact = cropCard.querySelector('.crop-contact')?.textContent || 'Contact not available';
    contactSeller(contact, cropName);
}

function handleInterestClick(e) {
    e.preventDefault();
    e.stopPropagation();
    toggleInterest(this);
}

function handleEditClick(e) {
    e.preventDefault();
    e.stopPropagation();
    const cropId = parseInt(this.getAttribute('onclick').match(/\d+/)[0]);
    editListing(cropId);
}

function handleDeleteClick(e) {
    e.preventDefault();
    e.stopPropagation();
    const cropId = parseInt(this.getAttribute('onclick').match(/\d+/)[0]);
    deleteListing(cropId);
}

// Main application initialization
document.addEventListener('DOMContentLoaded', function() {
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
    
    // Form validation for signup
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.querySelector('input[name="email"]').value;
            const phone = document.querySelector('input[name="phone"]').value;
            const password = document.querySelector('input[name="password"]').value;
            const confirmPassword = document.querySelector('input[name="confirm_password"]').value;
            
            // Clear any previous error messages
            clearErrorMessages();
            
            // Validation
            if (!email || !phone || !password || !confirmPassword) {
                showError('All fields are required!');
                return false;
            }
            
            if (!isValidEmail(email)) {
                showError('Please enter a valid email address!');
                return false;
            }
            
            if (password.length < 6) {
                showError('Password must be at least 6 characters long!');
                return false;
            }
            
            if (!isStrongPassword(password)) {
                showError('Password must contain at least one uppercase letter, one lowercase letter, and one number!');
                return false;
            }
            
            if (password !== confirmPassword) {
                showError('Passwords do not match!');
                return false;
            }
            
            // Show loading state
            const submitBtn = signupForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Creating Account...';
            submitBtn.disabled = true;
            
            // If validation passes, submit the form
            signupForm.submit();
        });
    }

    // Real-time password matching validation
    const passwordInput = document.querySelector('input[name="password"]');
    const confirmPasswordInput = document.querySelector('input[name="confirm_password"]');
    const emailInput = document.querySelector('input[name="email"]');
    
    if (passwordInput && confirmPasswordInput) {
        function validatePasswords() {
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;
            
            // Clear previous error messages
            clearErrorMessages();
            
            if (password && password.length < 6) {
                showError('Password must be at least 6 characters long!');
            } else if (password && !isStrongPassword(password)) {
                showError('Password must contain at least one uppercase letter, one lowercase letter, and one number!');
            } else if (confirmPassword && password !== confirmPassword) {
                showError('Passwords do not match!');
            }
        }
        
        // Add event listeners for real-time validation
        passwordInput.addEventListener('input', validatePasswords);
        confirmPasswordInput.addEventListener('input', validatePasswords);
    }
    
    // Real-time email validation
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            const email = emailInput.value;
            clearErrorMessages();
            
            if (email && !isValidEmail(email)) {
                showError('Please enter a valid email address!');
            }
        });
    }

    // Add loading states to forms (only for forms without custom handlers)
    document.querySelectorAll('form').forEach(form => {
        // Skip forms that have custom handlers (like crop-form)
        if (form.id === 'crop-form') {
            return;
        }
        
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Processing...';
                submitBtn.disabled = true;
            }
        });
    });
    
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
                const cropType = storyName.textContent.toLowerCase();
                if (cropType === 'your story') {
                    // Show user's own listings
                    showMyListings();
                } else {
                    // Filter crops by type
                    filterCropsByType(cropType);
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
    
    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            filterCrops(searchTerm);
        });
    }

    // Profile form submission
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

// Crop Marketplace Functionality
    // Set today's date as default for harvest date
    const today = new Date().toLocaleDateString('en-CA');
    const harvestDateInput = document.getElementById('harvest_date');
    if (harvestDateInput) {
        harvestDateInput.value = today;
    }

    // Sell form functionality
    const sellForm = document.getElementById('sell-form');
    const quantityInput = document.getElementById('quantity');
    const pricePerKgInput = document.getElementById('price_per_kg');
    const totalPriceDisplay = document.getElementById('total-price');
    const listCropButton = document.getElementById('list-crop-button');

    // Update total price when quantity or price changes
    function updateTotalPrice() {
        const quantity = quantityInput ? parseFloat(quantityInput.value) || 0 : 0;
        const pricePerKg = pricePerKgInput ? parseFloat(pricePerKgInput.value) || 0 : 0;
        const totalPrice = quantity * pricePerKg;
        
        if (totalPriceDisplay) {
            totalPriceDisplay.textContent = `Total Value: ₹${totalPrice.toLocaleString()}`;
        }
    }

    if (quantityInput) {
        quantityInput.addEventListener('input', updateTotalPrice);
    }
    if (pricePerKgInput) {
        pricePerKgInput.addEventListener('input', updateTotalPrice);
    }

    // Sell form submission - handle button click
    if (listCropButton) {
        listCropButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            const cropType = document.getElementById('crop_type').value;
            const quantity = document.getElementById('quantity').value;
            const pricePerKg = document.getElementById('price_per_kg').value;
            const harvestDate = document.getElementById('harvest_date').value;
            const location = document.getElementById('location').value;
            const description = document.getElementById('description').value;
            const contact = document.getElementById('contact').value;
            
            if (!cropType || !quantity || !pricePerKg || !harvestDate || !location || !contact) {
                alert('Please fill in all required fields!');
                return;
            }
            
            // Show loading state
            this.textContent = 'Listing Crop...';
            this.disabled = true;
            
            // Simulate listing process
            setTimeout(() => {
                // Show success message
                const successCard = document.getElementById('sell-success-card');
                if (successCard) {
                    successCard.style.display = 'block';
                    successCard.classList.remove('fade-out'); // Remove fade-out class if present
                    successCard.scrollIntoView({ behavior: 'smooth' });
                    
                    // Auto-hide success message after 5 seconds with fade-out animation
                    setTimeout(() => {
                        successCard.classList.add('fade-out');
                        // Hide completely after animation
                        setTimeout(() => {
                            successCard.style.display = 'none';
                        }, 500); // Match CSS transition duration
                    }, 5000);
                }
                
                // Reset form
                if (sellForm) {
                    sellForm.reset();
                }
                updateTotalPrice();
                
                // Reset button
                this.textContent = 'List My Crop';
                this.disabled = false;
                
                // Add to crops list (in real app, this would be sent to backend)
                const newCrop = {
                    id: Date.now(),
                    name: cropType.charAt(0).toUpperCase() + cropType.slice(1),
                    emoji: getCropEmoji(cropType),
                    type: cropType,
                    quantity: parseInt(quantity),
                    pricePerKg: parseInt(pricePerKg),
                    totalPrice: parseInt(quantity) * parseInt(pricePerKg),
                    location: location,
                    description: description || 'Fresh crop available for sale',
                    contact: contact,
                    harvestDate: harvestDate,
                    seller: 'You'
                };
                
                // Add to sample crops (in real app, this would be handled by backend)
                sampleCrops.unshift(newCrop);
                
                // Refresh my listings
                loadMyListings();
                
                // Show success message
                alert('🎉 Your crop has been listed successfully! It will appear in the Buy tab.');
                
                // Switch to buy tab to show the new crop
                setTimeout(() => {
                    switchTab('buy');
                }, 1000);
                
            }, 2000);
        });
    }

    // Get crop emoji based on type
    function getCropEmoji(type) {
        const emojiMap = {
            'wheat': '🌾',
            'rice': '🌾',
            'corn': '🌽',
            'tomatoes': '🍅',
            'potatoes': '🥔',
            'carrots': '🥕',
            'onions': '🧅',
            'spinach': '🥬',
            'cabbage': '🥬',
            'other': '📚'
        };
        return emojiMap[type] || '📚';
    }
});