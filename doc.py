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
                    pattern_name, pattern_desc = pattern_data[0], "None"

                pattern_list.append({
                    "name": pattern_name,
                    "desc": pattern_desc
                })
        return pattern_list

    def fill_template(self, data: dict):
        for paragraph in self.document.paragraphs:
            patterns = re.findall("\{\{.+\}\}", paragraph.text)

            for pattern in patterns:
                print(pattern)
                pattern_name = pattern[3:-3:].split(":")[0]
                if pattern_name in data:
                    print(pattern_name)
                    self.replace_text_in_paragraph(paragraph, pattern, data[pattern_name])
        path = f"temp/{random.randint(0, 999999999)}.docx"
        self.document.save(path)
        return path

    @staticmethod
    def replace_text_in_paragraph(paragraph, key, value):
        for item in paragraph.runs:
            print(item.text, key)
            if key in item.text:
                print("REPLACE")
                item.text = item.text.replace(key, value)
