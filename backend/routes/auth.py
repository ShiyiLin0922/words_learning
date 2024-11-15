from flask import jsonify, request, session
import logging
import mysql.connector
from db import get_db_connection
from datetime import datetime

def setup_auth_routes(app):
    @app.route("/api/login", methods=["POST"])
    def login():
        logging.debug('POST /api/login called')
        try:
            data = request.json
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                logging.warning("Missing username or password in request data.")
                return jsonify({"error": "Missing username or password"}), 400

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and user['password'] == password:
                session['user_id'] = user['id']
                session['username'] = username
                logging.info(f"User {username} logged in successfully.")

                current_date = datetime.now().date()
                cursor.execute("SELECT last_login_date FROM user_stats WHERE user_id = %s", (user['id'],))
                stats = cursor.fetchone()

                if stats:
                    last_login_date = stats['last_login_date']
                    if last_login_date != current_date:
                        cursor.execute(
                            "UPDATE user_stats SET login_days = login_days + 1, last_login_date = %s WHERE user_id = %s",
                            (current_date, user['id'])
                        )
                else:
                    cursor.execute(
                        "INSERT INTO user_stats (user_id, login_days, words_learned, last_login_date) VALUES (%s, 1, 0, %s)",
                        (user['id'], current_date)
                    )

                conn.commit()
                cursor.close()
                conn.close()

                return jsonify({"message": "Login successful", "username": username}), 200
            else:
                logging.warning("Invalid username or password.")
                return jsonify({"error": "Invalid username or password"}), 401

        except mysql.connector.Error as err:
            logging.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/check_login", methods=["GET"])
    def check_login():
        """Check if a user is logged in by checking the session."""
        if 'user_id' in session:
            logging.info(f"User {session['username']} is currently logged in.")
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT login_days FROM user_stats WHERE user_id = %s", (session['user_id'],))
            stats = cursor.fetchone()
            login_days = stats['login_days'] if stats else 0
            cursor.close()
            conn.close()
            return jsonify({"logged_in": True, "username": session['username'], "login_days": login_days}), 200
        else:
            logging.info("No user is currently logged in.")
            return jsonify({"logged_in": False}), 200

    @app.route("/api/logout", methods=["POST"])
    def logout():
        """Clear the session to log out the user."""
        session.clear()
        logging.info("User logged out successfully.")
        return jsonify({"message": "Logout successful"}), 200

    @app.route("/api/register", methods=["POST"])
    def register():
        logging.debug('POST /api/register called')
        try:
            data = request.json
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            
            if not username or not email or not password:
                logging.warning("Missing username, email, or password in request data.")
                return jsonify({"error": "Missing username, email, or password"}), 400

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                logging.warning("Username or email already exists.")
                return jsonify({"error": "Username or email already exists"}), 409

            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            conn.commit()

            logging.info(f"New user registered: {username}")
            cursor.close()
            conn.close()

            return jsonify({"message": "User registered successfully"}), 201
        except mysql.connector.Error as err:
            logging.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500
