document.addEventListener("DOMContentLoaded", function() {
    const map = L.map('map').setView([37.7749, -122.4194], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(map);

    const loadingElement = document.getElementById('mapLoading');

    fetch('/heatmap_data')
        .then(response => {
            if (!response.ok) throw new Error('Failed to load crime data');
            return response.json();
        })
        .then(data => {
            if (!data || data.length === 0) {
                throw new Error('No crime data available');
            }

            // Create marker cluster group
            const markers = L.markerClusterGroup({
                spiderfyOnMaxZoom: true,
                showCoverageOnHover: false,
                zoomToBoundsOnClick: true,
                maxClusterRadius: 40,
                iconCreateFunction: function (cluster) {
                    const childCount = cluster.getChildCount();
                    let size = 'small';
                    if (childCount > 100) size = 'large';
                    else if (childCount > 50) size = 'medium';
                    
                    return L.divIcon({
                        html: '<div><span>' + childCount + '</span></div>',
                        className: 'marker-cluster-' + size,
                        iconSize: new L.Point(40, 40)
                    });
                }
            });

            // Add markers with proper styling
            data.forEach(point => {
                const marker = L.circleMarker([point.lat, point.lng], {
                    radius: point.radius,
                    fillColor: point.color,
                    color: '#fff',
                    weight: 1,
                    opacity: 0.9,
                    fillOpacity: 0.8
                }).bindPopup(`
                    <div class="map-popup">
                        <h6>${point.category}</h6>
                        <p><strong>District:</strong> ${point.district}</p>
                        <p><strong>Incidents:</strong> ${point.count.toLocaleString()}</p>
                        <p style="color:${point.color}">
                            <i class="fas fa-map-marker-alt"></i> ${ 
                                point.color === '#ff4444' ? 'High Risk' : 
                                point.color === '#ffbb33' ? 'Medium Risk' : 'Low Risk'
                            }
                        </p>
                    </div>
                `);
                markers.addLayer(marker);
            });

            map.addLayer(markers);
            map.fitBounds(markers.getBounds(), { padding: [50, 50] });
        })
        .catch(error => {
            console.error('Error:', error);
            L.control.custom({
                position: 'topright',
                content: `<div class="alert alert-warning">${error.message}</div>`
            }).addTo(map);
        })
        .finally(() => {
            loadingElement.style.display = 'none';
        });

    // Add legend
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend p-2');
        div.style.backgroundColor = 'rgba(255,255,255,0.9)';
        div.style.borderRadius = '5px';
        div.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
        div.innerHTML = `
            <h6 class="mb-2">Crime Density</h6>
            <div class="d-flex align-items-center mb-1">
                <div style="width:15px;height:15px;background:#ff4444;margin-right:8px;border-radius:50%;"></div>
                <span>High Risk</span>
            </div>
            <div class="d-flex align-items-center mb-1">
                <div style="width:15px;height:15px;background:#ffbb33;margin-right:8px;border-radius:50%;"></div>
                <span>Medium Risk</span>
            </div>
            <div class="d-flex align-items-center">
                <div style="width:15px;height:15px;background:#00C851;margin-right:8px;border-radius:50%;"></div>
                <span>Low Risk</span>
            </div>
        `;
        return div;
    };
    legend.addTo(map);
});

// Helper for custom controls
L.Control.Custom = L.Control.extend({
    onAdd: function(map) {
        this._container = L.DomUtil.create('div');
        L.DomEvent.disableClickPropagation(this._container);
        this._container.innerHTML = this.options.content;
        return this._container;
    }
});

L.control.custom = function(opts) {
    return new L.Control.Custom(opts);
};