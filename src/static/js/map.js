// Initialize map and controls
let map = L.map('map').setView([20.5937, 78.9629], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Add geocoding control with Nominatim provider
let geocoder = L.Control.Geocoder.nominatim();
L.Control.Geocoder({
    geocoder: geocoder,
    defaultMarkGeocode: false,
    placeholder: 'Search location...',
    errorMessage: 'Location not found.',
    showResultIcons: true,
    suggestMinLength: 3,
    suggestTimeout: 250,
    queryMinLength: 1
}).on('markgeocode', function(e) {
    if (selectedMarker) {
        map.removeLayer(selectedMarker);
    }
    selectedLocation = {
        lat: e.geocode.center.lat,
        lng: e.geocode.center.lng
    };
    selectedMarker = L.marker(e.geocode.center).addTo(map);
    map.fitBounds(e.geocode.bbox);
    fetchLocationData();
}).addTo(map);

// Add select location button
L.Control.SelectLocation = L.Control.extend({
    onAdd: function(map) {
        const button = L.DomUtil.create('button', 'select-location-btn');
        button.innerHTML = '<i class="fas fa-map-marker-alt"></i> Select Location';
        button.style.padding = '8px 16px';
        button.style.backgroundColor = '#4CAF50';
        button.style.color = 'white';
        button.style.border = 'none';
        button.style.borderRadius = '4px';
        button.style.cursor = 'pointer';
        button.style.margin = '10px';
        
        L.DomEvent.on(button, 'click', function() {
            if (map.selectingLocation) {
                map.selectingLocation = false;
                button.style.backgroundColor = '#4CAF50';
                map.off('click', onMapClick);
            } else {
                map.selectingLocation = true;
                button.style.backgroundColor = '#f44336';
                map.on('click', onMapClick);
            }
        });
        
        return button;
    }
});

let selectButton = new L.Control.SelectLocation({ position: 'topleft' }).addTo(map);

// Initialize variables for selected location
let selectedMarker = null;
let selectedLocation = null;

// Validate coordinates
function isValidCoordinate(lat, lng) {
    return lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
}

// Handle map click for location selection
function onMapClick(e) {
    if (selectedMarker) {
        map.removeLayer(selectedMarker);
    }
    
    selectedLocation = {
        lat: e.latlng.lat,
        lng: e.latlng.lng
    };
    
    selectedMarker = L.marker(e.latlng).addTo(map);
    fetchLocationData();
}

// Handle geocoding results
geocoder.on('markgeocode', function(e) {
    if (selectedMarker) {
        map.removeLayer(selectedMarker);
    }
    
    const center = e.geocode.center;
    selectedLocation = {
        lat: center.lat,
        lng: center.lng
    };
    
    selectedMarker = L.marker(center).addTo(map);
    map.fitBounds(e.geocode.bbox);
    
    // Fetch and display data for the selected location
    fetchLocationData();
});

// Fetch data for selected location
async function fetchLocationData() {
    if (!selectedLocation) {
        showError('Please select a location on the map first');
        return;
    }
    
    const loadingIndicator = document.getElementById('loading-indicator');
    const panels = ['carbon-panel', 'vegetation-panel', 'soil-panel'];
    
    // Clear previous data
    panels.forEach(panelId => {
        const panel = document.getElementById(panelId);
        if (panel) panel.innerHTML = '';
    });
    
    if (!loadingIndicator) {
        showError('Loading indicator not found. Please refresh the page.');
        return;
    }
    
    try {
        loadingIndicator.style.display = 'block';
        document.body.style.cursor = 'wait';
        
        // Validate coordinates
        if (!isValidCoordinate(selectedLocation.lat, selectedLocation.lng)) {
            throw new Error('Invalid coordinates selected');
        }
        
        const currentDate = new Date().toISOString().split('T')[0];
        const requestBody = {
            latitude: selectedLocation.lat,
            longitude: selectedLocation.lng,
            date: currentDate
        };
        
        const requestOptions = {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestBody)
        };
        
        // Fetch all data in parallel
        const [carbonResponse, vegetationResponse, soilResponse] = await Promise.all([
            fetch('/analyze/carbon', requestOptions).catch(error => ({ ok: false, error })),
            fetch('/vegetation-indices', requestOptions).catch(error => ({ ok: false, error })),
            fetch('/soil-moisture', requestOptions).catch(error => ({ ok: false, error }))
        ]);
        
        // Check response status and provide detailed error messages
        if (!carbonResponse.ok) throw new Error(carbonResponse.error?.message || `Carbon API error: ${carbonResponse.status}`);
        if (!vegetationResponse.ok) throw new Error(vegetationResponse.error?.message || `Vegetation API error: ${vegetationResponse.status}`);
        if (!soilResponse.ok) throw new Error(soilResponse.error?.message || `Soil API error: ${soilResponse.status}`);
        
        // Parse response data
        const [carbonData, vegetationData, soilData] = await Promise.all([
            carbonResponse.json(),
            vegetationResponse.json(),
            soilResponse.json()
        ]);
        
        // Update panels with data
        updateCarbonPanel(carbonData);
        updateVegetationPanel(vegetationData);
        updateSoilPanel(soilData);
        
        // Ensure carbon visualization is updated
        if (carbonData && typeof carbonData.carbon_footprint !== 'undefined') {
            updateCarbonVisualization(carbonData);
        }
        
    } catch (error) {
        console.error('Error fetching data:', error);
        const errorMessage = error.message || 'Failed to fetch location data. Please check your internet connection and try again.';
        showError(errorMessage);
        // Clear panels on error and show detailed message
        panels.forEach(panelId => {
            const panel = document.getElementById(panelId);
            if (panel) {
                panel.innerHTML = `<div class="error-message">${errorMessage}</div>`;
            }
        });
        // Add error state to marker
        if (selectedMarker) {
            selectedMarker.setIcon(L.icon({
                iconUrl: '/static/images/marker-error.svg',
                iconSize: [25, 41],
                iconAnchor: [12, 41]
            }));
        }
    } finally {
        loadingIndicator.style.display = 'none';
        document.body.style.cursor = 'default';
    }
}

