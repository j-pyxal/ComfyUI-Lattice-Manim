import { app } from "../../scripts/app.js";

app.registerExtension({
	name: "Lattice.Manim",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		// Style ManimScriptNode
		if (nodeData.name === "ManimScriptNode") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				
				this.setSize([600, 500]);

				const codeWidget = this.widgets.find((w) => w.name === "code");
				if (codeWidget && codeWidget.inputEl) {
					Object.assign(codeWidget.inputEl.style, {
						fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace",
						fontSize: "14px",
						backgroundColor: "#1e1e1e",
						color: "#d4d4d4",
						border: "1px solid #3c3c3c",
						borderRadius: "4px",
						padding: "10px",
						lineHeight: "1.5",
						width: "100%",
						height: "350px",
						resize: "vertical",
						whiteSpace: "pre"
					});
					codeWidget.type = "customtext";
				}
				return r;
			};
		}
		
		// Style ManimAudioCaptionNode
		if (nodeData.name === "ManimAudioCaptionNode") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				
				this.setSize([700, 600]);

				// Style code editor
				const codeWidget = this.widgets.find((w) => w.name === "code");
				if (codeWidget && codeWidget.inputEl) {
					Object.assign(codeWidget.inputEl.style, {
						fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace",
						fontSize: "14px",
						backgroundColor: "#1e1e1e",
						color: "#d4d4d4",
						border: "1px solid #3c3c3c",
						borderRadius: "4px",
						padding: "10px",
						lineHeight: "1.5",
						width: "100%",
						height: "300px",
						resize: "vertical",
						whiteSpace: "pre"
					});
					codeWidget.type = "customtext";
				}
				
				// Add color picker for custom colors
				this.addColorPickers();
				
				return r;
			};
			
			// Add color picker method
			nodeType.prototype.addColorPickers = function() {
				const colorWidgets = [
					this.widgets.find((w) => w.name === "caption_color"),
					this.widgets.find((w) => w.name === "background_color_hex")
				];
				
				colorWidgets.forEach(widget => {
					if (widget && widget.inputEl && widget.inputEl.type === "text") {
						this.addColorPicker(widget);
					}
				});
			};
			
			nodeType.prototype.addColorPicker = function(colorWidget) {
				if (!colorWidget || !colorWidget.inputEl) return;
				
				const pickerContainer = document.createElement("div");
				pickerContainer.style.cssText = `
					display: flex;
					align-items: center;
					gap: 10px;
					margin: 5px 0;
				`;
				
				const colorInput = document.createElement("input");
				colorInput.type = "color";
				colorInput.value = colorWidget.inputEl.value || "#000000";
				colorInput.style.cssText = `
					width: 50px;
					height: 30px;
					border: 1px solid #555;
					border-radius: 4px;
					cursor: pointer;
				`;
				
				colorInput.addEventListener("input", (e) => {
					colorWidget.inputEl.value = e.target.value.toUpperCase();
					colorWidget.inputEl.dispatchEvent(new Event("input", { bubbles: true }));
				});
				
				colorWidget.inputEl.addEventListener("input", (e) => {
					if (/^#[0-9A-F]{6}$/i.test(e.target.value)) {
						colorInput.value = e.target.value;
					}
				});
				
				pickerContainer.appendChild(colorInput);
				pickerContainer.appendChild(colorWidget.inputEl);
				if (colorWidget.inputEl.parentNode) {
					colorWidget.inputEl.parentNode.insertBefore(
						pickerContainer,
						colorWidget.inputEl
					);
					colorWidget.inputEl.parentNode.removeChild(colorWidget.inputEl);
					pickerContainer.appendChild(colorWidget.inputEl);
				}
			};
		}
		
		// Style ManimDataVisualizationNode
		if (nodeData.name === "ManimDataVisualizationNode") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				
				this.setSize([700, 600]);

				// Style custom code editor
				const codeWidget = this.widgets.find((w) => w.name === "custom_code");
				if (codeWidget && codeWidget.inputEl) {
					Object.assign(codeWidget.inputEl.style, {
						fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace",
						fontSize: "14px",
						backgroundColor: "#1e1e1e",
						color: "#d4d4d4",
						border: "1px solid #3c3c3c",
						borderRadius: "4px",
						padding: "10px",
						lineHeight: "1.5",
						width: "100%",
						height: "300px",
						resize: "vertical",
						whiteSpace: "pre"
					});
					codeWidget.type = "customtext";
				}
				
				return r;
			};
		}
		
		// Timeline Scene Node with full timeline UI
		if (nodeData.name === "ManimTimelineSceneNode") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				
				this.setSize([900, 800]);
				
				// Add timeline UI
				setTimeout(() => {
					this.createTimelineUI();
				}, 100);
				
				return r;
			};
			
			// Create timeline UI
			nodeType.prototype.createTimelineUI = function() {
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget) return;
				
				// Create timeline container
				const timelineContainer = document.createElement("div");
				timelineContainer.className = "manim-timeline-container";
				timelineContainer.style.cssText = `
					width: 100%;
					margin: 10px 0;
					padding: 10px;
					background: #2d2d2d;
					border-radius: 4px;
					font-family: monospace;
				`;
				
				// Timeline header
				const header = document.createElement("div");
				header.style.cssText = `
					display: flex;
					justify-content: space-between;
					align-items: center;
					margin-bottom: 10px;
					padding: 5px;
					border-bottom: 1px solid #555;
				`;
				
				const title = document.createElement("h3");
				title.textContent = "Timeline Editor";
				title.style.cssText = "margin: 0; color: #d4d4d4; font-size: 14px;";
				
				const addSceneBtn = document.createElement("button");
				addSceneBtn.textContent = "+ Add Scene";
				addSceneBtn.style.cssText = `
					padding: 5px 10px;
					background: #3c3c3c;
					color: #d4d4d4;
					border: 1px solid #555;
					border-radius: 3px;
					cursor: pointer;
				`;
				addSceneBtn.onclick = () => this.addNewScene();
				
				header.appendChild(title);
				header.appendChild(addSceneBtn);
				timelineContainer.appendChild(header);
				
				// Timeline tracks area
				const tracksArea = document.createElement("div");
				tracksArea.className = "timeline-tracks";
				tracksArea.style.cssText = `
					max-height: 400px;
					overflow-y: auto;
					border: 1px solid #555;
					border-radius: 3px;
					padding: 5px;
				`;
				timelineContainer.appendChild(tracksArea);
				
				// Load and render timeline
				this.timelineContainer = timelineContainer;
				this.tracksArea = tracksArea;
				this.loadTimeline();
				
				// Insert before timeline_json widget
				if (timelineWidget.inputEl && timelineWidget.inputEl.parentNode) {
					timelineWidget.inputEl.parentNode.insertBefore(
						timelineContainer,
						timelineWidget.inputEl
					);
				}
			};
			
			// Load timeline from JSON
			nodeType.prototype.loadTimeline = function() {
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget || !this.tracksArea) return;
				
				try {
					const jsonStr = timelineWidget.inputEl.value || "{}";
					const timeline = JSON.parse(jsonStr);
					const scenes = timeline.scenes || [];
					
					// Clear tracks
					this.tracksArea.innerHTML = "";
					
					// Render each scene as a layer
					scenes.forEach((scene, index) => {
						this.renderSceneLayer(scene, index);
					});
				} catch (e) {
					console.error("Failed to load timeline:", e);
				}
			};
			
			// Render a scene as a timeline layer
			nodeType.prototype.renderSceneLayer = function(scene, index) {
				const layer = document.createElement("div");
				layer.className = "timeline-layer";
				layer.dataset.sceneId = scene.id;
				layer.style.cssText = `
					margin: 5px 0;
					padding: 10px;
					background: #3c3c3c;
					border-radius: 3px;
					border-left: 3px solid #0074D9;
				`;
				
				// Layer header
				const layerHeader = document.createElement("div");
				layerHeader.style.cssText = `
					display: flex;
					justify-content: space-between;
					align-items: center;
					margin-bottom: 8px;
				`;
				
				const layerTitle = document.createElement("div");
				layerTitle.textContent = `Scene ${scene.id} (${scene.start_time.toFixed(2)}s - ${scene.end_time.toFixed(2)}s)`;
				layerTitle.style.cssText = "color: #d4d4d4; font-weight: bold;";
				
				const deleteBtn = document.createElement("button");
				deleteBtn.textContent = "×";
				deleteBtn.style.cssText = `
					background: #ff4444;
					color: white;
					border: none;
					border-radius: 3px;
					width: 24px;
					height: 24px;
					cursor: pointer;
				`;
				deleteBtn.onclick = () => this.deleteScene(scene.id);
				
				layerHeader.appendChild(layerTitle);
				layerHeader.appendChild(deleteBtn);
				layer.appendChild(layerHeader);
				
				// Time controls (in/out points)
				const timeControls = document.createElement("div");
				timeControls.style.cssText = `
					display: flex;
					gap: 10px;
					margin: 5px 0;
					align-items: center;
				`;
				
				const inPoint = document.createElement("input");
				inPoint.type = "number";
				inPoint.value = scene.start_time;
				inPoint.step = 0.1;
				inPoint.style.cssText = `
					width: 80px;
					padding: 3px;
					background: #2d2d2d;
					color: #d4d4d4;
					border: 1px solid #555;
					border-radius: 3px;
				`;
				inPoint.onchange = () => this.updateSceneTime(scene.id, "start", parseFloat(inPoint.value));
				
				const outPoint = document.createElement("input");
				outPoint.type = "number";
				outPoint.value = scene.end_time;
				outPoint.step = 0.1;
				outPoint.style.cssText = inPoint.style.cssText;
				outPoint.onchange = () => this.updateSceneTime(scene.id, "end", parseFloat(outPoint.value));
				
				timeControls.appendChild(document.createTextNode("In:"));
				timeControls.appendChild(inPoint);
				timeControls.appendChild(document.createTextNode("Out:"));
				timeControls.appendChild(outPoint);
				layer.appendChild(timeControls);
				
				// Prompt input
				const promptLabel = document.createElement("label");
				promptLabel.textContent = "Visual Prompt:";
				promptLabel.style.cssText = "display: block; color: #d4d4d4; margin-top: 8px;";
				layer.appendChild(promptLabel);
				
				const promptInput = document.createElement("textarea");
				promptInput.value = scene.prompt || "";
				promptInput.placeholder = "Describe what you want to see (e.g., 'A blue circle rotating in the center')";
				promptInput.style.cssText = `
					width: 100%;
					height: 60px;
					padding: 5px;
					background: #1e1e1e;
					color: #d4d4d4;
					border: 1px solid #555;
					border-radius: 3px;
					font-family: inherit;
					resize: vertical;
				`;
				promptInput.onchange = () => this.updateScenePrompt(scene.id, promptInput.value);
				layer.appendChild(promptInput);
				
				// Generate button
				const generateBtn = document.createElement("button");
				generateBtn.textContent = "🔄 Generate Code";
				generateBtn.style.cssText = `
					margin-top: 5px;
					padding: 5px 10px;
					background: #0074D9;
					color: white;
					border: none;
					border-radius: 3px;
					cursor: pointer;
				`;
				generateBtn.onclick = () => this.generateSceneCode(scene.id, promptInput.value);
				layer.appendChild(generateBtn);
				
				// Code editor (collapsible)
				const codeSection = document.createElement("div");
				codeSection.style.cssText = "margin-top: 10px;";
				
				const codeToggle = document.createElement("button");
				codeToggle.textContent = "▼ Edit Code";
				codeToggle.style.cssText = `
					width: 100%;
					padding: 5px;
					background: #555;
					color: #d4d4d4;
					border: 1px solid #777;
					border-radius: 3px;
					cursor: pointer;
					text-align: left;
				`;
				
				const codeEditor = document.createElement("textarea");
				codeEditor.value = scene.manim_code || "";
				codeEditor.style.cssText = `
					width: 100%;
					height: 200px;
					margin-top: 5px;
					padding: 5px;
					background: #1e1e1e;
					color: #d4d4d4;
					border: 1px solid #555;
					border-radius: 3px;
					font-family: 'Consolas', 'Monaco', monospace;
					font-size: 12px;
					display: none;
					resize: vertical;
				`;
				codeEditor.onchange = () => this.updateSceneCode(scene.id, codeEditor.value);
				
				let codeExpanded = false;
				codeToggle.onclick = () => {
					codeExpanded = !codeExpanded;
					codeEditor.style.display = codeExpanded ? "block" : "none";
					codeToggle.textContent = codeExpanded ? "▲ Hide Code" : "▼ Edit Code";
				};
				
				codeSection.appendChild(codeToggle);
				codeSection.appendChild(codeEditor);
				layer.appendChild(codeSection);
				
				this.tracksArea.appendChild(layer);
			};
			
			// Add new scene
			nodeType.prototype.addNewScene = function() {
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget) return;
				
				try {
					const jsonStr = timelineWidget.inputEl.value || "{}";
					const timeline = JSON.parse(jsonStr);
					
					const scenes = timeline.scenes || [];
					const lastEnd = scenes.length > 0 
						? Math.max(...scenes.map(s => s.end_time))
						: 0;
					
					const newScene = {
						id: scenes.length + 1,
						start_time: lastEnd,
						end_time: lastEnd + 5.0,
						prompt: "",
						visual_type: "auto",
						manim_code: "",
						elements: [],
						auto_generated: false
					};
					
					scenes.push(newScene);
					timeline.scenes = scenes;
					
					timelineWidget.inputEl.value = JSON.stringify(timeline, null, 2);
					timelineWidget.inputEl.dispatchEvent(new Event("input", { bubbles: true }));
					
					this.loadTimeline();
				} catch (e) {
					console.error("Failed to add scene:", e);
				}
			};
			
			// Delete scene
			nodeType.prototype.deleteScene = function(sceneId) {
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget) return;
				
				try {
					const jsonStr = timelineWidget.inputEl.value || "{}";
					const timeline = JSON.parse(jsonStr);
					
					timeline.scenes = (timeline.scenes || []).filter(s => s.id !== sceneId);
					
					timelineWidget.inputEl.value = JSON.stringify(timeline, null, 2);
					timelineWidget.inputEl.dispatchEvent(new Event("input", { bubbles: true }));
					
					this.loadTimeline();
				} catch (e) {
					console.error("Failed to delete scene:", e);
				}
			};
			
			// Update scene time
			nodeType.prototype.updateSceneTime = function(sceneId, type, time) {
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget) return;
				
				try {
					const jsonStr = timelineWidget.inputEl.value || "{}";
					const timeline = JSON.parse(jsonStr);
					
					const scene = (timeline.scenes || []).find(s => s.id === sceneId);
					if (scene) {
						if (type === "start") {
							scene.start_time = Math.max(0, Math.min(time, scene.end_time - 0.1));
						} else {
							scene.end_time = Math.max(scene.start_time + 0.1, time);
						}
						
						timelineWidget.inputEl.value = JSON.stringify(timeline, null, 2);
						timelineWidget.inputEl.dispatchEvent(new Event("input", { bubbles: true }));
						
						this.loadTimeline();
					}
				} catch (e) {
					console.error("Failed to update scene time:", e);
				}
			};
			
			// Update scene prompt
			nodeType.prototype.updateScenePrompt = function(sceneId, prompt) {
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget) return;
				
				try {
					const jsonStr = timelineWidget.inputEl.value || "{}";
					const timeline = JSON.parse(jsonStr);
					
					const scene = (timeline.scenes || []).find(s => s.id === sceneId);
					if (scene) {
						scene.prompt = prompt;
						timelineWidget.inputEl.value = JSON.stringify(timeline, null, 2);
						timelineWidget.inputEl.dispatchEvent(new Event("input", { bubbles: true }));
					}
				} catch (e) {
					console.error("Failed to update scene prompt:", e);
				}
			};
			
			// Generate code from prompt
			nodeType.prototype.generateSceneCode = function(sceneId, prompt) {
				// This would trigger a backend call to generate code
				// For now, just mark as needing generation
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget) return;
				
				try {
					const jsonStr = timelineWidget.inputEl.value || "{}";
					const timeline = JSON.parse(jsonStr);
					
					const scene = (timeline.scenes || []).find(s => s.id === sceneId);
					if (scene) {
						scene.prompt = prompt;
						scene.manim_code = ""; // Will be generated on render
						scene.auto_generated = true;
						
						timelineWidget.inputEl.value = JSON.stringify(timeline, null, 2);
						timelineWidget.inputEl.dispatchEvent(new Event("input", { bubbles: true }));
						
						this.loadTimeline();
					}
				} catch (e) {
					console.error("Failed to generate scene code:", e);
				}
			};
			
			// Update scene code
			nodeType.prototype.updateSceneCode = function(sceneId, code) {
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget) return;
				
				try {
					const jsonStr = timelineWidget.inputEl.value || "{}";
					const timeline = JSON.parse(jsonStr);
					
					const scene = (timeline.scenes || []).find(s => s.id === sceneId);
					if (scene) {
						scene.manim_code = code;
						scene.auto_generated = false;
						
						timelineWidget.inputEl.value = JSON.stringify(timeline, null, 2);
						timelineWidget.inputEl.dispatchEvent(new Event("input", { bubbles: true }));
					}
				} catch (e) {
					console.error("Failed to update scene code:", e);
				}
			};
		}
	},
});
