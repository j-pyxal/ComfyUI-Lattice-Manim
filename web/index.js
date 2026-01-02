import { app } from "../../scripts/app.js";

app.registerExtension({
	name: "Lattice.Manim",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "ManimScriptNode") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				
				// Find the "code" widget and style it nicely
				const codeWidget = this.widgets.find((w) => w.name === "code");
				if (codeWidget && codeWidget.inputEl) {
					// Apply "Matrix" style to the text area
					Object.assign(codeWidget.inputEl.style, {
						fontFamily: "monospace",
						backgroundColor: "#1e1e1e",
						color: "#00ff41", // Matrix green
						border: "1px solid #333",
						padding: "10px",
						borderRadius: "4px"
					});
					codeWidget.inputEl.rows = 15;
				}
				return r;
			};
		}
	},
});
