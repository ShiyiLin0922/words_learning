from flask import Blueprint, jsonify, request, session
import datetime
from datetime import timezone

# Create a blueprint for session-related routes
end_session_bp = Blueprint('end_session', __name__)

# Check if the user is logged in
def check_login():
    return 'username' in session

# Start a new practice session
@end_session_bp.route("/start_session", methods=["POST"])
def start_session():
    if not check_login():
        return jsonify({"error": "User not logged in"}), 403
    
    data = request.json
    total_questions = data.get('totalQuestions', 0)

    session['total_questions'] = total_questions
    session['start_time'] = datetime.datetime.now(timezone.utc)  # Make start_time timezone-aware
    session['questions_answered'] = 0
    session['correct_answers'] = 0
    return jsonify({"status": "session started"}), 200

# End the current practice session
@end_session_bp.route("/end_session", methods=["POST"])
def end_session():
    if not check_login():
        return jsonify({"error": "User not logged in"}), 403
    
    if 'start_time' not in session:
        return jsonify({"error": "Session not started"}), 400

    end_time = datetime.datetime.now(timezone.utc)  # Make end_time timezone-aware
    session_duration = (end_time - session['start_time']).total_seconds()  # Duration in seconds
    questions_answered = session.get('questions_answered', 0)
    correct_answers = session.get('correct_answers', 0)
    accuracy = (correct_answers / questions_answered) * 100 if questions_answered > 0 else 0

    # Clear session data after ending the session
    session.pop('start_time', None)
    session.pop('questions_answered', None)
    session.pop('correct_answers', None)

    return jsonify({
        "duration": session_duration,
        "accuracy": accuracy,
        "questions_answered": questions_answered,
        "correct_answers": correct_answers
    }), 200

