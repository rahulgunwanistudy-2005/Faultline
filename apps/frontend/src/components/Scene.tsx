/* eslint-disable react-hooks/purity */
"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Environment, Float, MeshTransmissionMaterial } from "@react-three/drei";
import * as THREE from "three";

function DataCrystal() {
  const mesh = useRef<THREE.Mesh>(null);
  
  // Create a procedural fractured geometry
  const geometry = useMemo(() => {
    // Icosahedron for a crystal-like base shape
    const geo = new THREE.IcosahedronGeometry(2.5, 1);
    
    // Add some random noise to the vertices for a "fractured" look
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      const z = pos.getZ(i);
      
      const noise = (Math.random() - 0.5) * 0.4;
      pos.setXYZ(i, x + x * noise, y + y * noise, z + z * noise);
    }
    
    geo.computeVertexNormals();
    return geo;
  }, []);

  useFrame((state, delta) => {
    if (!mesh.current) return;
    
    // Smooth, slow rotation
    mesh.current.rotation.y += delta * 0.15;
    mesh.current.rotation.x += delta * 0.05;
    
    // React slightly to cursor
    const targetX = (state.pointer.x * Math.PI) / 10;
    const targetY = (state.pointer.y * Math.PI) / 10;
    
    mesh.current.rotation.y += 0.05 * (targetX - mesh.current.rotation.y);
    mesh.current.rotation.x += 0.05 * (targetY - mesh.current.rotation.x);
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
      <mesh ref={mesh} geometry={geometry}>
        <MeshTransmissionMaterial
          backside
          backsideThickness={1}
          thickness={2.5}
          ior={1.2}
          chromaticAberration={0.4}
          anisotropy={0.3}
          distortion={0.5}
          distortionScale={0.5}
          temporalDistortion={0.1}
          color="#E07A5F"
          emissive="#2A2421"
          emissiveIntensity={0.1}
        />
      </mesh>
      
      {/* Floating data particles around the crystal */}
      <DataParticles />
    </Float>
  );
}

function DataParticles() {
  const particles = useRef<THREE.Points>(null);
  
  const [positions, colors] = useMemo(() => {
    const count = 150;
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    
    const colorOptions = [
      new THREE.Color("#E07A5F"), // Burnt orange
      new THREE.Color("#8C7868"), // Muted terracotta
      new THREE.Color("#F4A261"), // Amber
    ];
    
    for (let i = 0; i < count; i++) {
      // Position in a sphere around the crystal
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      const radius = 3.5 + Math.random() * 3;
      
      pos[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = radius * Math.cos(phi);
      
      const c = colorOptions[Math.floor(Math.random() * colorOptions.length)];
      col[i * 3] = c.r;
      col[i * 3 + 1] = c.g;
      col[i * 3 + 2] = c.b;
    }
    
    return [pos, col];
  }, []);

  useFrame((state) => {
    if (!particles.current) return;
    particles.current.rotation.y = state.clock.elapsedTime * 0.05;
  });

  return (
    <points ref={particles}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.08}
        vertexColors
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  );
}

export default function Scene() {
  return (
    <div className="w-full h-[600px] lg:h-[800px] absolute right-0 top-0 -z-10 opacity-90">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 45 }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={1.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={2} color="#FDFBF8" />
        <pointLight position={[-10, -10, -10]} intensity={1} color="#E07A5F" />
        
        <DataCrystal />
        
        {/* Soft environment lighting to enhance transmission material */}
        <Environment preset="city" />
        
        {/* Disable orbit controls so it feels integrated, not like a 3D viewer widget */}
        <OrbitControls enableZoom={false} enablePan={false} enableRotate={false} />
      </Canvas>
    </div>
  );
}