// Initialize map layers
let carbonLayer = L.layerGroup().addTo(map);

// Add layer control
let baseMaps = {
    "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    })
};

let overlayMaps = {
    "Carbon Footprint": carbonLayer
};

L.control.layers(baseMaps, overlayMaps).addTo(map);

// Update carbon footprint visualization
function updateCarbonVisualization(data) {
    carbonLayer.clearLayers();
    
    // Create a circle with radius based on carbon footprint
    const radius = Math.max(data.carbon_footprint * 1000, 2000); // Scale for visibility
    const color = getCarbonIntensityColor(data.carbon_footprint);
    
    L.circle([selectedLocation.lat, selectedLocation.lng], {
        radius: radius,
        color: color,
        fillColor: color,
        fillOpacity: 0.3
    }).addTo(carbonLayer);
}

// Get color based on carbon intensity
function getCarbonIntensityColor(value) {
    return value > 8 ? '#d73027' :
           value > 6 ? '#fc8d59' :
           value > 4 ? '#fee08b' :
           value > 2 ? '#d9ef8b' :
                      '#91cf60';
}

// Update carbon footprint panel
function updateCarbonPanel(data) {
    if (!data) {
        showError('No carbon data received');
        return;
    }
    if (typeof data.carbon_footprint === 'undefined') {
        showError('Invalid carbon footprint data');
        return;
    }
    if (!data.contributing_factors) {
        showError('Missing contributing factors data');
        return;
    }
    
    const carbonPanel = document.getElementById('carbon-panel');
    if (!carbonPanel) {
        showError('Carbon panel element not found');
        return;
    }
    carbonPanel.innerHTML = `
        <h3>Carbon Footprint Analysis</h3>
        <div class="metric">
            <span class="label">Carbon Footprint:</span>
            <span class="value">${data.carbon_footprint.toFixed(2)} tons CO2/hectare</span>
        </div>
        <div class="metric">
            <span class="label">Risk Level:</span>
            <span class="value ${getCarbonRiskClass(data.carbon_footprint)}">${getCarbonRiskLevel(data.carbon_footprint)}</span>
        </div>
        ${data.contributing_factors ? `
        <div class="factors">
            <h4>Contributing Factors</h4>
            <div class="factor">
                <span class="label">Vegetation Index:</span>
                <span class="value">${data.contributing_factors.vegetation_index.toFixed(2)}</span>
            </div>
            <div class="factor">
                <span class="label">Land Use Change:</span>
                <span class="value">${data.contributing_factors.land_use_change.toFixed(2)}</span>
            </div>
            <div class="factor">
                <span class="label">Industrial Activity:</span>
                <span class="value">${data.contributing_factors.industrial_activity.toFixed(2)}</span>
            </div>
        </div>
        ` : ''}
    `;
    updateCarbonVisualization(data);
}

