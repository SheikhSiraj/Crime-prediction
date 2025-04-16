document.addEventListener("DOMContentLoaded", function() {
    // Initialize map
    const map = L.map('map').setView([37.7749, -122.4194], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    const loadingElement = document.getElementById('mapLoading');
    let markerCluster = null;

    // Load heatmap data
    function loadHeatmapData() {
        showLoading();
        
        fetch('/heatmap_data')
            .then(handleResponse)
            .then(displayHeatmap)
            .catch(handleError)
            .finally(hideLoading);
    }

    function showLoading() {
        loadingElement.style.display = 'flex';
        if (markerCluster) {
            map.removeLayer(markerCluster);
            markerCluster = null;
        }
    }

    function hideLoading() {
        loadingElement.style.display = 'none';
    }

    function handleResponse(response) {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    function displayHeatmap(data) {
        if (!Array.isArray(data) || data.length === 0) {
            showMessage('No crime data available', 'warning');
            return;
        }

        markerCluster = L.markerClusterGroup({
            maxClusterRadius: 40,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false
        });

        const validPoints = data.filter(point => 
            point.lat && point.lng &&
            !isNaN(point.lat) && !isNaN(point.lng) &&
            point.lat >= -90 && point.lat <= 90 &&
            point.lng >= -180 && point.lng <= 180
        );

        if (validPoints.length === 0) {
            showMessage('No valid crime locations found', 'warning');
            return;
        }

        validPoints.forEach(point => {
            const marker = L.circleMarker([point.lat, point.lng], {
                radius: point.radius || 5,
                fillColor: point.color || '#3388ff',
                color: '#fff',
                weight: 1,
                opacity: 0.8,
                fillOpacity: 0.7
            }).bindPopup(createPopup(point));
            markerCluster.addLayer(marker);
        });

        map.addLayer(markerCluster);
        map.fitBounds(markerCluster.getBounds(), { padding: [50, 50] });
    }

    function handleError(error) {
        console.error('Error:', error);
        showMessage('Failed to load crime data', 'danger');
    }

    function createPopup(point) {
        return `
            <div class="map-popup">
                <h6>${point.category || 'Unknown'}</h6>
                <p><strong>District:</strong> ${point.district || 'Unknown'}</p>
                <p><strong>Incidents:</strong> ${point.count || 0}</p>
                <p style="color:${point.color || '#3388ff'}">
                    <i class="fas fa-map-marker-alt"></i> ${getRiskLevel(point.color)}
                </p>
            </div>
        `;
    }

    function getRiskLevel(color) {
        return color === '#ff4444' ? 'High Risk' : 
               color === '#ffbb33' ? 'Medium Risk' : 'Low Risk';
    }

    function showMessage(text, type) {
        const control = L.control({ position: 'topright' });
        control.onAdd = () => {
            const div = L.DomUtil.create('div', 'alert alert-' + type);
            div.innerHTML = text;
            return div;
        };
        control.addTo(map);
        setTimeout(() => map.removeControl(control), 5000);
    }

    // Initial load
    loadHeatmapData();
});