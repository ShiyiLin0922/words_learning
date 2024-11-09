from flask import jsonify, request, session
import logging
from db import get_db_connection

def setup_missed_routes(app):
    # 获取错题
    @app.route("/api/get_missed_questions", methods=["GET"])
    def get_missed_questions():
        app.logger.debug('GET /api/get_missed_questions called')
        try:
            user_id = session.get('user_id')

            if user_id is None:
                app.logger.warning("User is not logged in or user_id is missing in session.")
                return jsonify({"error": "User not logged in"}), 401

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT words.id, words.word, words.meaning, words.detail 
                FROM words 
                JOIN missed_questions ON words.id = missed_questions.word_id 
                WHERE missed_questions.user_id = %s
            """, (user_id,))
            missed_words = cursor.fetchall()
            cursor.close()
            conn.close()

            if missed_words:
                return jsonify(missed_words), 200
            else:
                return jsonify({"error": "No missed questions found."}), 404

        except Exception as e:
            app.logger.error(f"Error in get_missed_questions: {str(e)}")
            return jsonify({"error": str(e)}), 500

    # 添加错题
    @app.route("/api/add_missed", methods=["POST"])
    def add_missed():
        app.logger.debug('POST /api/add_missed called with data: %s', request.json)
        try:
            data = request.json
            word_id = data.get("word_id")
            user_id = session.get('user_id')

            if word_id is None:
                app.logger.warning("Missing word_id in request data.")
                return jsonify({"error": "Missing word_id"}), 400
            if user_id is None:
                app.logger.warning("User not logged in.")
                return jsonify({"error": "User not logged in"}), 403

            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert the missed word into missed_questions if not already added
            cursor.execute("""
                INSERT INTO missed_questions (user_id, word_id)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM missed_questions WHERE user_id = %s AND word_id = %s
                )
            """, (user_id, word_id, user_id, word_id))

            conn.commit()
            cursor.close()
            conn.close()
            app.logger.info(f"Word added to missed questions by user {user_id}: {word_id}")
            return jsonify({"status": "added"}), 200

        except Exception as e:
            app.logger.error(f"Error in add_missed: {str(e)}")
            return jsonify({"error": str(e)}), 500

    # 删除错题
    @app.route("/api/del_missed", methods=["POST"])
    def del_missed():
        app.logger.debug('POST /api/del_missed called with data: %s', request.json)
        try:
            data = request.json
            word_id = data.get("word_id")
            user_id = session.get('user_id')

            if word_id is None:
                app.logger.warning("Missing word_id in request data.")
                return jsonify({"error": "Missing word_id"}), 400
            if user_id is None:
                app.logger.warning("User not logged in.")
                return jsonify({"error": "User not logged in"}), 403

            conn = get_db_connection()
            cursor = conn.cursor()

            # Delete the specific missed question for the user
            cursor.execute("DELETE FROM missed_questions WHERE user_id = %s AND word_id = %s", (user_id, word_id))
            if cursor.rowcount == 0:
                app.logger.warning(f"No missed question found for word_id: {word_id}")
                return jsonify({"error": "Word not found in missed questions"}), 404

            conn.commit()
            cursor.close()
            conn.close()
            app.logger.info(f"Missed question deleted by user {user_id}: {word_id}")
            return jsonify({"status": "deleted"}), 200

        except Exception as e:
            app.logger.error(f"Error in del_missed: {str(e)}")
            return jsonify({"error": str(e)}), 500

