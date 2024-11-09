# routes/practiceReport.py

from flask import Blueprint, jsonify, request, session
import logging
from db import get_db_connection

practice_report_bp = Blueprint('practice_report', __name__)

@practice_report_bp.route("/api/save_report", methods=["POST"])
def save_report():
    logging.debug("POST /api/save_report called with data: %s", request.json)
    try:
        # Fetch the report data
        data = request.json
        total_questions = data.get("total_questions")
        correct_answers = data.get("correct_answers")
        duration = data.get("duration")  # in seconds

        user_id = session.get("user_id")
        if user_id is None:
            logging.warning("User not logged in or user_id missing.")
            return jsonify({"error": "User not logged in"}), 401

        # Data validation
        if total_questions is None or correct_answers is None or duration is None:
            logging.warning("Incomplete data.")
            return jsonify({"error": "Incomplete data"}), 400

        # Insert report into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO practice_reports (user_id, total_questions, correct_answers, duration)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, total_questions, correct_answers, duration)
        )
        conn.commit()
        cursor.close()
        conn.close()

        logging.info(f"Report saved for user {user_id} with {correct_answers}/{total_questions} correct in {duration}s")
        return jsonify({"message": "Report saved successfully"}), 201

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500

