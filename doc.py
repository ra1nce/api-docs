import random
import re

from docx import Document


class DocTemplate:
    def __init__(self, file_path: str):
        self.document = Document(file_path)

    def get_patterns_from_template(self):
        pattern_list = []

        for paragraph in self.document.paragraphs:
            patterns = re.findall("\{\{.+\}\}", paragraph.text)
            for pattern in patterns:
                pattern_data = pattern[3:-3:].split(":")
                if len(pattern_data) == 2:
                    pattern_name, pattern_desc = pattern_data
                else:
                    pattern_name, pattern_desc = pattern_data[0], "Nonei"

                if any(map(lambda i: i["name"] == pattern_name, pattern_list)):
                    continue

                pattern_list.append({
                    "name": pattern_name,
                    "desc": pattern_desc
                })
        return pattern_list

    def fill_template(self, data: dict):
        for paragraph in self.document.paragraphs:
            patterns = re.findall("\{\{.+\}\}", paragraph.text)

            for pattern in patterns:
                pattern_name = pattern[3:-3:].split(":")[0]
                if pattern_name in data:
                    self.replace_text_in_paragraph(paragraph, data[pattern_name])

        path = f"temp/{random.randint(0, 999999999)}.docx"
        self.document.save(path)
        return path

    @staticmethod
    def replace_text_in_paragraph(paragraph, value):
        items = []
        close_char_count = 0
        is_open = False

        for item in paragraph.runs:
            if is_open:
                items.append(item)
                close_char_count += item.text.count("}")
            else:
                if "{" in item.text:
                    is_open = True
                    items.append(item)

                    close_char_count += item.text.count("}")

            if close_char_count == 2:
                break

        items[0].text = value

        for item in items[1:]:
            item.text = ""    

