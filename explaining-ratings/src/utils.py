def merge_to_single_text(all_texts):
    text = ''

    for t in all_texts:
        text += str(t).lower() + ' '

    return text
