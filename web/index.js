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
				
				this.setSize([1000, 900]);
				
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
				
				// Hide the raw JSON widget (make it collapsible for advanced users)
				if (timelineWidget.inputEl) {
					timelineWidget.inputEl.style.display = "none";
					
					// Add toggle button for advanced JSON editing
					const jsonToggle = document.createElement("button");
					jsonToggle.textContent = "Show Advanced JSON Editor";
					jsonToggle.style.cssText = `
						width: 100%;
						margin: 5px 0;
						padding: 6px;
						background: #444;
						color: #aaa;
						border: 1px solid #666;
						border-radius: 3px;
						cursor: pointer;
						font-size: 11px;
					`;
					jsonToggle.onclick = () => {
						const isVisible = timelineWidget.inputEl.style.display !== "none";
						timelineWidget.inputEl.style.display = isVisible ? "none" : "block";
						jsonToggle.textContent = isVisible ? "Show Advanced JSON Editor" : "Hide JSON Editor";
					};
					
					if (timelineWidget.inputEl.parentNode) {
						timelineWidget.inputEl.parentNode.insertBefore(jsonToggle, timelineWidget.inputEl);
					}
				}
				
				// Create timeline container with better styling
				const timelineContainer = document.createElement("div");
				timelineContainer.className = "manim-timeline-container";
				timelineContainer.style.cssText = `
					width: 100%;
					margin: 15px 0;
					padding: 15px;
					background: linear-gradient(135deg, #2a2a2a 0%, #1e1e1e 100%);
					border-radius: 8px;
					border: 1px solid #444;
					box-shadow: 0 2px 8px rgba(0,0,0,0.3);
					font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
				`;
				
				// Timeline header with better design
				const header = document.createElement("div");
				header.style.cssText = `
					display: flex;
					justify-content: space-between;
					align-items: center;
					margin-bottom: 15px;
					padding-bottom: 12px;
					border-bottom: 2px solid #444;
				`;
				
				const title = document.createElement("div");
				title.innerHTML = `<span style="font-size: 16px; font-weight: 600; color: #fff; letter-spacing: 0.5px;">Timeline Editor</span>`;
				
				const addSceneBtn = document.createElement("button");
				addSceneBtn.innerHTML = "<span style='font-size: 16px; margin-right: 4px;'>+</span> Add Scene";
				addSceneBtn.style.cssText = `
					padding: 8px 16px;
					background: linear-gradient(135deg, #0074D9 0%, #0056b3 100%);
					color: white;
					border: none;
					border-radius: 6px;
					cursor: pointer;
					font-weight: 500;
					font-size: 13px;
					transition: all 0.2s;
					box-shadow: 0 2px 4px rgba(0,116,217,0.3);
				`;
				addSceneBtn.onmouseenter = () => {
					addSceneBtn.style.transform = "translateY(-1px)";
					addSceneBtn.style.boxShadow = "0 4px 8px rgba(0,116,217,0.4)";
				};
				addSceneBtn.onmouseleave = () => {
					addSceneBtn.style.transform = "translateY(0)";
					addSceneBtn.style.boxShadow = "0 2px 4px rgba(0,116,217,0.3)";
				};
				addSceneBtn.onclick = () => this.addNewScene();
				
				header.appendChild(title);
				header.appendChild(addSceneBtn);
				timelineContainer.appendChild(header);
				
				// Timeline tracks area with better styling
				const tracksArea = document.createElement("div");
				tracksArea.className = "timeline-tracks";
				tracksArea.style.cssText = `
					max-height: 500px;
					overflow-y: auto;
					overflow-x: hidden;
					padding: 8px;
					background: #1a1a1a;
					border-radius: 6px;
					border: 1px solid #333;
				`;
				
				// Custom scrollbar styling
				const style = document.createElement("style");
				style.textContent = `
					.manim-timeline-container .timeline-tracks::-webkit-scrollbar {
						width: 8px;
					}
					.manim-timeline-container .timeline-tracks::-webkit-scrollbar-track {
						background: #1a1a1a;
						border-radius: 4px;
					}
					.manim-timeline-container .timeline-tracks::-webkit-scrollbar-thumb {
						background: #555;
						border-radius: 4px;
					}
					.manim-timeline-container .timeline-tracks::-webkit-scrollbar-thumb:hover {
						background: #666;
					}
				`;
				document.head.appendChild(style);
				
				timelineContainer.appendChild(tracksArea);
				
				// Load and render timeline
				this.timelineContainer = timelineContainer;
				this.tracksArea = tracksArea;
				this.loadTimeline();
				
				// Insert before timeline_json widget
				if (timelineWidget.inputEl && timelineWidget.inputEl.parentNode) {
					timelineWidget.inputEl.parentNode.insertBefore(
						timelineContainer,
						timelineWidget.inputEl.parentNode.firstChild
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
					margin: 10px 0;
					padding: 15px;
					background: linear-gradient(135deg, #2d2d2d 0%, #252525 100%);
					border-radius: 8px;
					border-left: 4px solid #0074D9;
					border: 1px solid #444;
					box-shadow: 0 2px 6px rgba(0,0,0,0.2);
					transition: all 0.2s;
				`;
				
				layer.onmouseenter = () => {
					layer.style.borderColor = "#0074D9";
					layer.style.boxShadow = "0 4px 12px rgba(0,116,217,0.3)";
				};
				layer.onmouseleave = () => {
					layer.style.borderColor = "#444";
					layer.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";
				};
				
				// Layer header with better design
				const layerHeader = document.createElement("div");
				layerHeader.style.cssText = `
					display: flex;
					justify-content: space-between;
					align-items: center;
					margin-bottom: 12px;
					padding-bottom: 10px;
					border-bottom: 1px solid #444;
				`;
				
				const layerTitle = document.createElement("div");
				const duration = (scene.end_time - scene.start_time).toFixed(2);
				layerTitle.innerHTML = `
					<span style="color: #0074D9; font-weight: 600; font-size: 14px;">Scene ${scene.id}</span>
					<span style="color: #888; font-size: 12px; margin-left: 8px;">${scene.start_time.toFixed(2)}s - ${scene.end_time.toFixed(2)}s (${duration}s)</span>
				`;
				
				const deleteBtn = document.createElement("button");
				deleteBtn.innerHTML = "×";
				deleteBtn.style.cssText = `
					background: #dc3545;
					color: white;
					border: none;
					border-radius: 4px;
					width: 28px;
					height: 28px;
					cursor: pointer;
					font-size: 18px;
					line-height: 1;
					transition: all 0.2s;
					font-weight: bold;
				`;
				deleteBtn.onmouseenter = () => {
					deleteBtn.style.background = "#c82333";
					deleteBtn.style.transform = "scale(1.1)";
				};
				deleteBtn.onmouseleave = () => {
					deleteBtn.style.background = "#dc3545";
					deleteBtn.style.transform = "scale(1)";
				};
				deleteBtn.onclick = () => {
					if (confirm(`Delete Scene ${scene.id}?`)) {
						this.deleteScene(scene.id);
					}
				};
				
				layerHeader.appendChild(layerTitle);
				layerHeader.appendChild(deleteBtn);
				layer.appendChild(layerHeader);
				
				// Time controls (in/out points) with better layout
				const timeControls = document.createElement("div");
				timeControls.style.cssText = `
					display: grid;
					grid-template-columns: 1fr 1fr;
					gap: 12px;
					margin-bottom: 12px;
				`;
				
				const inGroup = document.createElement("div");
				inGroup.style.cssText = "display: flex; flex-direction: column; gap: 4px;";
				const inLabel = document.createElement("label");
				inLabel.textContent = "In Point (seconds)";
				inLabel.style.cssText = "color: #aaa; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;";
				const inPoint = document.createElement("input");
				inPoint.type = "number";
				inPoint.value = scene.start_time;
				inPoint.step = 0.1;
				inPoint.min = 0;
				inPoint.style.cssText = `
					width: 100%;
					padding: 8px;
					background: #1a1a1a;
					color: #fff;
					border: 1px solid #555;
					border-radius: 4px;
					font-size: 13px;
					transition: border-color 0.2s;
				`;
				inPoint.onfocus = () => inPoint.style.borderColor = "#0074D9";
				inPoint.onblur = () => inPoint.style.borderColor = "#555";
				inPoint.onchange = () => this.updateSceneTime(scene.id, "start", parseFloat(inPoint.value));
				inGroup.appendChild(inLabel);
				inGroup.appendChild(inPoint);
				
				const outGroup = document.createElement("div");
				outGroup.style.cssText = "display: flex; flex-direction: column; gap: 4px;";
				const outLabel = document.createElement("label");
				outLabel.textContent = "Out Point (seconds)";
				outLabel.style.cssText = "color: #aaa; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;";
				const outPoint = document.createElement("input");
				outPoint.type = "number";
				outPoint.value = scene.end_time;
				outPoint.step = 0.1;
				outPoint.min = 0.1;
				outPoint.style.cssText = inPoint.style.cssText;
				outPoint.onfocus = () => outPoint.style.borderColor = "#0074D9";
				outPoint.onblur = () => outPoint.style.borderColor = "#555";
				outPoint.onchange = () => this.updateSceneTime(scene.id, "end", parseFloat(outPoint.value));
				outGroup.appendChild(outLabel);
				outGroup.appendChild(outPoint);
				
				timeControls.appendChild(inGroup);
				timeControls.appendChild(outGroup);
				layer.appendChild(timeControls);
				
				// Prompt input section with better styling
				const promptSection = document.createElement("div");
				promptSection.style.cssText = "margin-bottom: 12px;";
				
				const promptLabel = document.createElement("label");
				promptLabel.textContent = "Visual Prompt";
				promptLabel.style.cssText = "display: block; color: #fff; margin-bottom: 6px; font-size: 12px; font-weight: 500;";
				
				const promptInput = document.createElement("textarea");
				promptInput.value = scene.prompt || "";
				promptInput.placeholder = "Describe what you want to see (e.g., 'A blue circle rotating in the center')";
				promptInput.style.cssText = `
					width: 100%;
					height: 70px;
					padding: 10px;
					background: #1a1a1a;
					color: #fff;
					border: 1px solid #555;
					border-radius: 4px;
					font-family: inherit;
					font-size: 13px;
					resize: vertical;
					transition: border-color 0.2s;
				`;
				promptInput.onfocus = () => promptInput.style.borderColor = "#0074D9";
				promptInput.onblur = () => promptInput.style.borderColor = "#555";
				promptInput.onchange = () => this.updateScenePrompt(scene.id, promptInput.value);
				promptInput.oninput = () => this.updateScenePrompt(scene.id, promptInput.value);
				
				promptSection.appendChild(promptLabel);
				promptSection.appendChild(promptInput);
				layer.appendChild(promptSection);
				
				// Generate button with better styling
				const generateBtn = document.createElement("button");
				generateBtn.innerHTML = "<span style='margin-right: 6px;'>⚡</span> Generate Code from Prompt";
				generateBtn.style.cssText = `
					width: 100%;
					margin-bottom: 12px;
					padding: 10px;
					background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
					color: white;
					border: none;
					border-radius: 6px;
					cursor: pointer;
					font-weight: 500;
					font-size: 13px;
					transition: all 0.2s;
					box-shadow: 0 2px 4px rgba(40,167,69,0.3);
				`;
				generateBtn.onmouseenter = () => {
					generateBtn.style.transform = "translateY(-1px)";
					generateBtn.style.boxShadow = "0 4px 8px rgba(40,167,69,0.4)";
				};
				generateBtn.onmouseleave = () => {
					generateBtn.style.transform = "translateY(0)";
					generateBtn.style.boxShadow = "0 2px 4px rgba(40,167,69,0.3)";
				};
				generateBtn.onclick = () => {
					generateBtn.textContent = "Generating...";
					generateBtn.disabled = true;
					setTimeout(() => {
						this.generateSceneCode(scene.id, promptInput.value);
						generateBtn.innerHTML = "<span style='margin-right: 6px;'>⚡</span> Generate Code from Prompt";
						generateBtn.disabled = false;
					}, 100);
				};
				layer.appendChild(generateBtn);
				
				// Code editor section with better design
				const codeSection = document.createElement("div");
				codeSection.style.cssText = "margin-top: 12px; border-top: 1px solid #444; padding-top: 12px;";
				
				const codeToggle = document.createElement("button");
				codeToggle.innerHTML = "<span style='margin-right: 6px;'>▼</span> Edit Manim Code";
				codeToggle.style.cssText = `
					width: 100%;
					padding: 10px;
					background: #333;
					color: #fff;
					border: 1px solid #555;
					border-radius: 6px;
					cursor: pointer;
					text-align: left;
					font-weight: 500;
					font-size: 13px;
					transition: all 0.2s;
				`;
				codeToggle.onmouseenter = () => codeToggle.style.background = "#3a3a3a";
				codeToggle.onmouseleave = () => codeToggle.style.background = "#333";
				
				const codeEditor = document.createElement("textarea");
				codeEditor.value = scene.manim_code || "";
				codeEditor.placeholder = "# Your Manim code here\n# Example:\ncircle = Circle(radius=1, color=BLUE)\nself.play(Create(circle))";
				codeEditor.style.cssText = `
					width: 100%;
					height: 250px;
					margin-top: 8px;
					padding: 12px;
					background: #1e1e1e;
					color: #d4d4d4;
					border: 1px solid #555;
					border-radius: 4px;
					font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
					font-size: 12px;
					line-height: 1.6;
					display: none;
					resize: vertical;
					tab-size: 4;
					transition: border-color 0.2s;
				`;
				codeEditor.onfocus = () => codeEditor.style.borderColor = "#0074D9";
				codeEditor.onblur = () => codeEditor.style.borderColor = "#555";
				codeEditor.onchange = () => this.updateSceneCode(scene.id, codeEditor.value);
				codeEditor.oninput = () => this.updateSceneCode(scene.id, codeEditor.value);
				
				let codeExpanded = false;
				codeToggle.onclick = () => {
					codeExpanded = !codeExpanded;
					codeEditor.style.display = codeExpanded ? "block" : "none";
					codeToggle.innerHTML = codeExpanded 
						? "<span style='margin-right: 6px;'>▲</span> Hide Code Editor"
						: "<span style='margin-right: 6px;'>▼</span> Edit Manim Code";
					if (codeExpanded) {
						setTimeout(() => codeEditor.focus(), 100);
					}
				};
				
				// Show code editor if code exists
				if (scene.manim_code && scene.manim_code.trim()) {
					codeExpanded = true;
					codeEditor.style.display = "block";
					codeToggle.innerHTML = "<span style='margin-right: 6px;'>▲</span> Hide Code Editor";
				}
				
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
