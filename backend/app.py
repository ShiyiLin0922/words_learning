from flask import Flask, session
from flask_cors import CORS
import logging
import subprocess
from db import get_db_connection
from routes.auth import setup_auth_routes
from routes.word import setup_word_routes
from routes.delete import setup_delete_routes
from routes.favorite import setup_favorite_routes
from routes.upload import upload_bp
from routes.miss import setup_miss_routes
from routes.library import setup_library_routes
from routes.practiceReport import practice_report_bp  # 导入 practice_report_bp
from routes.leaderBoard import leaderboard_bp  # 导入 leaderboard_bp 蓝图

app = Flask(__name__)
app.secret_key = '05ac92752149c2bf20dd41148f9e8918'

# Register blueprints
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(practice_report_bp, url_prefix='/api')  # 注册 practice_report_bp 蓝图
app.register_blueprint(leaderboard_bp, url_prefix='/api')  # 注册 leaderboard_bp 蓝图

# Enable CORS for the app
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# Start MySQL server
def start_mysql_server():
    mysql_safe_path = "/data/home/fanglab/linshiyi/software/mysql/bin/mysqld_safe"
    config_file_path = "/data/home/fanglab/linshiyi/software/mysql/my.cnf"
    
    try:
        process = subprocess.Popen(
            [mysql_safe_path, f"--defaults-file={config_file_path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("MySQL server is starting...")
        return process
    except Exception as e:
        print(f"Failed to start MySQL server: {e}")

mysql_process = start_mysql_server()

# Setup routes for other blueprints
setup_auth_routes(app)
setup_word_routes(app)
setup_delete_routes(app)
setup_favorite_routes(app)
setup_miss_routes(app)
setup_library_routes(app)

if __name__ == "__main__":
    try:
        app.run(port=8083, debug=True)
    finally:
        if mysql_process:
            mysql_process.terminate()
            print("MySQL server has been stopped.")

