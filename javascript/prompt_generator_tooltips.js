//Basically copied and adapted from AUTOMATIC1111 implementation of the main UI
// mouseover tooltips for various UI elements in the form of "UI element label"="Tooltip text".

prompt_generator_titles = {
	"Category": "Refers to the primary category for the prompt output",
	"Style": "Determines the main style for the prompt output",
	"Lightning": "Represents the lightning strategy used for the prompt output",
	"Lens": "Specifies the lens parameter used for the prompt output",
	"Use default negative prompt?": "Checked: Default negative prompt sent. Unchecked: Empty string sent."
}

onUiUpdate(function () {
	gradioApp().querySelectorAll('span, button, select, p').forEach(function (span) {
		tooltip = prompt_generator_titles[span.textContent];

		if (!tooltip) {
			tooltip = prompt_generator_titles[span.value];
		}

		if (!tooltip) {
			for (const c of span.classList) {
				if (c in prompt_generator_titles) {
					tooltip = prompt_generator_titles[c];
					break;
				}
			}
		}

		if (tooltip) {
			span.title = tooltip;
		}
	})


	gradioApp().querySelectorAll('select').forEach(function (select) {
		if (select.onchange != null) return;

		select.onchange = function () {
			select.title = prompt_generator_titles[select.value] || "";
		}
	})
})
