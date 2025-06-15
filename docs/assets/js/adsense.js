/**
 * Google AdSense Configuration for dbterd Documentation
 *
 * Instructions for setup:
 * 1. Replace 'ca-pub-XXXXXXXXXX' with your actual AdSense publisher ID
 * 2. Apply for Google AdSense at https://www.google.com/adsense/
 * 3. Get approved and configure ad units in AdSense dashboard
 * 4. Update the publisher ID in this file and main.html template
 */

// Configuration - AdSense publisher ID
const ADSENSE_PUBLISHER_ID = 'ca-pub-9818368894527523';

// Initialize Google AdSense Auto Ads
(function() {
    // Only load ads in production environment
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('AdSense disabled in development environment');
        return;
    }

    // Load AdSense script
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_PUBLISHER_ID}`;
    script.crossOrigin = 'anonymous';

    // Error handling
    script.onerror = function() {
        console.warn('Failed to load Google AdSense');
    };

    // Initialize auto ads when script loads
    script.onload = function() {
        try {
            (adsbygoogle = window.adsbygoogle || []).push({
                google_ad_client: ADSENSE_PUBLISHER_ID,
                enable_page_level_ads: true
            });
            console.log('Google AdSense Auto Ads initialized');
        } catch (error) {
            console.warn('AdSense initialization error:', error);
        }
    };

    document.head.appendChild(script);
})();

// Function to initialize manual ad units
function initializeAdUnit() {
    if (typeof adsbygoogle !== 'undefined') {
        try {
            (adsbygoogle = window.adsbygoogle || []).push({});
        } catch (error) {
            console.warn('Ad unit initialization error:', error);
        }
    }
}

// Auto-initialize ad units when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Find all ad containers and initialize them
    const adContainers = document.querySelectorAll('.adsbygoogle');
    adContainers.forEach(initializeAdUnit);
});

// Function to close the ad (temporarily for current session)
function closeAd() {
    const adContainer = document.getElementById('sidebar-ad');
    if (adContainer) {
        // Add fade out animation
        adContainer.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        adContainer.style.opacity = '0';
        adContainer.style.transform = 'translateY(20px)';

        // Remove from DOM after animation
        setTimeout(() => {
            adContainer.style.display = 'none';
        }, 300);

        console.log('Advertisement closed by user (will show again on page refresh)');
    }
}

// Export for manual use if needed
window.dbterdAds = {
    initializeAdUnit: initializeAdUnit,
    publisherId: ADSENSE_PUBLISHER_ID,
    closeAd: closeAd
};

// Make closeAd globally available
window.closeAd = closeAd;
