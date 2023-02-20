import os

from random import randint
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename

from doc import DocTemplate
from config import Config
from database import Database

from flask_cors import CORS

import json

config = Config()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "UPLOADED_FILES"
CORS(app)


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
        return {
            "status": False,
            "msg": "Missing template id, use: /get_template_info?id=$ID",
        }

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
        return {
            "status": False,
            "msg": "Missing template id, use: /get_template_info?id=$ID",
        }

    template_info = config.get_template_info(template_id)
    template = DocTemplate(template_info["file_path"])
    path = template.fill_template(data)

    return send_file(path)


@app.route('/get_template_list', methods=['GET'])
def get_template_list():
    return {"status": True, "data": config.data["templates"]}


@app.route('/delete_template', methods=['GET'])
def delete_template():
    try:
        template_id = request.args.get('id', type=int)
    except:
        return {
            "status": False,
            "msg": "Missing template id, use: /delete_template?id=$ID",
        }

    config.data["templates"] = list(
        filter(
            function=lambda i: i["id"] != template_id,
            iterable=config.data["templates"],
        )
    )
    config.save()

    return {"status": True}


@app.route('/create_database', methods=['GET'])
def create_database():
    database_name = request.args.get("name")

    if database_name is None:
        return {
            "status": False,
            "msg": "Missing 'name', use: /create_database?name=$NAME",
        }

    Database.create_database(database_name)
    return {"status": True}


@app.route('/delete_database', methods=['GET'])
def delete_database():
    db_name = request.args.get("db_name")

    if db_name is None:
        return {
            "status": False,
            "msg": "Missing 'db_name', use: /delete_database?db_name=$DB_NAME",
        }

    Database.delete_database(db_name)
    return {"status": True}


@app.route('/create_table', methods=['GET'])
def create_table():
    db_name = request.args.get("db_name")
    if db_name not in Database.get_databases():
        return {
            "status": False,
            "msg": f"Database '{db_name}' not found!",
        }

    table_name = request.args.get("table_name")
    columns = request.args.getlist("columns")

    if all([db_name, table_name, columns]):
        db = Database(db_name)
        db.create_table(table_name, columns)
        return {"status": True}

    return {
        "status": False,
        "msg": "Missing args",
    }


@app.route('/delete_table', methods=['GET'])
def delete_table():
    db_name = request.args.get("db_name")
    if db_name not in Database.get_databases():
        return {
            "status": False,
            "msg": f"Database '{db_name}' not found!",
        }

    table_name = request.args.get("table_name")

    if all([db_name, table_name]):
        db = Database(db_name)
        db.drop_table(table_name)
        return {"status": True}

    return {
        "status": False,
        "msg": "Missing args",
    }


@app.route('/add_row_to_table', methods=["GET"])
def add_row_to_table():

    db_name = request.args.get("db_name")
    if db_name not in Database.get_databases():
        return {
            "status": False,
            "msg": f"Database '{db_name}' not found!",
        }

    table_name = request.args.get("table_name")
    data = json.loads(request.args.get("data"))

    if all([db_name, table_name, data]):
        db = Database(db_name)
        db.add_row_to_table(table_name, data)
        return {"status": True}

    return {
        "status": False,
        "msg": "Missing args",
    }


@app.route('/delete_row_from_table', methods=['GET'])
def delete_row_from_table():
    db_name = request.args.get("db_name")
    if db_name not in Database.get_databases():
        return {
            "status": False,
            "msg": f"Database '{db_name}' not found!",
        }

    table_name = request.args.get("table_name")
    _id = request.args.get("id")

    if all([db_name, table_name, _id]):
        db = Database(db_name)
        db.delete_row_from_table(table_name, _id)
        return {"status": True}

    return {
        "status": False,
        "msg": "Missing args",
    }


@app.route('/get_databases', methods=['GET'])
def get_databases():
    return {"status": True, "data": Database.get_databases()}


@app.route('/get_rows_from_table', methods=['GET'])
def get_rows_from_table():
    db_name = request.args.get("db_name")
    if db_name not in Database.get_databases():
        return {
            "status": False,
            "msg": f"Database '{db_name}' not found!",
        }

    table_name = request.args.get("table_name")
    db = Database(db_name)
    return {"status": True, "data": db.get_rows_from_table(table_name)}


@app.route('/get_tables', methods=['GET'])
def get_tables():
    db_name = request.args.get("db_name")
    if db_name not in Database.get_databases():
        return {
            "status": False,
            "msg": f"Database '{db_name}' not found!",
        }

    db = Database(db_name)
    return {"status": True, "data": db.get_tables()}


@app.route('/get_info_columns_of_table', methods=['GET'])
def get_info_columns_of_table():
    db_name = request.args.get("db_name")
    if db_name not in Database.get_databases():
        return {
            "status": False,
            "msg": f"Database '{db_name}' not found!",
        }

    table_name = request.args.get("table_name")
    db = Database(db_name)
    return {"status": True, "data": db.get_info_columns_of_table(table_name)}


if __name__ == "__main__":
    app.run(port=3000,debug=True)