// Update vegetation panel
function updateVegetationPanel(data) {
    if (!data || typeof data.ndvi === 'undefined') {
        showError('Invalid vegetation data');
        return;
    }
    const vegetationPanel = document.getElementById('vegetation-panel');
    if (!vegetationPanel) {
        showError('Vegetation panel element not found');
        return;
    }
    vegetationPanel.innerHTML = `
        <h3>Vegetation Analysis</h3>
        <div class="metric">
            <span class="label">NDVI Index:</span>
            <span class="value">${data.ndvi.toFixed(2)}</span>
        </div>
        <div class="metric">
            <span class="label">Vegetation Health:</span>
            <span class="value ${getVegetationHealthClass(data.ndvi)}">${getVegetationHealthStatus(data.ndvi)}</span>
        </div>
        ${data.evi ? `
        <div class="metric">
            <span class="label">EVI:</span>
            <span class="value">${data.evi.toFixed(2)}</span>
        </div>
        ` : ''}
    `;
}

// Update soil panel
function updateSoilPanel(data) {
    if (!data || typeof data.moisture === 'undefined') {
        showError('Invalid soil moisture data');
        return;
    }
    const soilPanel = document.getElementById('soil-panel');
    if (!soilPanel) {
        showError('Soil panel element not found');
        return;
    }
    const moistureValue = typeof data.moisture === 'number' ? data.moisture : data.moisture * 100;
    soilPanel.innerHTML = `
        <h3>Soil Analysis</h3>
        <div class="metric">
            <span class="label">Moisture Level:</span>
            <span class="value">${moistureValue.toFixed(2)}%</span>
        </div>
        <div class="metric">
            <span class="label">Soil Health:</span>
            <span class="value ${getSoilHealthClass(moistureValue)}">${getSoilHealthStatus(moistureValue)}</span>
        </div>
    `;
}

// Helper functions for status classes and levels
function getCarbonRiskClass(value) {
    return value > 8 ? 'high-risk' :
           value > 6 ? 'medium-risk' :
           'low-risk';
}

function getCarbonRiskLevel(value) {
    return value > 8 ? 'High Risk' :
           value > 6 ? 'Medium Risk' :
           'Low Risk';
}

function getVegetationHealthClass(ndvi) {
    return ndvi > 0.6 ? 'healthy' :
           ndvi > 0.3 ? 'moderate' :
           'poor';
}

function getVegetationHealthStatus(ndvi) {
    return ndvi > 0.6 ? 'Healthy' :
           ndvi > 0.3 ? 'Moderate' :
           'Poor';
}

function getSoilHealthClass(moisture) {
    return moisture > 70 ? 'over-saturated' :
           moisture > 30 ? 'optimal' :
           'dry';
}

function getSoilHealthStatus(moisture) {
    return moisture > 70 ? 'Over Saturated' :
           moisture > 30 ? 'Optimal' :
           'Dry';
}


// Clear error message timeouts
function clearErrorTimeouts() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    
    const existingErrors = sidebar.getElementsByClassName('error-message');
    Array.from(existingErrors).forEach(error => {
        if (error.dataset.timeoutId) {
            clearTimeout(parseInt(error.dataset.timeoutId));
            delete error.dataset.timeoutId;
        }
        error.remove();
    });
}

// Show error message
function showError(message) {
    if (!message) {
        console.error('Error message is required');
        return;
    }

    const sidebar = document.getElementById('sidebar');
    if (!sidebar) {
        console.error('Sidebar element not found');
        return;
    }
    
    // Clear existing error messages and their timeouts
    clearErrorTimeouts();
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    // Add error to the top of the sidebar
    if (sidebar.firstChild) {
        sidebar.insertBefore(errorDiv, sidebar.firstChild);
    } else {
        sidebar.appendChild(errorDiv);
    }
    
    // Auto-remove after 5 seconds
    const timeoutId = setTimeout(() => {
        if (errorDiv.parentNode) {
            if (errorDiv.dataset.timeoutId) {
                delete errorDiv.dataset.timeoutId;
            }
            errorDiv.remove();
        }
    }, 5000);
    
    // Store timeout ID on the element for cleanup
    errorDiv.dataset.timeoutId = timeoutId.toString();
}