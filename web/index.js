import { app } from "../../scripts/app.js";

app.registerExtension({
	name: "Lattice.Manim",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "ManimScriptNode") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				
				// 1. Resize the node immediately to be wide and tall (Editor style)
				this.setSize([600, 500]);

				// 2. Find the "code" widget and apply "VS Code" styling
				const codeWidget = this.widgets.find((w) => w.name === "code");
				if (codeWidget && codeWidget.inputEl) {
					Object.assign(codeWidget.inputEl.style, {
						fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace",
						fontSize: "14px",
						backgroundColor: "#1e1e1e", // VS Code Dark
						color: "#d4d4d4",           // VS Code Text
						border: "1px solid #3c3c3c",
						borderRadius: "4px",
						padding: "10px",
						lineHeight: "1.5",
						width: "100%",
						height: "350px",            // Force height
						resize: "vertical",         // Allow user resizing
                        whiteSpace: "pre"           // Preserve formatting
					});
                    
                    // Force the widget type to be "customtext" to avoid default Comfy constraints
                    codeWidget.type = "customtext";
				}
				return r;
			};
		}
	},
});
