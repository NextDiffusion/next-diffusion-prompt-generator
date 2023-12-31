import json
import random
import gradio as gr
import modules
from pathlib import Path
from modules import script_callbacks
import modules.scripts as scripts

result_prompt = ""
base_dir = scripts.basedir()
dropdown_options_file = Path(base_dir, "json/dropdown_options.json")
category_data_file = Path(base_dir, "json/category_data.json")
style_data_file = Path(base_dir, "json/style_data.json")
prefix_data_file = Path(base_dir, "json/prefix_data.json")
lighting_data_file = Path(base_dir, "json/lighting_data.json")
lens_data_file = Path(base_dir, "json/lens_data.json")


class Model:
    '''
    Small strut to hold data for the text generator
    '''

    def __init__(self, name) -> None:
        self.name = name
        pass


def populate_dropdown_options():
    path = dropdown_options_file
    with open(path, 'r') as f:
        data = json.load(f)
    category_choices = data["category"]
    style_choices = data["style"]
    lighting_choices = data["lighting"]
    lens_choices = data["lens"]
    return tuple(category_choices), tuple(style_choices), tuple(lighting_choices), tuple(lens_choices),


def add_to_prompt(*args):
    prompt, use_default_negative_prompt = args
    default_negative_prompt = "(worst quality:1.2), (low quality:1.2), (lowres:1.1), (monochrome:1.1), (greyscale), multiple views, comic, sketch, (((bad anatomy))), (((deformed))), (((disfigured))), watermark, multiple_views, mutation hands, mutation fingers, extra fingers, missing fingers, watermark"
    if (use_default_negative_prompt):
        return prompt, default_negative_prompt
    else:
        return prompt, ""


def get_random_prompt(data):
    random_key = random.choice(list(data.keys()))
    random_array = random.choice(data[random_key])
    random_strings = random.sample(random_array, 3)
    return random_strings


def get_correct_prompt(data, selected_dropdown):
    correct_array = data[selected_dropdown]
    random_array = random.choice(correct_array)
    random_strings = random.sample(random_array, 3)
    random_strings.insert(0, selected_dropdown)

    return random_strings


def generate_prompt_output(*args):
    # all imported files
    prefix_path = prefix_data_file
    category_path = category_data_file
    style_path = style_data_file
    lighting_path = lighting_data_file
    lens_path = lens_data_file

    # destructure args
    category, style, lighting, lens, negative_prompt = args

    # Convert variables to lowercase
    category = category.lower()
    style = style.lower()
    lighting = lighting.lower()
    lens = lens.lower()

    # Open category_data.json and grab correct text
    with open(prefix_path, 'r') as f:
        prefix_data = json.load(f)
        prefix_prompt = random.sample(prefix_data, 6)
        modified_prefix_prompt = [f"(({item}))" for item in prefix_prompt]

    # Open category_data.json and grab correct text
    with open(category_path, 'r') as f2:
        category_data = json.load(f2)

    if category == "none":
        category_prompt = ""
    elif category == "random":
        category_prompt = get_random_prompt(category_data)
    else:
        category_prompt = get_correct_prompt(category_data, category)

    # Open style_data.json and grab correct text
    with open(style_path, 'r') as f3:
        style_data = json.load(f3)

    if style == "none":
        style_prompt = ""
    elif style == "random":
        style_prompt = get_random_prompt(style_data)
    else:
        style_prompt = get_correct_prompt(style_data, style)

    # Open lighting_data.json and grab correct text
    with open(lighting_path, 'r') as f4:
        lighting_data = json.load(f4)

    if lighting == "none":
        lighting_prompt = ""
    elif lighting == "random":
        lighting_prompt = get_random_prompt(lighting_data)
    else:
        lighting_prompt = get_correct_prompt(lighting_data, lighting)

    # Open lens_data.json and grab correct text
    with open(lens_path, 'r') as f5:
        lens_data = json.load(f5)

    if lens == "none":
        lens_prompt = ""
    elif lens == "random":
        lens_prompt = get_random_prompt(lens_data)
    else:
        lens_prompt = get_correct_prompt(lens_data, lens)

    prompt_output = modified_prefix_prompt, category_prompt, style_prompt, lighting_prompt, lens_prompt
    prompt_strings = []

    for sublist in prompt_output:
        # Join the sublist elements into a single string
        prompt_string = ", ".join(str(item) for item in sublist)
        if prompt_string:  # Check if the prompt_string is not empty
            prompt_strings.append(prompt_string)

    # Join the non-empty prompt_strings
    final_output = ", ".join(prompt_strings)

    return final_output


