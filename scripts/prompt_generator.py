import json
import random
from tkinter import TRUE
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
lightning_data_file = Path(base_dir, "json/lightning_data.json")
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
    lightning_choices = data["lightning"]
    lens_choices = data["lens"]
    return tuple(category_choices), tuple(style_choices), tuple(lightning_choices), tuple(lens_choices),


def add_to_prompt(*args): 
    prompt, use_default_negative_prompt = args
    default_negative_prompt = "(worst quality:1.2), (low quality:1.2), (lowres:1.1), (monochrome:1.1), (greyscale), multiple views, comic, sketch, (((bad anatomy))), (((deformed))), (((disfigured))), watermark, multiple_views, mutation hands, mutation fingers, extra fingers, missing fingers, watermark"
    if(use_default_negative_prompt):
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
    #all imported files
    prefix_path = prefix_data_file
    category_path = category_data_file
    style_path = style_data_file
    lightning_path = lightning_data_file
    lens_path = lens_data_file

    #destructure args
    category, style, lightning, lens, negative_prompt = args

    # Convert variables to lowercase
    category = category.lower()
    style = style.lower()
    lightning = lightning.lower()
    lens = lens.lower()

    # Open category_data.json and grab correct text
    with open(prefix_path, 'r') as f:
        prefix_data = json.load(f)
        prefix_prompt = random.sample(prefix_data, 6)
        modified_prefix_prompt = [f"(({item}))" for item in prefix_prompt]


    # Open category_data.json and grab correct text
    with open(category_path, 'r') as f2:
        category_data = json.load(f2)
    
    if category == "random":
        category_prompt = get_random_prompt(category_data)
    else:
        category_prompt = get_correct_prompt(category_data, category)


    # Open style_data.json and grab correct text
    with open(style_path, 'r') as f3:
        style_data = json.load(f3)
    
    if style == "random":
        style_prompt = get_random_prompt(style_data)
    else:
        style_prompt = get_correct_prompt(style_data, style)

    # Open lightning_data.json and grab correct text
    with open(lightning_path, 'r') as f4:
        lightning_data = json.load(f4)
    
    if lightning == "random":
        lightning_prompt = get_random_prompt(lightning_data)
    else:
        lightning_prompt = get_correct_prompt(lightning_data, lightning)

    # Open lens_data.json and grab correct text
    with open(lens_path, 'r') as f5:
        lens_data = json.load(f5)
    
    if lens == "random":
        lens_prompt = get_random_prompt(lens_data)
    else:
        lens_prompt = get_correct_prompt(lens_data, lens)


    prompt_output = modified_prefix_prompt, category_prompt, style_prompt, lightning_prompt, lens_prompt
    final_output = ", ".join(", ".join(sublist) for sublist in prompt_output)

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
                    category_choices, style_choices, lightning_choices, lens_choices = populate_dropdown_options()
                    with gr.Row():  # Place dropdowns side by side
                        # Create a dropdown to select
                        category_dropdown = gr.Dropdown(
                            choices=category_choices,
                            value=category_choices[0],
                            label="Category", show_label=True
                        )

                        style_dropdown = gr.Dropdown(
                            choices=style_choices,
                            value=style_choices[0],
                            label="Style", show_label=True
                        )
                    with gr.Row():    
                        lightning_dropdown = gr.Dropdown(
                            choices=lightning_choices,
                            value=lightning_choices[0],
                            label="Lightning", show_label=True
                        )

                        lens_dropdown = gr.Dropdown(
                            choices=lens_choices,
                            value=lens_choices[0],
                            label="Lens", show_label=True
                        )
                    
                with gr.Column():  # Right column for result_textbox and generate_button
                    # Add a Textbox to display the generated text
                    result_textbox = gr.Textbox(label="Generated Prompt", lines=3)
                    use_default_negative_prompt = gr.Checkbox(label="Use default negative prompt?", value=True, interactive=True)
                    setattr(use_default_negative_prompt,"do_not_save_to_config",True)
                    with gr.Row():
                        txt2img = gr.Button("Send to txt2img")
                        img2img = gr.Button("Send to img2img")
                    # Create a button to trigger text generation
                    txt2img.click(add_to_prompt, inputs=[result_textbox, use_default_negative_prompt], outputs=[txt2img_prompt, txt2img_negative_prompt ]).then(None, _js='switch_to_txt2img',inputs=None, outputs=None)
                    img2img.click(add_to_prompt, inputs=[result_textbox, use_default_negative_prompt], outputs=[img2img_prompt, img2img_negative_prompt]).then(None, _js='switch_to_img2img',inputs=None, outputs=None)
                    generate_button = gr.Button(value="Generate", elem_id="generate_button")

        # Register the callback for the Generate button
        generate_button.click(fn=generate_prompt_output, inputs=[category_dropdown, style_dropdown, lightning_dropdown, lens_dropdown, use_default_negative_prompt], outputs=[result_textbox])

    return (prompt_generator, "Next Diffusion ⚡", "Next Diffusion ⚡"),

script_callbacks.on_ui_tabs(on_ui_tabs)
