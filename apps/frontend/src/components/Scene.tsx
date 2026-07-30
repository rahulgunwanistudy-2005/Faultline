/* eslint-disable react-hooks/purity */
"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

function FaultLineCore() {
  const group = useRef<THREE.Group>(null);
  const topCrust = useRef<THREE.Mesh>(null);
  const bottomCrust = useRef<THREE.Mesh>(null);
  const core = useRef<THREE.Mesh>(null);

  // Sharp, low-poly geometry for the outer crust
  const crustGeo = useMemo(() => {
    // Icosahedron with 0 detail produces sharp triangles
    return new THREE.IcosahedronGeometry(1.6, 0);
  }, []);

  useFrame((state, delta) => {
    if (!group.current || !topCrust.current || !bottomCrust.current || !core.current) return;
    
    // Overall slow baseline rotation
    group.current.rotation.y += delta * 0.1;
    group.current.rotation.x += delta * 0.05;

    // INTERACTION 1: 3D Mouse Tracking (Rotates the entire fault structure to face the cursor)
    const targetX = (state.pointer.x * Math.PI) / 2;
    const targetY = (state.pointer.y * Math.PI) / 2;
    group.current.rotation.y += 0.05 * (targetX - group.current.rotation.y);
    group.current.rotation.x += 0.05 * (targetY - group.current.rotation.x);

    // INTERACTION 2: The "Fault Line" Fracture
    // The further the mouse moves from the center of the screen, the more the crust splits open!
    const mouseDistance = Math.sqrt(state.pointer.x * state.pointer.x + state.pointer.y * state.pointer.y);
    const split = 0.1 + mouseDistance * 1.5; 
    
    // Smoothly animate the crust pieces pulling apart diagonally
    topCrust.current.position.y = THREE.MathUtils.lerp(topCrust.current.position.y, split, 0.1);
    topCrust.current.position.x = THREE.MathUtils.lerp(topCrust.current.position.x, split * 0.5, 0.1);
    
    bottomCrust.current.position.y = THREE.MathUtils.lerp(bottomCrust.current.position.y, -split, 0.1);
    bottomCrust.current.position.x = THREE.MathUtils.lerp(bottomCrust.current.position.x, -split * 0.5, 0.1);
    
    // INTERACTION 3: The glowing core pulses and spins rapidly
    const scale = 0.9 + Math.sin(state.clock.elapsedTime * 4) * 0.05;
    core.current.scale.set(scale, scale, scale);
    core.current.rotation.y -= delta * 0.5;
    core.current.rotation.z += delta * 0.3;
  });

  return (
    <group position={[2.8, 0, 0]} ref={group}>
      
      {/* Glowing Inner Core (Exposed when the fault line opens) */}
      <mesh ref={core}>
        <icosahedronGeometry args={[0.9, 1]} />
        <meshBasicMaterial color="#F4A261" transparent opacity={0.9} />
        {/* Wireframe overlay on the core for a data/tech vibe */}
        <mesh>
          <icosahedronGeometry args={[0.92, 1]} />
          <meshBasicMaterial color="#FFFFFF" wireframe={true} transparent opacity={0.5} />
        </mesh>
      </mesh>
      
      {/* Top Crust (Distinct Orange) */}
      <mesh ref={topCrust} geometry={crustGeo} rotation={[0, 0, 0.2]}>
        <meshStandardMaterial
          color="#E07A5F"
          roughness={0.2}
          metalness={0.4}
          flatShading={true}
        />
      </mesh>
      
      {/* Bottom Crust (Distinct Orange, flipped) */}
      <mesh ref={bottomCrust} geometry={crustGeo} rotation={[Math.PI, 0, -0.2]}>
        <meshStandardMaterial
          color="#E07A5F"
          roughness={0.2}
          metalness={0.4}
          flatShading={true}
        />
      </mesh>
      
      <DataParticles />
    </group>
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
      new THREE.Color("#F4A261"), // Amber
      new THREE.Color("#FFFFFF"), // White sparks
    ];
    
    for (let i = 0; i < count; i++) {
      // Position in a sphere around the fault
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      const radius = 2.5 + Math.random() * 2.5;
      
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

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    return geo;
  }, [positions, colors]);

  useFrame((state, delta) => {
    if (!particles.current) return;
    
    // Base rotation
    particles.current.rotation.y += delta * 0.05;
    
    // Interactive mouse follow for particles too
    const targetX = (state.pointer.x * Math.PI) / 8;
    particles.current.rotation.y += 0.05 * (targetX - particles.current.rotation.y);
  });

  return (
    <points ref={particles} geometry={geometry}>
      <pointsMaterial
        size={0.06}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  );
}

export default function Scene() {
  return (
    <div className="w-full h-[600px] lg:h-[800px] absolute right-0 top-0 z-0 opacity-100 pointer-events-auto">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 45 }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={1.5} />
        {/* Bright directional lighting makes the flat-shaded geometry pop vibrantly */}
        <directionalLight position={[10, 10, 10]} intensity={3} color="#FCFAF6" />
        <directionalLight position={[-10, -10, -10]} intensity={1.5} color="#F4A261" />
        
        <FaultLineCore />
      </Canvas>
    </div>
  );
}
