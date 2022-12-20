import os

from random import randint
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename

from doc import DocTemplate
from config import Config


config = Config()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "UPLOADED_FILES"


@app.route('/upload_template', methods=['POST'])
def upload_template():
    info = dict(request.form)
    file = request.files['file']

    if file:
        file_id = randint(1, 999999999)
        file_name = secure_filename(f"{file_id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_path)

        template = DocTemplate(file_path)
        patterns = template.get_patterns_from_template()

        template_info = {
            "id": file_id,
            "file_name": file_name,
            "file_path": file_path,
            "patterns": patterns,
            "info": info
        }

        config.data["templates"].append(template_info)
        config.save()

        return {"status": True, "data": template_info}

    return {"status": False}


@app.route('/get_template_info', methods=['GET'])
def get_template_info():
    try:
        template_id = request.args.get('id', type=int)
    except:
        return {"status": False, "msg": "Missing template id, use: /get_template_info?id=$ID"}

    template_info = config.get_template_info(template_id)

    if template_info:
        return {"status": True, "data": template_info}

    return {"status": False, "msg": "Template not found!"}


@app.route('/fill_template', methods=['GET'])
def fill_template():
    data = dict(request.args)

    try:
        template_id = request.args.get('id', type=int)
    except:
        return {"status": False, "msg": "Missing template id, use: /get_template_info?id=$ID"}

    template_info = config.get_template_info(template_id)
    template = DocTemplate(template_info["file_path"])
    path = template.fill_template(data)

    return send_file(path)


@app.route('/get_template_list', methods=['GET'])
def get_template_list():
    return {"status": True, "data": config.data["templates"]}


if __name__ == "__main__":
    app.run(debug=True)
