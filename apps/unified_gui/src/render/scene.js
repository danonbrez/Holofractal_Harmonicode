import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { PARTICLE_COUNT } from "../physics/address_map.js";

export const RENDER_PROFILES = Object.freeze({
  MOBILE_SAFE: { mode: "points", pixelRatio: 1, detail: 0 },
  BALANCED: { mode: "instances", pixelRatio: 1.25, detail: 0 },
  DESKTOP_HIGH: { mode: "instances", pixelRatio: 1.75, detail: 1 },
  DIAGNOSTIC: { mode: "points", pixelRatio: 1, detail: 0 },
});

export class HHSRenderProjection {
  constructor(canvas, particleEngine, options = {}) {
    if (!(canvas instanceof HTMLCanvasElement)) throw new TypeError("canvas required");
    this.canvas = canvas;
    this.engine = particleEngine;
    this.profileName = options.profile ?? "MOBILE_SAFE";
    this.profile = RENDER_PROFILES[this.profileName];
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.controls = null;
    this.object = null;
    this.geometry = null;
    this.material = null;
    this.animationFrame = null;
    this.frame = 0;
    this.onContextLost = options.onContextLost ?? (() => {});
    this.onContextRestored = options.onContextRestored ?? (() => {});
    this._contextLostHandler = (event) => {
      event.preventDefault();
      this.pause();
      this.onContextLost();
    };
    this._contextRestoredHandler = () => {
      this.disposeRenderResources();
      this.initialize();
      this.onContextRestored();
      this.start();
    };
  }

  initialize() {
    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: this.profileName !== "MOBILE_SAFE" });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, this.profile.pixelRatio));
    this.renderer.setSize(this.canvas.clientWidth || 640, this.canvas.clientHeight || 480, false);
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x05070d);
    this.camera = new THREE.PerspectiveCamera(50, 1, 0.1, 200);
    this.camera.position.set(0, 8, 30);
    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.minDistance = 5;
    this.controls.maxDistance = 90;
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x182038, 1.7));
    const key = new THREE.DirectionalLight(0xffffff, 2.2);
    key.position.set(12, 18, 15);
    this.scene.add(key);
    this._createPersistentPool();
    this.canvas.addEventListener("webglcontextlost", this._contextLostHandler, false);
    this.canvas.addEventListener("webglcontextrestored", this._contextRestoredHandler, false);
    this.resize();
    this.updateBuffers();
    return this.diagnostics();
  }

  _createPersistentPool() {
    if (this.profile.mode === "instances") {
      this.geometry = new THREE.IcosahedronGeometry(0.075, this.profile.detail);
      this.material = new THREE.MeshStandardMaterial({ roughness: 0.45, metalness: 0.15, vertexColors: true });
      this.object = new THREE.InstancedMesh(this.geometry, this.material, PARTICLE_COUNT);
      this.object.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
      this.object.frustumCulled = false;
      this.scene.add(this.object);
    } else {
      this.geometry = new THREE.BufferGeometry();
      this.geometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array(PARTICLE_COUNT * 3), 3));
      this.geometry.setAttribute("color", new THREE.BufferAttribute(new Float32Array(PARTICLE_COUNT * 3), 3));
      this.material = new THREE.PointsMaterial({ size: this.profileName === "DIAGNOSTIC" ? 0.065 : 0.045, vertexColors: true });
      this.object = new THREE.Points(this.geometry, this.material);
      this.object.frustumCulled = false;
      this.scene.add(this.object);
    }
  }

  resize() {
    if (!this.renderer || !this.camera) return;
    const width = Math.max(1, this.canvas.clientWidth || this.canvas.width || 640);
    const height = Math.max(1, this.canvas.clientHeight || this.canvas.height || 480);
    this.renderer.setSize(width, height, false);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
  }

  updateBuffers() {
    if (!this.object) return;
    const positions = this.engine.positions;
    const color = new THREE.Color();
    if (this.object.isInstancedMesh) {
      const matrixObject = new THREE.Object3D();
      for (let index = 0; index < PARTICLE_COUNT; index += 1) {
        const base = index * 3;
        matrixObject.position.set(positions[base], positions[base + 1], positions[base + 2]);
        matrixObject.updateMatrix();
        this.object.setMatrixAt(index, matrixObject.matrix);
        const particle = this.engine.addresses[index];
        color.setHSL(particle.phase72 / 72, 0.72, 0.42 + particle.loshu_a / 45);
        this.object.setColorAt(index, color);
      }
      this.object.instanceMatrix.needsUpdate = true;
      if (this.object.instanceColor) this.object.instanceColor.needsUpdate = true;
    } else {
      const positionAttribute = this.geometry.getAttribute("position");
      const colorAttribute = this.geometry.getAttribute("color");
      for (let index = 0; index < PARTICLE_COUNT; index += 1) {
        const base = index * 3;
        positionAttribute.array[base] = positions[base];
        positionAttribute.array[base + 1] = positions[base + 1];
        positionAttribute.array[base + 2] = positions[base + 2];
        const particle = this.engine.addresses[index];
        color.setHSL(particle.phase72 / 72, 0.72, 0.42 + particle.loshu_a / 45);
        colorAttribute.array[base] = color.r;
        colorAttribute.array[base + 1] = color.g;
        colorAttribute.array[base + 2] = color.b;
      }
      positionAttribute.needsUpdate = true;
      colorAttribute.needsUpdate = true;
      this.geometry.computeBoundingSphere();
    }
  }

  renderFrame = () => {
    if (!this.renderer) return;
    this.controls?.update();
    this.updateBuffers();
    this.renderer.render(this.scene, this.camera);
    this.frame += 1;
    this.animationFrame = requestAnimationFrame(this.renderFrame);
  };

  start() {
    if (this.animationFrame === null) this.animationFrame = requestAnimationFrame(this.renderFrame);
  }

  pause() {
    if (this.animationFrame !== null) cancelAnimationFrame(this.animationFrame);
    this.animationFrame = null;
  }

  setProfile(profileName) {
    if (!RENDER_PROFILES[profileName]) throw new Error("INVALID_RENDER_PROFILE");
    if (profileName === this.profileName) return this.diagnostics();
    this.profileName = profileName;
    this.profile = RENDER_PROFILES[profileName];
    this.pause();
    this.disposeRenderResources();
    this.initialize();
    this.start();
    return this.diagnostics();
  }

  focusParticle(index) {
    const particle = this.engine.getParticle(index);
    this.controls.target.set(...particle.position);
    this.camera.position.set(particle.position[0], particle.position[1] + 2, particle.position[2] + 5);
    this.controls.update();
    return particle;
  }

  diagnostics() {
    return Object.freeze({
      profile: this.profileName,
      mode: this.profile.mode,
      particle_count: PARTICLE_COUNT,
      frame: this.frame,
      webgl2: Boolean(this.renderer?.capabilities?.isWebGL2),
      draw_object: this.object?.isInstancedMesh ? "THREE.InstancedMesh" : "THREE.Points",
    });
  }

  disposeRenderResources() {
    if (this.object && this.scene) this.scene.remove(this.object);
    this.geometry?.dispose();
    this.material?.dispose();
    this.controls?.dispose();
    this.renderer?.dispose();
    this.object = null;
    this.geometry = null;
    this.material = null;
    this.controls = null;
    this.renderer = null;
  }

  dispose() {
    this.pause();
    this.canvas.removeEventListener("webglcontextlost", this._contextLostHandler, false);
    this.canvas.removeEventListener("webglcontextrestored", this._contextRestoredHandler, false);
    this.disposeRenderResources();
  }
}
