from flask import Blueprint, jsonify
from db import get_db_connection

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/login_days', methods=['GET'])
def leaderboard_login_days():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username, us.login_days 
        FROM user_stats us
        JOIN users u ON us.user_id = u.id
        ORDER BY us.login_days DESC, us.user_id ASC
    """)
    login_days_ranking = cursor.fetchall()
    conn.close()

    return jsonify(login_days_ranking)

@leaderboard_bp.route('/words_learned', methods=['GET'])
def leaderboard_words_learned():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username, us.words_learned 
        FROM user_stats us
        JOIN users u ON us.user_id = u.id
        ORDER BY us.words_learned DESC, us.user_id ASC
    """)
    words_learned_ranking = cursor.fetchall()
    conn.close()

    return jsonify(words_learned_ranking)

