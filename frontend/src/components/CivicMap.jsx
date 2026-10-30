import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

// Fix Leaflet's default icon path in bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function createCustomMarker(color, label = '') {
  return L.divIcon({
    className: 'custom-map-pin',
    html: `
      <div style="
        background: ${color};
        width: 28px;
        height: 28px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 2px solid #ffffff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <span style="
          transform: rotate(45deg);
          color: white;
          font-size: 11px;
          font-weight: 700;
        ">${label}</span>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -28],
  });
}

function CivicMap({
  assets = [],
  issues = [],
  hotspots = [],
  selectedAssetId = null,
  onSelectAsset = () => {},
  height = '500px',
  center = [12.9716, 77.5946],
  zoom = 13,
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersLayerRef = useRef(null);

  // Initialize Map Once
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        zoomControl: true,
        attributionControl: false,
      }).setView(center, zoom);

      // Dark theme OpenStreetMap tiles via CartoDB
      L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
        {
          maxZoom: 19,
          subdomains: 'abcd',
        }
      ).addTo(map);

      markersLayerRef.current = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update Layers when data changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layer = markersLayerRef.current;
    if (!map || !layer) return;

    layer.clearLayers();

    // 1. Render Hotspot Radii
    hotspots.forEach((h) => {
      if (h.latitude == null || h.longitude == null || isNaN(h.latitude) || isNaN(h.longitude)) return;
      const circleColor = h.risk_level === 'Critical' ? '#ef4444' : '#f59e0b';
      const circle = L.circle([h.latitude, h.longitude], {
        radius: h.radius_meters || 300,
        color: circleColor,
        fillColor: circleColor,
        fillOpacity: 0.18,
        weight: 2,
        dashArray: '4, 4',
      }).addTo(layer);

      circle.bindPopup(`
        <div style="font-family: sans-serif; padding: 4px; color: #0f172a;">
          <div style="font-weight: 700; font-size: 13px; color: ${circleColor};">
            ⚡ CHRONIC HOTSPOT: ${h.cluster_id}
          </div>
          <div style="font-size: 12px; margin-top: 4px;">
            <b>Ward:</b> ${h.ward}<br/>
            <b>Defects:</b> ${h.defect_count} issues (${h.primary_category})<br/>
            <b>Recurrence Index:</b> ${h.recurrence_index}/10 (${h.risk_level})
          </div>
        </div>
      `);
    });

    // 2. Render Physical Assets
    assets.forEach((a) => {
      if (a.latitude == null || a.longitude == null || isNaN(a.latitude) || isNaN(a.longitude)) return;
      let pinColor = '#3b82f6'; // Blue
      if (a.category === 'Streetlight') pinColor = '#eab308';
      if (a.category === 'Drainage') pinColor = '#06b6d4';
      if (a.category === 'Waste Point') pinColor = '#a855f7';
      if (a.risk_level === 'Critical' || a.risk_score >= 7.0) pinColor = '#ef4444';

      const isSelected = selectedAssetId && selectedAssetId === a.id;
      const marker = L.marker([a.latitude, a.longitude], {
        icon: createCustomMarker(pinColor, a.category[0]),
      }).addTo(layer);

      marker.bindPopup(`
        <div style="font-family: sans-serif; padding: 6px; color: #0f172a; min-width: 200px;">
          <div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600;">
            ${a.asset_code} • ${a.category}
          </div>
          <div style="font-weight: 700; font-size: 13px; margin: 2px 0 6px;">
            ${a.name}
          </div>
          <div style="font-size: 12px; background: #f1f5f9; padding: 6px; border-radius: 6px; margin-bottom: 6px;">
            <div><b>Health Score:</b> ${a.health_score}/100</div>
            <div><b>Risk Score:</b> <span style="color: ${a.risk_score >= 6 ? '#dc2626' : '#16a34a'}; font-weight: 700;">${a.risk_score}/10 (${a.risk_level})</span></div>
            <div><b>Ward:</b> ${a.ward}</div>
          </div>
          ${a.risk_factors?.length ? `<div style="font-size: 11px; color: #b91c1c;">⚠️ ${a.risk_factors[0]}</div>` : ''}
        </div>
      `);

      marker.on('click', () => {
        onSelectAsset(a);
      });

      if (isSelected) {
        marker.openPopup();
      }
    });

    // 3. Render Issues
    issues.forEach((i) => {
      if (i.latitude == null || i.longitude == null || isNaN(i.latitude) || isNaN(i.longitude)) return;
      if (i.is_recurrence || i.recurrence_count > 0) {
        const marker = L.marker([i.latitude, i.longitude], {
          icon: createCustomMarker('#dc2626', '⚠️'),
        }).addTo(layer);

        marker.bindPopup(`
          <div style="font-family: sans-serif; padding: 6px; color: #0f172a;">
            <div style="color: #dc2626; font-weight: 800; font-size: 12px;">
              🔄 RECURRING DEFECT (#${i.recurrence_count})
            </div>
            <div style="font-weight: 700; font-size: 13px; margin: 3px 0;">
              ${i.title}
            </div>
            <div style="font-size: 11px; color: #475569;">
              Code: ${i.issue_code} | Severity: <b>${i.severity}</b>
            </div>
            <div style="font-size: 11px; margin-top: 4px; color: #64748b;">
              ${i.recurrence_notes || 'Defect recurred post-repair cycle.'}
            </div>
          </div>
        `);
      }
    });
  }, [assets, issues, hotspots, selectedAssetId]);

  return (
    <div
      ref={mapContainerRef}
      style={{ height, width: '100%', borderRadius: '12px', zIndex: 10 }}
      className="border border-slate-700/60 shadow-xl overflow-hidden"
    />
  );
}

export default CivicMap;
