// 3D Earth scene component with Three.js rendering real-time satellite positions, risk heatmaps, and orbital mechanics visualization
import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { RiskPoint, RiskLevel, RiskType } from '../types';
import { useRiskAlerts } from '../hooks/useWebSocket';

interface EarthSceneProps {
  className?: string;
  onRiskPointClick?: (risk: RiskPoint) => void;
  onEarthClick?: (lat: number, lng: number) => void;
  showRiskPoints?: boolean;
  showSatellites?: boolean;
  riskData?: RiskPoint[];
}

const EarthScene: React.FC<EarthSceneProps> = ({
  className = '',
  onRiskPointClick,
  onEarthClick,
  showRiskPoints = true,
  showSatellites = true,
  riskData = []
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const animationIdRef = useRef<number | null>(null);
  const earthRef = useRef<THREE.Mesh | null>(null);
  const riskPointsRef = useRef<THREE.Group | null>(null);
  const satellitesRef = useRef<THREE.Group | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get real-time risk alerts
  const { riskAlerts } = useRiskAlerts();

  // Risk point colors based on level
  const getRiskColor = (level: RiskLevel): number => {
    switch (level) {
      case 'low': return 0x00ff88; // Green
      case 'medium': return 0xffaa00; // Yellow
      case 'high': return 0xff4444; // Red
      case 'critical': return 0xff00ff; // Magenta
      default: return 0x00c8ff; // Cyan
    }
  };

  // Risk point colors based on type
  const getRiskTypeColor = (type: RiskType): number => {
    switch (type) {
      case 'flood': return 0x0066cc; // Blue
      case 'drought': return 0xff6600; // Orange
      case 'wildfire': return 0xff0000; // Red
      case 'earthquake': return 0x8b4513; // Brown
      case 'storm': return 0x4169e1; // Royal Blue
      case 'heatwave': return 0xff4500; // Orange Red
      case 'landslide': return 0x654321; // Dark Brown
      case 'tsunami': return 0x00bfff; // Deep Sky Blue
      default: return 0x00c8ff; // Cyan
    }
  };

  // Convert lat/lng to 3D position on sphere
  const latLngToVector3 = (lat: number, lng: number, radius: number = 1.01): THREE.Vector3 => {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lng + 180) * (Math.PI / 180);
    
    return new THREE.Vector3(
      radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    );
  };

  // Create Earth geometry and material
  const createEarth = useCallback(() => {
    const geometry = new THREE.SphereGeometry(1, 64, 64);
    
    // Create Earth material with Mapbox satellite texture
    const mapboxToken = import.meta.env.VITE_MAPBOX_TOKEN;
    const textureUrl = `https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/0,0,0/1024x512?access_token=${mapboxToken}`;
    
    const textureLoader = new THREE.TextureLoader();
    const texture = textureLoader.load(textureUrl);
    
    const material = new THREE.MeshLambertMaterial({
      map: texture,
      transparent: false
    });

    const earth = new THREE.Mesh(geometry, material);
    earthRef.current = earth;
    sceneRef.current?.add(earth);

    // Add atmosphere effect
    const atmosphereGeometry = new THREE.SphereGeometry(1.05, 32, 32);
    const atmosphereMaterial = new THREE.MeshBasicMaterial({
      color: 0x00c8ff,
      transparent: true,
      opacity: 0.1,
      side: THREE.BackSide
    });
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    sceneRef.current?.add(atmosphere);

    return earth;
  }, []);

  // Create risk point markers
  const createRiskPoints = useCallback((risks: RiskPoint[]) => {
    if (!sceneRef.current) return;

    // Remove existing risk points
    if (riskPointsRef.current) {
      sceneRef.current.remove(riskPointsRef.current);
    }

    const riskGroup = new THREE.Group();
    riskPointsRef.current = riskGroup;

    risks.forEach((risk) => {
      const position = latLngToVector3(risk.latitude, risk.longitude);
      
      // Create risk marker geometry
      const geometry = new THREE.SphereGeometry(0.02, 8, 8);
      const material = new THREE.MeshBasicMaterial({
        color: getRiskTypeColor(risk.type),
        transparent: true,
        opacity: 0.8
      });
      
      const marker = new THREE.Mesh(geometry, material);
      marker.position.copy(position);
      marker.userData = { risk };
      
      // Add pulsing animation
      const pulseGeometry = new THREE.SphereGeometry(0.03, 8, 8);
      const pulseMaterial = new THREE.MeshBasicMaterial({
        color: getRiskColor(risk.level),
        transparent: true,
        opacity: 0.3,
        side: THREE.BackSide
      });
      
      const pulseMarker = new THREE.Mesh(pulseGeometry, pulseMaterial);
      pulseMarker.position.copy(position);
      pulseMarker.userData = { risk, isPulse: true };
      
      riskGroup.add(marker);
      riskGroup.add(pulseMarker);
    });

    sceneRef.current.add(riskGroup);
  }, []);

  // Create satellite markers
  const createSatellites = useCallback(() => {
    if (!sceneRef.current) return;

    // Remove existing satellites
    if (satellitesRef.current) {
      sceneRef.current.remove(satellitesRef.current);
    }

    const satelliteGroup = new THREE.Group();
    satellitesRef.current = satelliteGroup;

    // Mock satellite positions (in a real app, these would come from telemetry)
    const satellites = [
      { name: 'Sentinel-1A', lat: 45, lng: 0, altitude: 693 },
      { name: 'Landsat-8', lat: -30, lng: 120, altitude: 705 },
      { name: 'MODIS', lat: 0, lng: -90, altitude: 705 },
      { name: 'NOAA-20', lat: 60, lng: 180, altitude: 824 }
    ];

    satellites.forEach((sat) => {
      const position = latLngToVector3(sat.lat, sat.lng, 1.1);
      
      const geometry = new THREE.BoxGeometry(0.01, 0.01, 0.01);
      const material = new THREE.MeshBasicMaterial({
        color: 0x00c8ff,
        transparent: true,
        opacity: 0.9
      });
      
      const satellite = new THREE.Mesh(geometry, material);
      satellite.position.copy(position);
      satellite.userData = { satellite: sat };
      
      satelliteGroup.add(satellite);
    });

    sceneRef.current.add(satelliteGroup);
  }, []);

  // Initialize Three.js scene
  const initScene = useCallback(() => {
    if (!mountRef.current) return;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000814);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      45,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 0, 15);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;
    mountRef.current.appendChild(renderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 5;
    controls.maxDistance = 50;
    controls.enablePan = false;
    controlsRef.current = controls;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Create Earth
    createEarth();

    // Create satellites if enabled
    if (showSatellites) {
      createSatellites();
    }

    setIsLoading(false);
  }, [createEarth, createSatellites, showSatellites]);

  // Animation loop
  const animate = useCallback(() => {
    if (!sceneRef.current || !cameraRef.current || !rendererRef.current || !controlsRef.current) return;

    // Update controls
    controlsRef.current.update();

    // Animate risk point pulses
    if (riskPointsRef.current) {
      riskPointsRef.current.children.forEach((child) => {
        if (child.userData.isPulse) {
          const time = Date.now() * 0.001;
          child.scale.setScalar(1 + Math.sin(time * 2) * 0.2);
        }
      });
    }

    // Animate satellites
    if (satellitesRef.current) {
      const time = Date.now() * 0.0005;
      satellitesRef.current.children.forEach((child, index) => {
        child.rotation.y = time + index * Math.PI / 2;
      });
    }

    // Render
    rendererRef.current.render(sceneRef.current, cameraRef.current);
    animationIdRef.current = requestAnimationFrame(animate);
  }, []);

  // Handle window resize
  const handleResize = useCallback(() => {
    if (!mountRef.current || !cameraRef.current || !rendererRef.current) return;

    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;

    cameraRef.current.aspect = width / height;
    cameraRef.current.updateProjectionMatrix();
    rendererRef.current.setSize(width, height);
  }, []);

  // Handle mouse clicks
  const handleClick = useCallback((event: MouseEvent) => {
    if (!cameraRef.current || !sceneRef.current || !rendererRef.current) return;

    const mouse = new THREE.Vector2();
    mouse.x = (event.clientX / rendererRef.current.domElement.clientWidth) * 2 - 1;
    mouse.y = -(event.clientY / rendererRef.current.domElement.clientHeight) * 2 + 1;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mouse, cameraRef.current);

    // Check for risk point clicks
    if (riskPointsRef.current) {
      const intersects = raycaster.intersectObjects(riskPointsRef.current.children);
      if (intersects.length > 0) {
        const clickedObject = intersects[0].object;
        if (clickedObject.userData.risk && onRiskPointClick) {
          onRiskPointClick(clickedObject.userData.risk);
        }
        return;
      }
    }

    // Check for Earth clicks
    if (earthRef.current) {
      const intersects = raycaster.intersectObject(earthRef.current);
      if (intersects.length > 0) {
        const point = intersects[0].point;
        const lat = Math.asin(point.y) * (180 / Math.PI);
        const lng = Math.atan2(point.z, point.x) * (180 / Math.PI);
        
        if (onEarthClick) {
          onEarthClick(lat, lng);
        }
      }
    }
  }, [onRiskPointClick, onEarthClick]);

  // Initialize scene on mount
  useEffect(() => {
    initScene();
  }, [initScene]);

  // Start animation loop
  useEffect(() => {
    animate();
    return () => {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
    };
  }, [animate]);

  // Handle resize
  useEffect(() => {
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [handleResize]);

  // Handle clicks
  useEffect(() => {
    if (!rendererRef.current) return;

    const canvas = rendererRef.current.domElement;
    canvas.addEventListener('click', handleClick);
    return () => canvas.removeEventListener('click', handleClick);
  }, [handleClick]);

  // Update risk points when data changes
  useEffect(() => {
    const allRisks = [...riskData, ...riskAlerts];
    if (showRiskPoints && allRisks.length > 0) {
      createRiskPoints(allRisks);
    }
  }, [riskData, riskAlerts, showRiskPoints, createRiskPoints]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (rendererRef.current && mountRef.current) {
        mountRef.current.removeChild(rendererRef.current.domElement);
      }
    };
  }, []);

  if (error) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="text-center">
          <div className="text-red-400 text-lg mb-2">⚠️ Error Loading Earth</div>
          <div className="text-gray-400 text-sm">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative w-full h-full ${className}`}>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-10">
          <div className="text-center">
            <div className="holo-spinner mx-auto mb-4"></div>
            <div className="text-cyan-400 text-sm font-mono">INITIALIZING EARTH...</div>
          </div>
        </div>
      )}
      <div ref={mountRef} className="w-full h-full" />
    </div>
  );
};

export default EarthScene;
