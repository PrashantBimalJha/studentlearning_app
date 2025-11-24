// Crop Marketplace functionality
// Note: Crop data is now fetched from the database via API calls

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
    
    cropsGrid.innerHTML = '<div class="loading">Loading crops...</div>';
    
    // Fetch crops from API
    fetch('/api/crops')
        .then(response => response.json())
        .then(data => {
            cropsGrid.innerHTML = '';
            
            if (data.success && data.crops.length > 0) {
                data.crops.forEach(crop => {
                    const cropCard = createCropCard(crop);
                    cropsGrid.appendChild(cropCard);
                });
            } else {
                cropsGrid.innerHTML = '<div class="no-crops">No crops available at the moment.</div>';
            }
            
            // Re-attach event listeners for new crop cards
            attachEventListeners();
        })
        .catch(error => {
            console.error('Error loading crops:', error);
            cropsGrid.innerHTML = '<div class="error">Error loading crops. Please try again.</div>';
        });
}

// Create crop card element
function createCropCard(crop) {
    const card = document.createElement('div');
    card.className = 'crop-card';
    
    // Get appropriate emoji based on category
    let emoji = '📚';
    if (crop.category === 'grains') emoji = '🌾';
    else if (crop.category === 'vegetables') emoji = '🥕';
    else if (crop.category === 'fruits') emoji = '🍎';
    else if (crop.category === 'spices') emoji = '🌶️';
    
    card.innerHTML = `
        <div class="crop-image ${crop.category}">
            <div class="crop-emoji">${emoji}</div>
        </div>
        <div class="crop-info">
            <div class="crop-name">${crop.name}</div>
            <div class="crop-details">
                <span class="crop-price">₹${crop.total_price.toLocaleString()}</span>
                <span class="crop-quantity">${crop.quantity} kg</span>
            </div>
            <div class="crop-location">📍 ${crop.location}</div>
            <div class="crop-description">${crop.description || 'No description available'}</div>
            <div class="crop-actions">
                <button class="contact-btn" onclick="contactSeller('${crop.seller_phone || ''}', '${crop.name}')">
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
    
    myListingsGrid.innerHTML = '<div class="loading">Loading your listings...</div>';
    
    // Fetch user's crops from API
    fetch('/api/crops')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.crops.length > 0) {
                myListingsGrid.style.display = 'grid';
                noListings.style.display = 'none';
                myListingsGrid.innerHTML = '';
                
                data.crops.forEach(crop => {
                    const listingCard = createMyListingCard(crop);
                    myListingsGrid.appendChild(listingCard);
                });
            } else {
                myListingsGrid.style.display = 'none';
                noListings.style.display = 'block';
            }
            
            // Re-attach event listeners for new listing cards
            attachEventListeners();
        })
        .catch(error => {
            console.error('Error loading listings:', error);
            myListingsGrid.innerHTML = '<div class="error">Error loading listings. Please try again.</div>';
        });
}

// Create my listing card
function createMyListingCard(crop) {
    const card = document.createElement('div');
    card.className = 'my-listing-card';
    
    // Get appropriate emoji based on category
    let emoji = '📚';
    if (crop.category === 'grains') emoji = '🌾';
    else if (crop.category === 'vegetables') emoji = '🥕';
    else if (crop.category === 'fruits') emoji = '🍎';
    else if (crop.category === 'spices') emoji = '🌶️';
    
    card.innerHTML = `
        <div class="my-listing-header">
            <div class="my-listing-name">${emoji} ${crop.name}</div>
            <div class="my-listing-status">${crop.is_active ? 'Active' : 'Inactive'}</div>
        </div>
        <div class="my-listing-details">
            <span class="my-listing-price">₹${crop.total_price.toLocaleString()}</span>
            <span class="my-listing-quantity">${crop.quantity} kg</span>
        </div>
        <div class="my-listing-location">📍 ${crop.location}</div>
        <div class="my-listing-actions">
            <button class="edit-btn" onclick="editListing('${crop._id}')">✏️ Edit</button>
            <button class="delete-btn" onclick="deleteListing('${crop._id}')">🗑️ Delete</button>
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
    // For now, just show an alert. In a real app, you'd open an edit modal
    alert('Edit functionality will be implemented. Crop ID: ' + cropId);
}

// Delete listing
function deleteListing(cropId) {
    if (confirm('Are you sure you want to delete this listing?')) {
        fetch(`/api/crops/${cropId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Listing deleted successfully!');
                // Refresh both my listings and buy tab
                loadMyListings();
                if (document.getElementById('buy-content') && !document.getElementById('buy-content').classList.contains('hidden')) {
                    loadCrops();
                }
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the listing.');
        });
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
