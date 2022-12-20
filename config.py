import os
import json


class Config:
    def __init__(self, config_path="config.json"):
        self.default_config = {
            "templates": []
        }
        self.config_path = config_path
        self.data = self.read_config()

    def save(self):
        with open(self.config_path, "w", encoding="utf-8") as file:
            file.write(json.dumps(self.data))

    def read_config(self):
        if self.config_exists():
            with open(self.config_path, "r", encoding="utf-8") as file:
                return json.loads(file.read())

        return self.default_config

    def config_exists(self):
        if not os.path.isfile(self.config_path):
            with open(self.config_path, "w", encoding="utf-8") as file:
                file.write(json.dumps(self.default_config))

            return False

        return True

    def get_template_info(self, template_id: int):
        for template_info in self.data["templates"]:
            if template_info["id"] == template_id:
                return template_info

        return None
