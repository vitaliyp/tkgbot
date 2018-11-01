import bs4

from tkgbot.utils import intersperse
from .components import (
    CommentLineBreak,
    CommentText,
    CommentImage,
    CommentLink,
)


def parse_tag(tag: bs4.Tag):
    parts_list = []

    for child in tag.children:
        if isinstance(child, bs4.NavigableString):
            string = str(child.string)
            # replace &nbsp with spaces
            string = string.replace(chr(160), ' ')
            if string and string != '\n':
                parts_list.append(CommentText(string))
        if isinstance(child, bs4.Tag):
            tag_name = child.name
            if tag_name == 'a':
                href = child.get('href')
                text = ' '.join(string for string in child.stripped_strings if string)
                parts_list.append(CommentLink(text=text, href=href))
            elif tag_name == 'p':
                parsed_components = parse_tag(child)
                if parsed_components:
                    parts_list.extend(parsed_components)
                    parts_list.append(CommentLineBreak())
            elif tag_name == 'br':
                parts_list.append(CommentLineBreak())
            elif tag_name == 'img':
                src = child.get('src')
                parts_list.append(CommentImage(src))
            elif tag_name in ('ul', 'ol'):
                parsed_components = parse_tag(child)
                if parsed_components:
                    parts_list.extend(parsed_components)
            elif tag_name == 'li':
                parsed_components = parse_tag(child)
                if parsed_components:
                    parts_list.append(CommentText('  ◦ '))
                    parts_list.extend(parsed_components)
                    parts_list.append(CommentLineBreak())
            elif tag_name == 'table':
                parsed_components = parse_tag(child)
                if parsed_components:
                    parts_list.extend(parsed_components)
            elif tag_name == 'tr':
                parsed_components = parse_tag(child)
                if parsed_components:
                    row_components = intersperse(parsed_components, CommentText(' | '))
                    parts_list.extend(row_components)
                    parts_list.append(CommentLineBreak())
            else:
                parts_list.extend(parse_tag(child))

    return parts_list
