from flask import jsonify, request, session
import logging
from db import get_db_connection

def setup_library_routes(app):
    @app.route("/api/library", methods=["POST"])
    def library():
        app.logger.debug('POST /api/library called with data: %s', request.json)
        try:
            data = request.json
            word = data.get("word")
            meaning = data.get("meaning")
            detail = data.get("detail", "")
            user_id = session.get('user_id')

            if not word or not meaning:
                app.logger.warning("Missing word or meaning in request data.")
                return jsonify({"error": "Missing word or meaning"}), 400
            if user_id is None:
                app.logger.warning("User not logged in.")
                return jsonify({"error": "User not logged in"}), 403

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Insert the word into user_words with user-specific data
                    cursor.execute("""
                        INSERT INTO user_words (user_id, word, meaning, detail) 
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, word, meaning, detail))
                    conn.commit()

            app.logger.info(f"Word added to library by user {user_id}: {word}")
            return jsonify({"status": "library"}), 201
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/get_libraries", methods=["GET"])
    def get_libraries():
        app.logger.debug('GET /api/get_libraries called')
        try:
            user_id = session.get('user_id')
            if user_id is None:
                app.logger.warning("User not logged in.")
                return jsonify({"error": "User not logged in"}), 403

            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    # Query directly from user_words for the logged-in user
                    cursor.execute("""
                        SELECT id, word, meaning, detail 
                        FROM user_words 
                        WHERE user_id = %s
                    """, (user_id,))
                    library_words = cursor.fetchall()

            if not library_words:
                app.logger.info(f"No library words found for user {user_id}")
                return jsonify({"message": "No words found in library"}), 404

            return jsonify(library_words), 200
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/unlibrary", methods=["POST"])
    def unlibrary():
        app.logger.debug('POST /api/unlibrary called with data: %s', request.json)
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

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Delete the word from user_words for the specific user and word_id
                    cursor.execute("""
                        DELETE FROM user_words 
                        WHERE user_id = %s AND id = %s
                    """, (user_id, word_id))
                    conn.commit()

                    if cursor.rowcount == 0:
                        app.logger.warning(f"No library entry found for word_id: {word_id}")
                        return jsonify({"error": "Word not found in libraries"}), 404

            app.logger.info(f"Word removed from library by user {user_id}: {word_id}")
            return jsonify({"status": "unlibrary"}), 200
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

