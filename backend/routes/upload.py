#routes/upload.py
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import csv
from db import get_db_connection  # 假设你有一个db.py来管理数据库连接

# 配置上传的文件夹和允许的文件类型
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

# 创建 Blueprint
upload_bp = Blueprint('upload', __name__)

# 检查文件格式是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 上传文件接口
@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 确保上传文件夹存在
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(filepath)

        # 在保存后处理文件内容
        return jsonify({"message": "File uploaded successfully", "filepath": filepath}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400

# 处理上传文件内容并存入数据库
@upload_bp.route('/process_upload', methods=['POST'])
def process_upload():
    user_id = session.get('user_id')
    filepath = request.json.get("filepath")

    if not user_id:
        return jsonify({"error": "User not logged in"}), 403
    if not filepath:
        return jsonify({"error": "Filepath missing"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # 处理 CSV 文件中的数据，假设每行有单词、释义和可选的详细信息
                word, meaning, detail = row[0], row[1], row[2] if len(row) > 2 else None
                cursor.execute("""
                    INSERT INTO user_words (user_id, word, meaning, detail) 
                    VALUES (%s, %s, %s, %s)
                """, (user_id, word, meaning, detail))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Words added to user-specific question bank"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

