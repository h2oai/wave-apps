from transformers import pipeline

# This function takes input text, runs an NLP model to generate new text, and returns wave UI elements
def get_textgeneration_content(starter_text, num_words_to_generate):
    if num_words_to_generate is None:
        text = "H2O is one of the best tools for any machine learning team to have when dealing with large volumes " \
               "of data. H2O helps improve"
    else:
        text = starter_text

    items = [
        ui.text_xl('Enter text to begin generation: '),
        ui.textbox(
            name='input_text',
            label='',
            value=text,
            multiline=True
        ),
        ui.separator(),
        ui.slider(
            name='num_words_to_generate',
            label="Number of Words to Generation",
            min=5,
            max=50,
            step=1,
            value=num_words_to_generate if num_words_to_generate else 20
        ),
        ui.button(name='online_generate_button', label='Generate', primary=True)
    ]

    if num_words_to_generate is not None:

        model = pipeline("text-generation")
        result = model(text, max_length=num_words_to_generate + len(text.split()), do_sample=False)[0]

        items.append(ui.text(result["generated_text"]))
    else:
        items.append(ui.text('Enter text to see results.'))

    return items
