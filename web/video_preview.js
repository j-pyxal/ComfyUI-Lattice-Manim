/**
 * Video preview functionality for Manim nodes
 * Inspired by ComfyUI-VideoHelperSuite preview system
 */

import { app } from "../../scripts/app.js";

// Video preview manager
class VideoPreviewManager {
	constructor() {
		this.previews = new Map();
		this.previewContainers = new Map();
	}
	
	createPreview(node, imageTensor) {
		// Convert IMAGE tensor to video preview
		// IMAGE format: [batch, height, width, channels]
		// We'll create a canvas-based preview that cycles through frames
		
		if (!imageTensor || imageTensor.length === 0) return;
		
		const nodeId = node.id;
		
		// Create preview container if it doesn't exist
		if (!this.previewContainers.has(nodeId)) {
			const container = this.createPreviewContainer(node);
			this.previewContainers.set(nodeId, container);
		}
		
		const container = this.previewContainers.get(nodeId);
		const canvas = container.querySelector('canvas');
		
		if (!canvas) return;
		
		// Get frame data from tensor
		// Note: In ComfyUI, we'd need to access the actual tensor data
		// For now, this is a placeholder structure
		this.previews.set(nodeId, {
			frames: imageTensor,
			currentFrame: 0,
			playing: false,
			fps: 30
		});
		
		// Start preview animation
		this.startPreview(nodeId);
	}
	
	createPreviewContainer(node) {
		// Find the node's widget area
		const nodeEl = node.el || node;
		if (!nodeEl) return null;
		
		// Create preview container
		const container = document.createElement("div");
		container.className = "manim-video-preview";
		container.style.cssText = `
			width: 100%;
			margin: 10px 0;
			padding: 10px;
			background: #1a1a1a;
			border-radius: 4px;
			border: 1px solid #444;
		`;
		
		// Create canvas for video preview
		const canvas = document.createElement("canvas");
		canvas.width = 320;
		canvas.height = 180;
		canvas.style.cssText = `
			width: 100%;
			height: auto;
			border-radius: 4px;
			background: #000;
		`;
		
		// Create controls
		const controls = document.createElement("div");
		controls.style.cssText = `
			display: flex;
			gap: 5px;
			margin-top: 5px;
			align-items: center;
		`;
		
		const playBtn = document.createElement("button");
		playBtn.textContent = "▶";
		playBtn.style.cssText = `
			padding: 4px 8px;
			background: #0074D9;
			color: white;
			border: none;
			border-radius: 3px;
			cursor: pointer;
			font-size: 12px;
		`;
		playBtn.onclick = () => this.togglePlay(node.id);
		
		const frameInfo = document.createElement("span");
		frameInfo.textContent = "Frame 0/0";
		frameInfo.style.cssText = "color: #aaa; font-size: 11px; margin-left: auto;";
		
		controls.appendChild(playBtn);
		controls.appendChild(frameInfo);
		
		container.appendChild(canvas);
		container.appendChild(controls);
		
		// Insert into node (find widget area)
		const widgetArea = nodeEl.querySelector('.litegraph') || nodeEl;
		if (widgetArea) {
			widgetArea.appendChild(container);
		}
		
		return container;
	}
	
	startPreview(nodeId) {
		const preview = this.previews.get(nodeId);
		if (!preview) return;
		
		preview.playing = true;
		this.animatePreview(nodeId);
	}
	
	animatePreview(nodeId) {
		const preview = this.previews.get(nodeId);
		if (!preview || !preview.playing) return;
		
		const container = this.previewContainers.get(nodeId);
		if (!container) return;
		
		const canvas = container.querySelector('canvas');
		const ctx = canvas.getContext('2d');
		
		// Draw current frame
		// Note: This would need actual tensor data access
		// For now, just cycle through frame numbers
		preview.currentFrame = (preview.currentFrame + 1) % (preview.frames?.length || 1);
		
		// Update frame info
		const frameInfo = container.querySelector('span');
		if (frameInfo) {
			frameInfo.textContent = `Frame ${preview.currentFrame + 1}/${preview.frames?.length || 0}`;
		}
		
		// Continue animation
		setTimeout(() => {
			this.animatePreview(nodeId);
		}, 1000 / preview.fps);
	}
	
	togglePlay(nodeId) {
		const preview = this.previewContainers.get(nodeId);
		if (!preview) return;
		
		const playBtn = preview.querySelector('button');
		const manager = this.previews.get(nodeId);
		
		if (manager) {
			manager.playing = !manager.playing;
			playBtn.textContent = manager.playing ? "⏸" : "▶";
			
			if (manager.playing) {
				this.animatePreview(nodeId);
			}
		}
	}
}

// Global preview manager
const previewManager = new VideoPreviewManager();

// Export for use in index.js
export { previewManager };