def on_ui_tabs():
    # UI structure
    txt2img_prompt = modules.ui.txt2img_paste_fields[0][0]
    img2img_prompt = modules.ui.img2img_paste_fields[0][0]

    txt2img_negative_prompt = modules.ui.txt2img_paste_fields[1][0]
    img2img_negative_prompt = modules.ui.img2img_paste_fields[1][0]

    with gr.Blocks(analytics_enabled=False) as prompt_generator:
        with gr.Tab("Prompt Generator"):
            with gr.Row():  # Use Row to arrange two columns side by side
                with gr.Column():  # Left column for dropdowns
                    category_choices, style_choices, lighting_choices, lens_choices = populate_dropdown_options()

                    with gr.Row():
                        gr.HTML('''<h2 id="input_header">Input 👇</h2>''')
                    with gr.Row().style(equal_height=True):  # Place dropdowns side by side
                        # Create a dropdown to select

                        category_dropdown = gr.Dropdown(
                            choices=category_choices,
                            value=category_choices[1],
                            label="Category", show_label=True
                        )

                        style_dropdown = gr.Dropdown(
                            choices=style_choices,
                            value=style_choices[1],
                            label="Style", show_label=True
                        )
                    with gr.Row():
                        lighting_dropdown = gr.Dropdown(
                            choices=lighting_choices,
                            value=lighting_choices[1],
                            label="Lighting", show_label=True
                        )

                        lens_dropdown = gr.Dropdown(
                            choices=lens_choices,
                            value=lens_choices[1],
                            label="Lens", show_label=True
                        )
                    with gr.Row():
                        gr.HTML('''
                        <hr class="rounded" id="divider">
                    ''')
                    with gr.Row():
                        gr.HTML('''<h2 id="input_header">Links</h2>''')
                    with gr.Row():
                        gr.HTML('''
                        <h3>Stable Diffusion Tutorials⚡</h3>
                        <container>
                            <a href="https://nextdiffusion.ai" target="_blank">
                                <button id="website_button" class="external-link">Website</button>
                            </a>
                            <a href="https://www.youtube.com/channel/UCd9UIUkLnjE-Fj-CGFdU74Q?sub_confirmation=1" target="_blank">
                                <button id="youtube_button" class="external-link">YouTube</button>
                            </a>
                        </container>
                    ''')

                with gr.Column():  # Right column for result_textbox and generate_button
                    # Add a Textbox to display the generated text
                    with gr.Row():
                        gr.HTML('''<h2 id="output_header">Output 👋</h2>''')
                    result_textbox = gr.Textbox(
                        label="Generated Prompt", lines=3)
                    use_default_negative_prompt = gr.Checkbox(
                        label="Include Negative Prompt", value=True, interactive=True, elem_id="negative_prompt_checkbox")
                    setattr(use_default_negative_prompt,
                            "do_not_save_to_config", True)
                    with gr.Row():
                        txt2img = gr.Button("Send to txt2img")
                        img2img = gr.Button("Send to img2img")
                    # Create a button to trigger text generation
                    txt2img.click(add_to_prompt, inputs=[result_textbox, use_default_negative_prompt], outputs=[
                                  txt2img_prompt, txt2img_negative_prompt]).then(None, _js='switch_to_txt2img', inputs=None, outputs=None)
                    img2img.click(add_to_prompt, inputs=[result_textbox, use_default_negative_prompt], outputs=[
                                  img2img_prompt, img2img_negative_prompt]).then(None, _js='switch_to_img2img', inputs=None, outputs=None)
                    generate_button = gr.Button(
                        value="Generate", elem_id="generate_button")

        # Register the callback for the Generate button
        generate_button.click(fn=generate_prompt_output, inputs=[
                              category_dropdown, style_dropdown, lighting_dropdown, lens_dropdown, use_default_negative_prompt], outputs=[result_textbox])

    return (prompt_generator, "Next Diffusion ⚡", "Next Diffusion ⚡"),


script_callbacks.on_ui_tabs(on_ui_tabs)
