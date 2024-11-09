# 后端说明文档
✍️：馒头<br/>
🏠：求是潮产研

## 1. auth.py - 用户认证相关路由
### 1.1 POST /api/login
- 功能：处理用户登录请求。通过传入的用户名和密码验证用户身份，并在登录成功后更新用户的登录天数和最后登录日期。
- 请求参数：
  - username：用户名（字符串）
  - password：密码（字符串）
- 返回值：
  - 登录成功：{"message": "Login successful", "username": "用户名"}
  - 登录失败：{"error": "Invalid username or password"}
  - 参数缺失：{"error": "Missing username or password"}
  
### 1.2 GET /api/check_login
- 功能：检查当前用户是否已登录，并返回登录状态以及用户的登录天数。
- 返回值：
  - 已登录：{"logged_in": true, "username": "用户名", "login_days": 登录天数}
  - 未登录：{"logged_in": false}

## 2. delete.py - 删除相关路由

### 2.1 POST /api/delete
- 功能：将指定单词添加到删除记录中，以便用户查看已删除的单词。
- 请求参数：
  - word_id：单词 ID（整数）
- 返回值：
  - 删除成功：{"status": "deleted"}
  - 参数缺失：{"error": "Missing word_id"}
  - 未登录：{"error": "User not logged in"}

### 2.2 GET /api/get_deletes
- 功能：获取当前用户已删除的单词列表。
- 返回值：
  - 返回单词列表：[{"id": 单词ID, "word": 单词, "meaning": 意思, "detail": 详情}, ...]
  - 未登录：{"error": "User not logged in"}

### 2.3 POST /api/undelete
- 功能：将单词从删除记录中恢复，取消删除。
- 请求参数：
  - word_id：单词 ID（整数）
- 返回值：
  - 恢复成功：{"status": "undeleted"}
  - 参数缺失：{"error": "Missing word_id"}
  - 单词未在删除记录中：{"error": "Word not found in deletes"}
  - 未登录：{"error": "User not logged in"}

## 3. favorite.py - 收藏相关路由

### 3.1 POST /api/favorite
- 功能：将指定单词添加到收藏列表中。
- 请求参数：
  - word_id：单词 ID（整数）
- 返回值：
  - 收藏成功：{"status": "favorited"}
  - 参数缺失：{"error": "Missing word_id"}
  - 未登录：{"error": "User not logged in"}

### 3.2 GET /api/get_favorites
- 功能：获取当前用户收藏的单词列表。
- 返回值：
  - 返回单词列表：[{"id": 单词ID, "word": 单词, "meaning": 意思, "detail": 详情}, ...]
  - 未登录：{"error": "User not logged in"}

### 3.3 POST /api/unfavorite
- 功能：将指定单词从收藏列表中移除。
- 请求参数：
  - word_id：单词 ID（整数）
- 返回值：
  - 取消收藏成功：{"status": "unfavorited"}
  - 参数缺失：{"error": "Missing word_id"}
  - 单词未在收藏列表中：{"error": "Word not found in favorites"}
  - 未登录：{"error": "User not logged in"}


## 4. missed.py - 错题相关路由

### 4.1 GET /api/get_missed_questions
- 功能：获取当前用户的错题列表。
- 返回值：
  - 返回错题列表：[{"id": 单词ID, "word": 单词, "meaning": 意思, "detail": 详情}, ...]
  - 未登录：{"error": "User not logged in"}
  - 无错题：{"error": "No missed questions found."}

### 4.2 POST /api/add_missed
- 功能：将指定单词添加到错题记录中。
- 请求参数：
  - word_id：单词 ID（整数）
- 返回值：
  - 添加成功：{"status": "added"}
  - 参数缺失：{"error": "Missing word_id"}
  - 未登录：{"error": "User not logged in"}



## 5. leaderboard.py - 排行榜相关路由

### 5.1 GET /login_days
- 功能：获取用户登录天数的排行榜。
- 返回值：
  - 返回排行榜列表：[{"username": 用户名, "login_days": 登录天数}, ...]

