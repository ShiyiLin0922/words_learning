import mysql.connector  # 导入 mysql.connector
from flask import Flask, session, jsonify, request
from db import get_db_connection  # Add this import

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define the setup_miss_routes function
def setup_miss_routes(app):
    @app.route("/api/miss", methods=["POST"])
    def miss():
        app.logger.debug('POST /api/miss called with data: %s', request.json)
        try:
            data = request.json
            word_id = data.get("word_id")
            user_id = session.get('user_id')  # Get the current user's ID from the session

            if word_id is None:
                app.logger.warning("Missing word_id in request data.")
                return jsonify({"error": "Missing word_id"}), 400
            if user_id is None:
                app.logger.warning("User not logged in.")
                return jsonify({"error": "User not logged in"}), 403

            conn = get_db_connection()
            cursor = conn.cursor()

            # 检查是否已存在记录
            cursor.execute("""
                SELECT 1 FROM missed_questions 
                WHERE user_id = %s AND word_id = %s
            """, (user_id, word_id))
            existing_record = cursor.fetchone()

            if existing_record:
                app.logger.info(f"Word already missed by user {user_id}: {word_id}")
                return jsonify({"status": "already missed"})

            # 如果没有重复记录，插入新记录
            cursor.execute("INSERT INTO missed_questions (user_id, word_id) VALUES (%s, %s)", (user_id, word_id))
            conn.commit()
            cursor.close()
            conn.close()
            app.logger.info(f"Word missed by user {user_id}: {word_id}")
            return jsonify({"status": "missed"})
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/get_misses", methods=["GET"])
    def get_misses():
        app.logger.debug('GET /api/get_misses called')
        try:
            user_id = session.get('user_id')  # 获取当前用户的ID
            if user_id is None:
                app.logger.warning("User not logged in.")
                return jsonify({"error": "User not logged in"}), 403

            conn = get_db_connection()  # Ensure this function is imported from db
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT w.id, w.word, w.meaning, w.detail 
                FROM words w 
                JOIN missed_questions d ON w.id = d.word_id
                WHERE d.user_id = %s
            """, (user_id,))
            miss_words = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify(miss_words), 200
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/unmiss", methods=["POST"])
    def unmiss():
        app.logger.debug('POST /api/unmiss called with data: %s', request.json)
        try:
            data = request.json
            word_id = data.get("word_id")
            user_id = session.get('user_id')  # Get the current user's ID from the session

            if word_id is None:
                app.logger.warning("Missing word_id in request data.")
                return jsonify({"error": "Missing word_id"}), 400
            if user_id is None:
                app.logger.warning("User not logged in.")
                return jsonify({"error": "User not logged in"}), 403

            app.logger.debug(f"Attempting to unmiss word_id: {word_id} for user_id: {user_id}")

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM missed_questions WHERE user_id = %s AND word_id = %s", (user_id, word_id))
            
            if cursor.rowcount == 0:
                app.logger.warning(f"No miss record found for word_id: {word_id}")
                return jsonify({"error": "Word not found in misses"}), 404

            conn.commit()
            cursor.close()
            conn.close()
            app.logger.info(f"Word unmissed by user {user_id}: {word_id}")
            return jsonify({"status": "unmissed"})
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": f"MySQL error: {str(err)}"}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

# Initialize app and pass it to the route setup function
if __name__ == "__main__":
    setup_miss_routes(app)  # Pass the app to the function
    app.run(debug=True)

