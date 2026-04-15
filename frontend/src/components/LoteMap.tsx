import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet'
import L from 'leaflet'

// Fix for default marker icons in Leaflet + Vite
const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41],
})
L.Marker.prototype.options.icon = defaultIcon

interface Props {
  lat: number
  lng: number
  label?: string
  zoom?: number
  height?: number | string
  light?: boolean
}

export default function LoteMap({ lat, lng, label, zoom = 16, height = 220, light = false }: Props) {
  return (
    <div style={{ height, overflow: 'hidden', borderRadius: 12 }} className="border border-white/[0.06]">
      <MapContainer
        center={[lat, lng]}
        zoom={zoom}
        scrollWheelZoom={false}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url={light
            ? 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'}
          attribution='&copy; OpenStreetMap'
        />
        <Marker position={[lat, lng]}>
          {label && <Popup>{label}</Popup>}
        </Marker>
        <CircleMarker
          center={[lat, lng]} radius={40}
          pathOptions={{ color: '#F2C94C', weight: 1.5, fillOpacity: 0.1 }}
        />
      </MapContainer>
    </div>
  )
}
