import { app } from "../../scripts/app.js";

// Video preview functionality (inspired by ComfyUI-VideoHelperSuite)
// Note: ComfyUI's built-in preview system will handle IMAGE tensor previews
// We can enhance it with video-specific controls

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
				
				// Increase node size to prevent cut-off
				this.setSize([800, 1100]);

				// Make custom code editor collapsible and smaller
				setTimeout(() => {
					const codeWidget = this.widgets.find((w) => w.name === "custom_code");
					if (codeWidget && codeWidget.inputEl) {
						// Hide the original input
						const originalInput = codeWidget.inputEl;
						originalInput.style.display = "none";
						
						// Create collapsible section
						const codeSection = document.createElement("div");
						codeSection.style.cssText = "margin: 10px 0;";
						
						const toggleBtn = document.createElement("button");
						toggleBtn.textContent = "▼ Custom Code (Advanced)";
						toggleBtn.style.cssText = `
							width: 100%;
							padding: 8px;
							background: #444;
							color: #aaa;
							border: 1px solid #666;
							border-radius: 4px;
							cursor: pointer;
							text-align: left;
							font-size: 12px;
						`;
						
						const codeEditor = document.createElement("textarea");
						codeEditor.value = originalInput.value || "";
						codeEditor.placeholder = "# Optional: Custom Manim code to override defaults";
						Object.assign(codeEditor.style, {
							fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace",
							fontSize: "12px",
							backgroundColor: "#1e1e1e",
							color: "#d4d4d4",
							border: "1px solid #3c3c3c",
							borderRadius: "4px",
							padding: "8px",
							lineHeight: "1.5",
							width: "100%",
							height: "150px",
							marginTop: "5px",
							resize: "vertical",
							whiteSpace: "pre",
							display: "none"
						});
						
						codeEditor.addEventListener("input", (e) => {
							originalInput.value = e.target.value;
							originalInput.dispatchEvent(new Event("input", { bubbles: true }));
						});
						
						let isExpanded = false;
						toggleBtn.onclick = () => {
							isExpanded = !isExpanded;
							codeEditor.style.display = isExpanded ? "block" : "none";
							toggleBtn.textContent = isExpanded ? "▲ Hide Custom Code" : "▼ Custom Code (Advanced)";
						};
						
						codeSection.appendChild(toggleBtn);
						codeSection.appendChild(codeEditor);
						
						// Insert before the hidden input
						if (originalInput.parentNode) {
							originalInput.parentNode.insertBefore(codeSection, originalInput);
						}
					}
					
					// Add file upload helper for data input
					this.addDataFileUpload();
				}, 100);
				
				return r;
			};
			
			// Add file upload helper
			nodeType.prototype.addDataFileUpload = function() {
				const widgets = this.widgets || [];
				// Look for the first widget which should be "data"
				if (widgets.length > 0) {
					const dataWidget = widgets[0];
					if (dataWidget && dataWidget.inputEl && dataWidget.inputEl.parentNode) {
						const uploadSection = document.createElement("div");
						uploadSection.style.cssText = `
							margin: 10px 0;
							padding: 10px;
							background: #2a2a2a;
							border-radius: 4px;
							border: 1px dashed #555;
						`;
						
						const label = document.createElement("div");
						label.textContent = "Data Input:";
						label.style.cssText = "color: #aaa; font-size: 11px; margin-bottom: 5px; text-transform: uppercase;";
						
						const helpText = document.createElement("div");
						helpText.innerHTML = `
							<span style="color: #888; font-size: 11px;">
								Connect a data node, or enter file path (CSV/JSON).<br>
								Supports: CSV, JSON, NumPy arrays, Pandas DataFrames
							</span>
						`;
						
						uploadSection.appendChild(label);
						uploadSection.appendChild(helpText);
						
						dataWidget.inputEl.parentNode.insertBefore(uploadSection, dataWidget.inputEl);
					}
				}
			};
		}
		
		// Timeline Scene Node with full timeline UI
		if (nodeData.name === "ManimTimelineSceneNode") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				
				// Increase size to prevent cut-off and give more space
				this.setSize([1400, 1200]);
				
				// Add timeline UI
				setTimeout(() => {
					this.createTimelineUI();
				}, 100);
				
				return r;
			};
			
			// Create timeline UI
			nodeType.prototype.createTimelineUI = function() {
				console.log("[ManimTimeline] Creating timeline UI...");
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget) {
					console.warn("[ManimTimeline] Timeline widget not found, retrying...");
					setTimeout(() => this.createTimelineUI(), 500);
					return;
				}
				
				// Wait for widget to be fully rendered
				if (!timelineWidget.inputEl) {
					console.log("[ManimTimeline] Widget not rendered yet, waiting...");
					setTimeout(() => this.createTimelineUI(), 200);
					return;
				}
				
				console.log("[ManimTimeline] Widget found, creating UI elements...");
				
				const jsonInput = timelineWidget.inputEl;
				const widgetParent = jsonInput.parentNode;
				if (!widgetParent) {
					setTimeout(() => this.createTimelineUI(), 200);
					return;
				}
				
				// Hide the raw JSON widget
				jsonInput.style.display = "none";
				
				// Create timeline container FIRST
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
					position: relative;
					pointer-events: auto;
					z-index: 1;
				`;
				
				// Timeline header
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
				
				// Create visual timeline with time ruler
				const timelineVisual = document.createElement("div");
				timelineVisual.className = "timeline-visual";
				timelineVisual.style.cssText = `
					width: 100%;
					height: 220px;
					background: #1a1a1a;
					border-radius: 6px;
					border: 1px solid #333;
					position: relative;
					margin-bottom: 15px;
					overflow-x: auto;
					overflow-y: hidden;
					pointer-events: auto;
				`;
				
				// Time ruler
				const timeRuler = document.createElement("div");
				timeRuler.className = "time-ruler";
				timeRuler.style.cssText = `
					height: 30px;
					background: #252525;
					border-bottom: 1px solid #444;
					position: relative;
					white-space: nowrap;
					min-width: 100%;
				`;
				
				// Add time markers (0-60 seconds)
				for (let i = 0; i <= 60; i += 5) {
					const marker = document.createElement("div");
					marker.style.cssText = `
						position: absolute;
						left: ${(i / 60) * 100}%;
						height: 100%;
						border-left: 1px solid ${i % 10 === 0 ? '#666' : '#444'};
						padding-left: 4px;
						font-size: 10px;
						color: #888;
						line-height: 30px;
					`;
					marker.textContent = i + 's';
					timeRuler.appendChild(marker);
				}
				
				timelineVisual.appendChild(timeRuler);
				
				// Timeline tracks area (for scene bars)
				const tracksArea = document.createElement("div");
				tracksArea.className = "timeline-tracks";
				tracksArea.style.cssText = `
					height: 190px;
					overflow-y: auto;
					overflow-x: hidden;
					padding: 8px;
					position: relative;
					pointer-events: auto;
				`;
				
				// Custom scrollbar styling (only add once)
				if (!document.getElementById('manim-timeline-scrollbar-style')) {
					const style = document.createElement("style");
					style.id = 'manim-timeline-scrollbar-style';
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
				}
				
				timelineVisual.appendChild(tracksArea);
				timelineContainer.appendChild(timelineVisual);
				
				// Store references
				this.timelineContainer = timelineContainer;
				this.tracksArea = tracksArea;
				this.timeRuler = timeRuler;
				
				// Insert timeline container right before the JSON input widget
				// Find the widget container (usually the parent of the input element)
				const widgetContainer = jsonInput.closest('.widget') || jsonInput.parentElement;
				if (widgetContainer && widgetContainer.parentNode) {
					// Insert before the widget container, not inside it
					widgetContainer.parentNode.insertBefore(timelineContainer, widgetContainer);
				} else {
					// Fallback: insert before jsonInput
					widgetParent.insertBefore(timelineContainer, jsonInput);
				}
				
				// Add toggle button for advanced JSON editing AFTER timeline
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
					const isVisible = jsonInput.style.display !== "none";
					jsonInput.style.display = isVisible ? "none" : "block";
					jsonToggle.textContent = isVisible ? "Show Advanced JSON Editor" : "Hide JSON Editor";
				};
				// Insert JSON toggle right before the JSON input widget container
				const widgetContainer = jsonInput.closest('.widget') || jsonInput.parentElement;
				if (widgetContainer && widgetContainer.parentNode) {
					widgetContainer.parentNode.insertBefore(jsonToggle, widgetContainer);
				} else {
					widgetParent.insertBefore(jsonToggle, jsonInput);
				}
				
				// Load timeline after everything is inserted
				console.log("[ManimTimeline] UI created, loading timeline...");
				setTimeout(() => {
					this.loadTimeline();
				}, 100);
			};
			
			// Load timeline from JSON
			nodeType.prototype.loadTimeline = function() {
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget) {
					console.warn("[ManimTimeline] Timeline widget not found in loadTimeline");
					return;
				}
				if (!this.tracksArea) {
					console.warn("[ManimTimeline] Tracks area not found, UI may not be initialized");
					return;
				}
				
				try {
					const jsonStr = timelineWidget.inputEl.value || "{}";
					console.log("[ManimTimeline] Loading timeline from JSON:", jsonStr.substring(0, 100));
					const timeline = JSON.parse(jsonStr);
					const scenes = timeline.scenes || [];
					console.log(`[ManimTimeline] Found ${scenes.length} scenes`);
					
				// Clear tracks and details
				if (this.tracksArea) {
					this.tracksArea.innerHTML = "";
				}
				if (this.detailsArea) {
					this.detailsArea.innerHTML = "";
				}
				
				// Render each scene as a visual bar and detail card
				scenes.forEach((scene, index) => {
					this.renderSceneLayer(scene, index);
				});
				} catch (e) {
					console.error("Failed to load timeline:", e);
				}
			};
			
			// Render a scene as a timeline layer
			nodeType.prototype.renderSceneLayer = function(scene, index) {
				// Create visual timeline bar FIRST
				if (this.tracksArea) {
					const visualBar = document.createElement("div");
					visualBar.className = "timeline-visual-bar";
					visualBar.dataset.sceneId = scene.id;
					const duration = this.getTimelineDuration();
					const leftPercent = duration > 0 ? (scene.start_time / duration) * 100 : 0;
					const widthPercent = duration > 0 ? ((scene.end_time - scene.start_time) / duration) * 100 : 10;
					
					visualBar.style.cssText = `
						position: absolute;
						left: ${leftPercent}%;
						width: ${widthPercent}%;
						top: ${index * 50}px;
						height: 40px;
						background: linear-gradient(135deg, #0074D9 0%, #0056b3 100%);
						border-radius: 4px;
						border: 1px solid #0056b3;
						cursor: move;
						display: flex;
						align-items: center;
						justify-content: center;
						color: white;
						font-size: 11px;
						font-weight: 500;
						box-shadow: 0 2px 4px rgba(0,116,217,0.3);
						transition: all 0.2s;
					`;
					visualBar.textContent = `Scene ${scene.id}`;
					visualBar.title = `${scene.start_time.toFixed(2)}s - ${scene.end_time.toFixed(2)}s`;
					
					visualBar.onmouseenter = () => {
						visualBar.style.transform = "scaleY(1.1)";
						visualBar.style.boxShadow = "0 4px 8px rgba(0,116,217,0.5)";
					};
					visualBar.onmouseleave = () => {
						visualBar.style.transform = "scaleY(1)";
						visualBar.style.boxShadow = "0 2px 4px rgba(0,116,217,0.3)";
					};
					
					// Make draggable
					this.makeTimelineBarDraggable(visualBar, scene);
					
					this.tracksArea.appendChild(visualBar);
				}
				
				// Create detail card (collapsible)
				if (!this.detailsArea) {
					this.detailsArea = document.createElement("div");
					this.detailsArea.className = "timeline-details";
					this.detailsArea.style.cssText = `
						margin-top: 15px;
						max-height: 400px;
						overflow-y: auto;
					`;
					this.timelineContainer.appendChild(this.detailsArea);
				}
				
				const layer = document.createElement("div");
				layer.className = "timeline-layer";
				layer.dataset.sceneId = scene.id;
				layer.style.cssText = `
					margin: 10px 0;
					padding: 12px;
					background: linear-gradient(135deg, #2d2d2d 0%, #252525 100%);
					border-radius: 6px;
					border-left: 3px solid #0074D9;
					border: 1px solid #444;
					box-shadow: 0 2px 4px rgba(0,0,0,0.2);
				`;
				
				// Collapsible header
				const layerHeader = document.createElement("div");
				layerHeader.style.cssText = `
					display: flex;
					justify-content: space-between;
					align-items: center;
					cursor: pointer;
					padding: 5px;
					margin: -5px -5px 5px -5px;
					border-radius: 4px;
				`;
				layerHeader.onmouseenter = () => layerHeader.style.background = "#333";
				layerHeader.onmouseleave = () => layerHeader.style.background = "transparent";
				
				const layerTitle = document.createElement("div");
				const duration = (scene.end_time - scene.start_time).toFixed(2);
				layerTitle.innerHTML = `
					<span style="color: #0074D9; font-weight: 600;">Scene ${scene.id}</span>
					<span style="color: #888; font-size: 11px; margin-left: 8px;">${scene.start_time.toFixed(2)}s - ${scene.end_time.toFixed(2)}s</span>
				`;
				
				const expandBtn = document.createElement("span");
				expandBtn.textContent = "▼";
				expandBtn.style.cssText = "color: #888; font-size: 10px;";
				
				layerHeader.appendChild(layerTitle);
				layerHeader.appendChild(expandBtn);
				
				const layerContent = document.createElement("div");
				layerContent.style.cssText = "display: none;";
				
				let isExpanded = false;
				layerHeader.onclick = () => {
					isExpanded = !isExpanded;
					layerContent.style.display = isExpanded ? "block" : "none";
					expandBtn.textContent = isExpanded ? "▲" : "▼";
				};
				
				layer.appendChild(layerHeader);
				layer.appendChild(layerContent);
				
				// Add time controls to layerContent
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
				inPoint.onchange = () => {
					this.updateSceneTime(scene.id, "start", parseFloat(inPoint.value));
					this.loadTimeline(); // Refresh visual
				};
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
				outPoint.onchange = () => {
					this.updateSceneTime(scene.id, "end", parseFloat(outPoint.value));
					this.loadTimeline(); // Refresh visual
				};
				outGroup.appendChild(outLabel);
				outGroup.appendChild(outPoint);
				
				timeControls.appendChild(inGroup);
				timeControls.appendChild(outGroup);
				layerContent.appendChild(timeControls);
				
				// Add prompt and code sections to layerContent
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
					height: 60px;
					padding: 8px;
					background: #1a1a1a;
					color: #fff;
					border: 1px solid #555;
					border-radius: 4px;
					font-family: inherit;
					font-size: 13px;
					resize: vertical;
				`;
				promptInput.onchange = () => this.updateScenePrompt(scene.id, promptInput.value);
				promptInput.oninput = () => this.updateScenePrompt(scene.id, promptInput.value);
				promptSection.appendChild(promptLabel);
				promptSection.appendChild(promptInput);
				layerContent.appendChild(promptSection);
				
				const generateBtn = document.createElement("button");
				generateBtn.innerHTML = "<span style='margin-right: 6px;'>⚡</span> Generate Code";
				generateBtn.style.cssText = `
					width: 100%;
					margin-bottom: 12px;
					padding: 8px;
					background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
					color: white;
					border: none;
					border-radius: 6px;
					cursor: pointer;
					font-weight: 500;
					font-size: 12px;
				`;
				generateBtn.onclick = () => {
					generateBtn.textContent = "Generating...";
					generateBtn.disabled = true;
					setTimeout(() => {
						this.generateSceneCode(scene.id, promptInput.value);
						generateBtn.innerHTML = "<span style='margin-right: 6px;'>⚡</span> Generate Code";
						generateBtn.disabled = false;
					}, 100);
				};
				layerContent.appendChild(generateBtn);
				
				// Code editor section
				const codeSection = document.createElement("div");
				const codeToggle = document.createElement("button");
				codeToggle.innerHTML = "<span style='margin-right: 6px;'>▼</span> Edit Code";
				codeToggle.style.cssText = `
					width: 100%;
					padding: 8px;
					background: #333;
					color: #fff;
					border: 1px solid #555;
					border-radius: 6px;
					cursor: pointer;
					text-align: left;
					font-size: 12px;
				`;
				const codeEditor = document.createElement("textarea");
				codeEditor.value = scene.manim_code || "";
				codeEditor.placeholder = "# Your Manim code here";
				codeEditor.style.cssText = `
					width: 100%;
					height: 150px;
					margin-top: 5px;
					padding: 8px;
					background: #1e1e1e;
					color: #d4d4d4;
					border: 1px solid #555;
					border-radius: 4px;
					font-family: 'Consolas', 'Monaco', monospace;
					font-size: 11px;
					display: none;
					resize: vertical;
				`;
				codeEditor.onchange = () => this.updateSceneCode(scene.id, codeEditor.value);
				codeEditor.oninput = () => this.updateSceneCode(scene.id, codeEditor.value);
				
				let codeExpanded = false;
				codeToggle.onclick = () => {
					codeExpanded = !codeExpanded;
					codeEditor.style.display = codeExpanded ? "block" : "none";
					codeToggle.innerHTML = codeExpanded 
						? "<span style='margin-right: 6px;'>▲</span> Hide Code"
						: "<span style='margin-right: 6px;'>▼</span> Edit Code";
				};
				
				if (scene.manim_code && scene.manim_code.trim()) {
					codeExpanded = true;
					codeEditor.style.display = "block";
					codeToggle.innerHTML = "<span style='margin-right: 6px;'>▲</span> Hide Code";
				}
				
				codeSection.appendChild(codeToggle);
				codeSection.appendChild(codeEditor);
				layerContent.appendChild(codeSection);
				
				// Add delete button
				const deleteBtn = document.createElement("button");
				deleteBtn.textContent = "Delete Scene";
				deleteBtn.style.cssText = `
					width: 100%;
					margin-top: 8px;
					padding: 6px;
					background: #dc3545;
					color: white;
					border: none;
					border-radius: 4px;
					cursor: pointer;
					font-size: 11px;
				`;
				deleteBtn.onclick = () => {
					if (confirm(`Delete Scene ${scene.id}?`)) {
						this.deleteScene(scene.id);
					}
				};
				layerContent.appendChild(deleteBtn);
				
				// Add to a separate details area (not in visual timeline)
				if (!this.detailsArea) {
					this.detailsArea = document.createElement("div");
					this.detailsArea.className = "timeline-details";
					this.detailsArea.style.cssText = `
						margin-top: 15px;
						max-height: 400px;
						overflow-y: auto;
					`;
					timelineContainer.appendChild(this.detailsArea);
				}
				this.detailsArea.appendChild(layer);
			};
			
			// Get timeline duration for visual scaling
			nodeType.prototype.getTimelineDuration = function() {
				const timelineWidget = this.widgets.find((w) => w.name === "timeline_json");
				if (!timelineWidget || !timelineWidget.inputEl) return 60;
				
				try {
					const jsonStr = timelineWidget.inputEl.value || "{}";
					const timeline = JSON.parse(jsonStr);
					if (timeline.audio_duration && timeline.audio_duration > 0) {
						return Math.max(timeline.audio_duration, 60);
					}
					const scenes = timeline.scenes || [];
					if (scenes.length > 0) {
						const maxEnd = Math.max(...scenes.map(s => s.end_time || 0));
						return Math.max(maxEnd, 60);
					}
				} catch (e) {
					console.error("Failed to parse timeline:", e);
				}
				return 60; // Default 60 seconds
			};
			
			// Make timeline bar draggable
			nodeType.prototype.makeTimelineBarDraggable = function(bar, scene) {
				let isDragging = false;
				let dragStartX = 0;
				let startTime = 0;
				
				bar.onmousedown = (e) => {
					isDragging = true;
					dragStartX = e.clientX;
					startTime = scene.start_time;
					bar.style.cursor = "grabbing";
					e.preventDefault();
				};
				
				document.addEventListener("mousemove", (e) => {
					if (!isDragging) return;
					
					const duration = this.getTimelineDuration();
					const barRect = bar.parentElement.getBoundingClientRect();
					const deltaX = e.clientX - dragStartX;
					const deltaTime = (deltaX / barRect.width) * duration;
					const newStartTime = Math.max(0, startTime + deltaTime);
					const sceneDuration = scene.end_time - scene.start_time;
					const newEndTime = newStartTime + sceneDuration;
					
					// Update visual position
					const leftPercent = (newStartTime / duration) * 100;
					bar.style.left = `${leftPercent}%`;
					
					// Update scene times
					this.updateSceneTime(scene.id, "start", newStartTime);
					this.updateSceneTime(scene.id, "end", newEndTime);
				});
				
				document.addEventListener("mouseup", () => {
					if (isDragging) {
						isDragging = false;
						bar.style.cursor = "move";
						this.loadTimeline(); // Refresh to sync
					}
				});
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
