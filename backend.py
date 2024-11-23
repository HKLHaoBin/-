import os , pyperclip , time
from flask import Flask, request, render_template, jsonify, send_from_directory , abort
from urllib.parse import unquote
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import subprocess
import socket  # 用于获取局域网 IP 地址
# 运行 ngrok 命令
def start_ngrok():
    try:
        # 使用 subprocess 启动 ngrok 并将其运行在后台
        process = subprocess.Popen(["ngrok", "http", "7000"])
        print("ngrok started.")
        return process
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        return None


# 获取当前设备的局域网 IP 地址
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 连接到一个外部的地址（并不会实际连接）
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception as e:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip


# 递归获取文件和文件夹结构
def get_files_structure(directory):
    items = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            # 如果是文件夹，递归调用以获取子文件夹内容
            items.append({
                'name': item,
                'is_folder': True,
                'children': get_files_structure(item_path)
            })
        else:
            # 如果是文件，添加到列表
            items.append({
                'name': item,
                'is_folder': False
            })
    return items


# 初始化 Flask 应用
app = Flask(__name__)
app.secret_key = 'your_random_secret_key'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app)

# 文件上传和下载的目录，设定为项目下的 'UPLOAD_FOLDER' 文件夹
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'UPLOAD_FOLDER')  # 使用当前工作目录下的 'UPLOAD_FOLDER' 文件夹
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传文件的目录是否存在，如果不存在则创建
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])  # 列出目录中的所有文件
        return render_template('backendpy.html', files=files)  # 在模板中显示文件列表
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)})
    
@app.route('/api/get_role', methods=['POST'])
def handle_role_request():
    global useu  # Declare the global variable to update it
    useu = request.json['action']
    pyperclip.copy(useu)
    print(f"已复制到剪贴板: {useu}")
    local_ip = get_local_ip()
    print(f" * Running on http://{local_ip}:7000/ (local network)")
    return jsonify({'useu': useu})  # Return JSON response

# 处理文件上传的路由
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    files = request.files.getlist('file')  # 获取多个文件
    uploaded_files = []

    for file in files:
        if file.filename == '':
            continue
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        uploaded_files.append(file.filename)

    socketio.emit('file_uploaded', {'filenames': uploaded_files})
    return jsonify({'message': 'Files uploaded successfully', 'filenames': uploaded_files}), 200


# 列出文件夹及其嵌套内容
@app.route('/files')
def list_files():
    try:
        files_structure = get_files_structure(app.config['UPLOAD_FOLDER'])
        return jsonify(files_structure)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)})
    
@app.route('/download/<path:file_path>')
def download_file(file_path):
    # 对路径进行解码
    file_path = unquote(file_path)

    # 构造完整的文件路径
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)

    # 检查文件是否存在
    if os.path.exists(full_path) and os.path.isfile(full_path):
        directory, filename = os.path.split(full_path)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        abort(404, description="File not found")

@app.route('/list_folder/<foldername>')
def list_folder(foldername):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], foldername)
    if not os.path.isdir(folder_path):
        return jsonify({'error': 'Folder not found'}), 404

    # 获取文件夹中的文件列表
    files = os.listdir(folder_path)
    files_list = [file for file in files if os.path.isfile(os.path.join(folder_path, file))]
    
    return jsonify({'files': files_list})

if __name__ == '__main__':
    # 获取局域网 IP 地址
    local_ip = get_local_ip()
    print(f" * Running on http://{local_ip}:7000/ (local network)")
    time.sleep(2)
    # 启动 ngrok 隧道
    #ngrok_process = start_ngrok()
    
    try:
        # 启动 Flask 应用
        socketio.run(app, host='0.0.0.0', port=7000, debug=True)
    except KeyboardInterrupt:
        print("Shutting down ngrok and Flask.")
    #    ngrok_process.terminate()  # 停止 ngrok 进程
