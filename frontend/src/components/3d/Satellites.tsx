// 3D satellite visualization component displaying real-time satellite positions using SGP4 orbital mechanics and physics simulation
import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as THREE from 'three';
import { TelemetryData, Position } from '../types';
import { useTelemetryUpdates } from '../../hooks/useWebSocket';
import { apiClient } from '../../lib/api-utils';

interface Satellite {
  id: string;
  name: string;
  position: Position;
  velocity?: { x: number; y: number; z: number };
  mission_id?: string;
  status: 'operational' | 'maintenance' | 'offline';
}

interface SatellitePhysicsData {
  satellite_id: string;
  satellite_name: string;
  position: { x: number; y: number; z: number };
  velocity: { x: number; y: number; z: number };
  latitude: number;
  longitude: number;
  altitude: number;
  timestamp: string;
}

interface SatellitesProps {
  satellites?: Satellite[];
  onSatelliteClick?: (satellite: Satellite) => void;
  showOrbits?: boolean;
  showLabels?: boolean;
}

const Satellites: React.FC<SatellitesProps> = ({
  satellites = [],
  onSatelliteClick,
  showOrbits = true,
  showLabels = false
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const orbitLinesRef = useRef<THREE.Line[]>([]);
  const [isVisible, setIsVisible] = useState(true);
  const [satellitePhysicsData, setSatellitePhysicsData] = useState<SatellitePhysicsData[]>([]);

  // Get real-time telemetry updates
  const { telemetryUpdates } = useTelemetryUpdates();

  // Fetch real satellite physics data from backend
  const fetchSatellitePhysicsData = useCallback(async () => {
    try {
      const response = await apiClient.get('/satellites/positions');
      setSatellitePhysicsData(response.data);
    } catch (error) {
      console.error('Failed to fetch satellite physics data:', error);
    }
  }, []);

  // Fetch satellite data on component mount and periodically
  useEffect(() => {
    fetchSatellitePhysicsData();
    const interval = setInterval(fetchSatellitePhysicsData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, [fetchSatellitePhysicsData]);

  // Convert lat/lng/alt to 3D position
  const latLngAltToVector3 = useCallback((lat: number, lng: number, alt: number = 700): THREE.Vector3 => {
    const earthRadius = 6371; // km
    const radius = (earthRadius + alt) / earthRadius; // Normalize to Earth radius
    
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lng + 180) * (Math.PI / 180);
    
    return new THREE.Vector3(
      radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    );
  }, []);

  // Create satellite geometry
  const createSatelliteGeometry = useCallback((size: number = 0.01): THREE.BufferGeometry => {
    const geometry = new THREE.BoxGeometry(size, size, size);
    return geometry;
  }, []);

  // Create satellite material based on status
  const createSatelliteMaterial = useCallback((status: string): THREE.Material => {
    let color = 0x00c8ff; // Default cyan
    
    switch (status) {
      case 'operational':
        color = 0x00ff88; // Green
        break;
      case 'maintenance':
        color = 0xffaa00; // Yellow
        break;
      case 'offline':
        color = 0xff4444; // Red
        break;
    }

    return new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: 0.9
    });
  }, []);

  // Create orbital path
  const createOrbitalPath = useCallback((satellite: Satellite): THREE.Line => {
    const points: THREE.Vector3[] = [];
    const segments = 64;
    
    // Create circular orbit (simplified)
    for (let i = 0; i <= segments; i++) {
      const angle = (i / segments) * Math.PI * 2;
      const lat = satellite.position.latitude + Math.cos(angle) * 5; // 5 degree orbit
      const lng = satellite.position.longitude + Math.sin(angle) * 5;
      const alt = satellite.position.altitude || 700;
      
      points.push(latLngAltToVector3(lat, lng, alt));
    }

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: 0x00c8ff,
      transparent: true,
      opacity: 0.3,
      linewidth: 1
    });

    return new THREE.Line(geometry, material);
  }, [latLngAltToVector3]);

  // Create satellite mesh
  const createSatelliteMesh = useCallback((satellite: Satellite): THREE.Mesh => {
    const geometry = createSatelliteGeometry();
    const material = createSatelliteMaterial(satellite.status);
    const mesh = new THREE.Mesh(geometry, material);
    
    // Position satellite
    const position = latLngAltToVector3(
      satellite.position.latitude,
      satellite.position.longitude,
      satellite.position.altitude || 700
    );
    mesh.position.copy(position);
    
    // Store satellite data
    mesh.userData = { satellite };
    
    // Add pulsing animation for active satellites
    if (satellite.status === 'operational') {
      const pulseGeometry = createSatelliteGeometry(0.015);
      const pulseMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ff88,
        transparent: true,
        opacity: 0.2,
        side: THREE.BackSide
      });
      const pulseMesh = new THREE.Mesh(pulseGeometry, pulseMaterial);
      pulseMesh.position.copy(position);
      pulseMesh.userData = { satellite, isPulse: true };
      
      return pulseMesh;
    }
    
    return mesh;
  }, [createSatelliteGeometry, createSatelliteMaterial, latLngAltToVector3]);

  // Update satellite positions from telemetry
  const updateSatellitePositions = useCallback((telemetryData: TelemetryData[]) => {
    if (!groupRef.current) return;

    // Group telemetry by agent_id (satellite)
    const satelliteTelemetry = telemetryData.reduce((acc, data) => {
      if (!acc[data.agent_id]) {
        acc[data.agent_id] = [];
      }
      acc[data.agent_id].push(data);
      return acc;
    }, {} as Record<string, TelemetryData[]>);

    // Update satellite positions
    Object.entries(satelliteTelemetry).forEach(([agentId, data]) => {
      const latestData = data[data.length - 1]; // Get most recent data
      
      groupRef.current?.children.forEach((child) => {
        if (child.userData.satellite?.id === agentId) {
          const newPosition = latLngAltToVector3(
            latestData.position.latitude,
            latestData.position.longitude,
            latestData.position.altitude || 700
          );
          child.position.copy(newPosition);
        }
      });
    });
  }, [latLngAltToVector3]);

  // Initialize satellites with real physics data
  useEffect(() => {
    if (!groupRef.current) return;

    // Clear existing satellites
    groupRef.current.clear();
    orbitLinesRef.current = [];

    // Use real satellite physics data if available, otherwise fall back to props
    const satellitesToRender = satellitePhysicsData.length > 0 
      ? satellitePhysicsData.map(data => ({
          id: data.satellite_id,
          name: data.satellite_name,
          position: {
            latitude: data.latitude,
            longitude: data.longitude,
            altitude: data.altitude
          },
          velocity: data.velocity,
          status: 'operational' as const
        }))
      : satellites;

    satellitesToRender.forEach((satellite) => {
      // Create satellite mesh
      const satelliteMesh = createSatelliteMesh(satellite);
      groupRef.current?.add(satelliteMesh);

      // Create orbital path if enabled
      if (showOrbits) {
        const orbitLine = createOrbitalPath(satellite);
        orbitLinesRef.current.push(orbitLine);
        groupRef.current?.add(orbitLine);
      }
    });
  }, [satellites, satellitePhysicsData, showOrbits, createSatelliteMesh, createOrbitalPath]);

  // Update positions from telemetry
  useEffect(() => {
    if (telemetryUpdates.length > 0) {
      updateSatellitePositions(telemetryUpdates);
    }
  }, [telemetryUpdates, updateSatellitePositions]);

  // Animation loop for pulsing effects
  useEffect(() => {
    const animate = () => {
      if (!groupRef.current) return;

      const time = Date.now() * 0.001;
      
      groupRef.current.children.forEach((child) => {
        if (child.userData.isPulse) {
          // Pulsing animation
          const scale = 1 + Math.sin(time * 2) * 0.3;
          child.scale.setScalar(scale);
        } else if (child.userData.satellite) {
          // Rotation animation
          child.rotation.y = time * 0.5;
        }
      });

      requestAnimationFrame(animate);
    };

    animate();
  }, []);

  // Handle click events
  const handleClick = useCallback((event: MouseEvent) => {
    if (!onSatelliteClick || !groupRef.current) return;

    // This would need to be integrated with the main scene's raycasting
    // For now, we'll just log the click
    console.log('Satellite clicked:', event);
  }, [onSatelliteClick]);

  if (!isVisible) {
    return null;
  }

  return (
    <group ref={groupRef}>
      {/* Satellites and orbits will be added here */}
    </group>
  );
};

export default Satellites;
