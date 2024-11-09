# routes/delete.py
from flask import jsonify, request, session
import logging
from db import get_db_connection

def setup_delete_routes(app):
    @app.route("/api/delete", methods=["POST"])
    def delete():
        app.logger.debug('POST /api/delete called with data: %s', request.json)
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
            cursor.execute("INSERT INTO deletes (user_id, word_id) VALUES (%s, %s)", (user_id, word_id))
            conn.commit()
            cursor.close()
            conn.close()
            app.logger.info(f"Word deleted by user {user_id}: {word_id}")
            return jsonify({"status": "deleted"})
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/get_deletes", methods=["GET"])
    def get_deletes():
        app.logger.debug('GET /api/get_deletes called')
        try:
            user_id = session.get('user_id')  # 获取当前用户的ID
            if user_id is None:
                app.logger.warning("User not logged in.")
                return jsonify({"error": "User not logged in"}), 403

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT w.id, w.word, w.meaning, w.detail 
                FROM words w 
                JOIN deletes d ON w.id = d.word_id 
                WHERE d.user_id = %s
            """, (user_id,))
            delete_words = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify(delete_words), 200
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/undelete", methods=["POST"])
    def undelete():
        app.logger.debug('POST /api/undelete called with data: %s', request.json)
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
            cursor.execute("DELETE FROM deletes WHERE user_id = %s AND word_id = %s", (user_id, word_id))
            if cursor.rowcount == 0:
                app.logger.warning(f"No delete record found for word_id: {word_id}")
                return jsonify({"error": "Word not found in deletes"}), 404

            conn.commit()
            cursor.close()
            conn.close()
            app.logger.info(f"Word undeleted by user {user_id}: {word_id}")
            return jsonify({"status": "undeleted"})
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500
