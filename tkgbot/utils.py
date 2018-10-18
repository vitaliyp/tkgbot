def escape_html_characters(text: str):
    result_text = text
    result_text = result_text.replace('&', '&amp;')
    result_text = result_text.replace('<', '&lt;')
    result_text = result_text.replace('>', '&gt;')
    result_text = result_text.replace('"', '&quot;')

    return result_text
