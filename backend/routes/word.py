from flask import jsonify, request, session
import logging
import random
import mysql.connector
from db import get_db_connection

def setup_word_routes(app):
    @app.route("/api/get_word", methods=["GET"])
    def get_word():
        app.logger.debug('GET /api/get_word called')
        try:
            pool = request.args.get('pool', 'all')  # Determine which pool of words to fetch
            user_id = session.get('user_id')

            if user_id is None:
                app.logger.warning("User is not logged in or user_id is missing in session.")
                return jsonify({"error": "User not logged in"}), 401

            app.logger.info(f"User {user_id} is logged in. Proceeding with fetching words.")

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            if pool == 'favorites':
                # Query user's favorite words
                cursor.execute("""
                    SELECT id, word, meaning, detail 
                    FROM words 
                    WHERE id IN (
                        SELECT word_id FROM favorites WHERE user_id = %s
                    )
                    ORDER BY RAND() 
                    LIMIT 1
                """, (user_id,))
            elif pool == 'library':
                # Query words from user's personal library (user_words table)
                cursor.execute("""
                    SELECT id, word, meaning, detail 
                    FROM user_words 
                    WHERE user_id = %s
                    ORDER BY RAND() 
                    LIMIT 1
                """, (user_id,))
            else:
                # Query all words, excluding deleted ones
                cursor.execute("""
                    SELECT id, word, meaning, detail 
                    FROM words 
                    WHERE id NOT IN (
                        SELECT word_id FROM deletes WHERE user_id = %s
                    )
                    ORDER BY RAND() 
                    LIMIT 1
                """, (user_id,))
            
            word = cursor.fetchone()
            cursor.close()
            conn.close()

            if word:
                app.logger.info(f"Word fetched: {word}")
                return jsonify(word)
            else:
                app.logger.warning("No words found.")
                return jsonify({"error": "No words found"}), 404

        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500


    @app.route("/api/get_options")
    def get_options():
        app.logger.debug('GET /api/get_options called')
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT id, meaning FROM words")
            word_learning = cursor.fetchall()
            cursor.close()

            if not word_learning:
                app.logger.error("No words found in the database.")
                return jsonify({"error": "No words available."}), 404

            word_id = random.choice([word['id'] for word in word_learning])
            correct_answer = next(word['meaning'] for word in word_learning if word['id'] == word_id)

            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT meaning FROM words WHERE id != %s ORDER BY RAND() LIMIT 2", (word_id,))
            error_options = [row['meaning'] for row in cursor.fetchall()]
            cursor.close()
            conn.close()

            if len(error_options) < 2:
                app.logger.error("Not enough error options found in the database.")
                return jsonify({"error": "Not enough options available."}), 500

            options = error_options + [correct_answer]
            random.shuffle(options)

            app.logger.debug(f"Options: {options}, Count: {len(options)}")
            return jsonify(options)
        
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL error: {str(err)}")
            return jsonify({"error": str(err)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    # 处理答题结果
    @app.route('/api/check_answer', methods=['POST'])
    def check_answer():
        # 获取请求中的数据
        data = request.json
        word_id = data.get('word_id')
        user_answer = data.get('user_answer')
        correct_answer = data.get('correct_answer')
        
        if not word_id or user_answer is None or correct_answer is None:
            return jsonify({'error': 'Invalid data'}), 400
        
        # 获取当前用户的ID
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401
        
        # 比较答案是否正确
        is_correct = (user_answer == correct_answer)
        
        # 如果答对了，更新 words_learned 计数
        if is_correct:
            try:
                connection = get_db_connection()
                cursor = connection.cursor()
    
                # 更新 user_stats 表，增加 words_learned 数量
                cursor.execute("""
                    UPDATE user_stats
                    SET words_learned = words_learned + 1
                    WHERE user_id = %s
                """, (user_id,))
                
                connection.commit()
                cursor.close()
                connection.close()
    
                return jsonify({'message': 'Correct answer, words_learned updated'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'message': 'Incorrect answer'}), 200