### 5.2 GET /words_learned
- 功能：获取用户学习单词数量的排行榜。
- 返回值：
  - 返回排行榜列表：[{"username": 用户名, "words_learned": 学习单词数量}, ...]

## 6. library.py - 用户词库相关路由

### 6.1 POST /api/library
- 功能：将单词添加到用户的个人词库中。
- 请求参数：
  - word：单词（字符串）
  - meaning：单词意思（字符串）
  - detail：单词详细信息（字符串，可选）
- 返回值：
  - 添加成功：{"status": "library"}
  - 参数缺失：{"error": "Missing word or meaning"}
  - 未登录：{"error": "User not logged in"}

### 6.2 GET /api/get_libraries
- 功能：获取当前用户个人词库中的单词列表。
- 返回值：
  - 返回单词列表：[{"id": 单词ID, "word": 单词, "meaning": 意思, "detail": 详情}, ...]
  - 未登录：{"error": "User not logged in"}
  - 无单词：{"message": "No words found in library"}

### 6.3 POST /api/unlibrary
- 功能：将单词从用户的个人词库中删除。
- 请求参数：
  - word_id：单词 ID（整数）
- 返回值：
  - 删除成功：{"status": "unlibrary"}
  - 参数缺失：{"error": "Missing word_id"}
  - 单词未在词库中：{"error": "Word not found in libraries"}
  - 未登录：{"error": "User not logged in"}

## 7. practiceReport.py - 练习报告相关路由

### 7.1 POST /api/save_report
- 功能：保存用户的练习报告。
- 请求参数：
  - total_questions：总题目数量（整数）
  - correct_answers：正确答案数量（整数）
  - duration：练习时长（秒，整数）
- 返回值：
  - 保存成功：{"message": "Report saved successfully"}
  - 参数缺失：{"error": "Incomplete data"}
  - 未登录：{"error": "User not logged in"}

## 8. upload.py - 文件上传相关路由

### 8.1 POST /upload
- 功能：上传文件到服务器。
- 请求参数：
  - file：上传的文件（文件对象）
- 返回值：
  - 上传成功：{"message": "File uploaded successfully", "filepath": 文件路径}
  - 无文件：{"error": "No file part"}
  - 文件名缺失：{"error": "No selected file"}
  - 文件类型不允许：{"error": "File type not allowed"}

### 8.2 POST /process_upload
- 功能：处理上传的文件内容并将其存入数据库。
- 请求参数：
  - filepath：文件路径（字符串）
- 返回值：
  - 处理成功：{"message": "Words added to user-specific question bank"}
  - 文件路径缺失：{"error": "Filepath missing"}
  - 未登录：{"error": "User not logged in"}

## 9. word.py - 单词相关路由

### 9.1 GET /api/get_word
- 功能：获取一个随机单词。
- 请求参数：
  - pool：单词池类型（字符串，可选，默认为'all'，可选值：'favorites', 'library'）
- 返回值：
  - 返回单词：{"id": 单词ID, "word": 单词, "meaning": 意思, "detail": 详情}
  - 未登录：{"error": "User not logged in"}
  - 无单词：{"error": "No words found"}

### 9.2 GET /api/get_options
- 功能：获取单词的选项列表。
- 返回值：
  - 返回选项列表：[选项1, 选项2, 选项3]
  - 无单词：{"error": "No words available."}
  - 选项不足：{"error": "Not enough options available."}

### 9.3 POST /api/check_answer
- 功能：检查用户答题结果并更新学习统计。
- 请求参数：
  - word_id：单词 ID（整数）
  - user_answer：用户答案（字符串）
  - correct_answer：正确答案（字符串）
- 返回值：
  - 答案正确：{"message": "Correct answer, words_learned updated"}
  - 答案错误：{"message": "Incorrect answer"}
  - 参数缺失：{"error": "Invalid data"}
  - 未登录：{"error": "User not logged in"}

