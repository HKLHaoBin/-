from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pyperclip
import os

# 初始化 Flask 应用
app = Flask(__name__, static_url_path='')
app.secret_key = 'your_random_secret_key'
CORS(app)
socketio = SocketIO(app)  # 添加 SocketIO 支持

# 文件上传的目录，设定为项目下的 'uploads' 文件夹
UPLOAD_FOLDER = 'UPLOAD_FOLDER'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传文件的目录是否存在，如果不存在则创建
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 确保上传文件的目录是否存在
folder_exists = os.path.exists(UPLOAD_FOLDER)

useu = ""

@app.route('/')
def index():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER']) if folder_exists else []
        return render_template('backendpy.html', useu=useu, files=files)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/get_role', methods=['POST'])
def handle_role_request():
    global useu  # Declare the global variable to update it
    useu = request.json['action']
    pyperclip.copy(useu)
    print(f"已复制到剪贴板: {useu}")
    return jsonify({'useu': useu})  # Return JSON response

# 处理文件上传的路由
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        # 动态检查文件夹是否存在
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            return jsonify({'message': 'Upload folder does not exist'}), 500
        
        # 保存上传的文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # 通知所有客户端文件上传成功，广播给所有连接的客户端
        socketio.emit('file_uploaded', {'filename': file.filename})
        print(f"文件已保存: {file.filename}")
        
        # 返回文件路径和文件名
        return jsonify({'message': 'File uploaded successfully', 'filename': file.filename}), 200

# 如果上传文件夹存在，提供下载和列出文件服务
if folder_exists:
    @app.route('/files')
    def list_files():
        try:
            files = os.listdir(app.config['UPLOAD_FOLDER'])
            return jsonify(files)
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': str(e)})

    @app.route('/download/<filename>')
    def download_file(filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"文件 {filename} 未找到")
            return jsonify({'message': 'File not found'}), 404
        
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=7000, debug=True)
