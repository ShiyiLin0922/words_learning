# routes/favorite.py
from flask import jsonify, request, session
import logging
from db import get_db_connection

def setup_favorite_routes(app):
    @app.route("/api/favorite", methods=["POST"])
    def favorite():
        app.logger.debug('POST /api/favorite called with data: %s', request.json)
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
            cursor.execute("INSERT INTO favorites (user_id, word_id) VALUES (%s, %s)", (user_id, word_id))
            conn.commit()
            cursor.close()
            conn.close()
            app.logger.info(f"Word favorited by user {user_id}: {word_id}")
            return jsonify({"status": "favorited"})
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/get_favorites", methods=["GET"])
    def get_favorites():
        app.logger.debug('GET /api/get_favorites called')
        try:
            user_id = session.get('user_id')  # Get the current user's ID from the session
            if user_id is None:
                app.logger.warning("User not logged in.")
                return jsonify({"error": "User not logged in"}), 403

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT w.id, w.word, w.meaning, w.detail 
                FROM words w 
                JOIN favorites f ON w.id = f.word_id 
                WHERE f.user_id = %s
            """, (user_id,))
            favorite_words = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify(favorite_words), 200
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/unfavorite", methods=["POST"])
    def unfavorite():
        app.logger.debug('POST /api/unfavorite called with data: %s', request.json)
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
            cursor.execute("DELETE FROM favorites WHERE user_id = %s AND word_id = %s", (user_id, word_id))
            if cursor.rowcount == 0:
                app.logger.warning(f"No favorite found for word_id: {word_id}")
                return jsonify({"error": "Word not found in favorites"}), 404

            conn.commit()
            cursor.close()
            conn.close()
            app.logger.info(f"Word unfavorited by user {user_id}: {word_id}")
            return jsonify({"status": "unfavorited"})
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500
