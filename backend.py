import os , pyperclip , time
from flask import Flask, request, render_template, jsonify, send_from_directory , abort
from urllib.parse import unquote
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import subprocess
import socket  # 用于获取局域网 IP 地址
import webbrowser
# 运行 ngrok 命令
# 定义一个函数 start_ngrok，用于启动 ngrok 服务
def start_ngrok():
    try:
        # 使用 subprocess 模块的 Popen 函数启动 ngrok 服务，将其运行在后台，监听 HTTP 端口 7000
        process = subprocess.Popen(["ngrok", "http", "7000"])
        # 打印 ngrok 服务已启动的消息
        print("ngrok started.")
        # 返回启动的进程对象，以便后续操作，如终止进程
        return process
    except Exception as e:
        # 若启动过程中出现异常，打印错误信息
        print(f"Error starting ngrok: {e}")
        # 返回 None 表示启动失败
        return None



# 获取当前设备的局域网 IP 地址
# 定义一个函数 get_local_ip，用于获取当前设备的局域网 IP 地址
def get_local_ip():
    # 创建一个基于 IPv4 和 UDP 的套接字对象 s
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 尝试将套接字连接到外部地址 8.8.8.8 的 80 端口，此操作不会实际发送数据，仅用于获取本地 IP 地址
        s.connect(("8.8.8.8", 80))
        # 获取套接字的本地 IP 地址
        local_ip = s.getsockname()[0]
    except Exception as e:
        # 如果连接出现异常，将本地 IP 地址设置为回环地址 127.0.0.1
        local_ip = "127.0.0.1"
    finally:
        # 关闭套接字，释放资源
        s.close()
    # 返回获取到的本地 IP 地址
    return local_ip



# 递归获取文件和文件夹结构
# 定义一个函数 get_files_structure，用于递归获取文件和文件夹结构
def get_files_structure(directory):
    # 初始化一个空列表 items，用于存储文件和文件夹信息
    items = []
    # 遍历目录中的每个项目
    for item in os.listdir(directory):
        # 构建项目的完整路径
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            # 如果是文件夹，递归调用 get_files_structure 函数以获取子文件夹内容
            items.append({
                'name': item,
                'is_folder': True,
                'children': get_files_structure(item_path)
            })
        else:
            # 如果是文件，将其添加到 items 列表中
            items.append({
                'name': item,
                'is_folder': False
            })
    # 返回存储文件和文件夹信息的列表
    return items

os.chdir(os.path.dirname(os.path.abspath(__file__)))
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
# 定义处理根路径请求的视图函数 index
def index():
    try:
        # 尝试列出 UPLOAD_FOLDER 目录中的所有文件
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        # 使用 render_template 函数将文件列表传递给 'backendpy.html' 模板并返回渲染结果
        return render_template('backendpy.html', files=files)
    except Exception as e:
        # 若出现异常，打印错误信息
        print(f"Error: {e}")
        # 将错误信息以 JSON 格式返回
        return jsonify({'error': str(e)})

    
@app.route('/api/get_role', methods=['POST'])
# 定义一个处理 POST 请求的路由函数，路由为 '/api/get_role'
def handle_role_request():
    # 声明 useu 为全局变量，以便在函数内部修改其值
    global useu
    # 从请求的 JSON 数据中获取 'action' 键对应的值，并赋值给 useu 变量
    useu = request.json['action']
    # 将 useu 的值复制到剪贴板
    pyperclip.copy(useu)
    # 打印已复制到剪贴板的信息
    print(f"已复制到剪贴板: {useu}")
    # 调用 get_local_ip 函数获取本地 IP 地址
    local_ip = get_local_ip()
    # 打印服务器运行的地址信息
    print(f" * Running on http://{local_ip}:7000/ (local network)")
    # 将包含 useu 的字典转换为 JSON 格式并返回
    return jsonify({'useu': useu})


# 处理文件上传的路由
@app.route('/upload', methods=['POST'])
# 处理文件上传的路由函数
def upload_file():
    # 检查请求中是否包含文件部分，如果没有则返回错误信息及 400 状态码
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    # 获取请求中的文件列表
    files = request.files.getlist('file')
    # 初始化一个空列表，用于存储已上传的文件名称
    uploaded_files = []

    # 遍历文件列表
    for file in files:
        # 如果文件名为空则跳过该文件
        if file.filename == '':
            continue
        # 构建文件的存储路径
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # 保存文件到指定路径
        file.save(file_path)
        # 将文件名添加到已上传文件列表中
        uploaded_files.append(file.filename)

    # 发送文件上传成功的消息，包含已上传文件的名称列表
    socketio.emit('file_uploaded', {'filenames': uploaded_files})
    # 返回文件上传成功的消息及 200 状态码
    return jsonify({'message': 'Files uploaded successfully', 'filenames': uploaded_files}), 200



# 列出文件夹及其嵌套内容
@app.route('/files')
# 定义处理 '/files' 路由请求的视图函数 list_files
def list_files():
    try:
        # 调用 get_files_structure 函数，传入 UPLOAD_FOLDER 的配置路径，获取文件和文件夹结构
        files_structure = get_files_structure(app.config['UPLOAD_FOLDER'])
        # 将文件和文件夹结构转换为 JSON 格式并返回
        return jsonify(files_structure)
    except Exception as e:
        # 若出现异常，打印错误信息
        print(f"Error: {e}")
        # 将错误信息以 JSON 格式返回
        return jsonify({'error': str(e)})

    
@app.route('/download/<path:file_path>')
def download_file(file_path):
    # 对文件路径进行 URL 解码，以处理可能包含的特殊字符
    file_path = unquote(file_path)

    # 构造文件的完整路径，将解码后的文件路径与上传文件夹的路径拼接
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)

    # 检查文件是否存在且为文件（而不是目录）
    if os.path.exists(full_path) and os.path.isfile(full_path):
        # 分离文件的目录和文件名
        directory, filename = os.path.split(full_path)
        # 从指定目录发送文件作为附件进行下载
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        # 如果文件不存在，返回 404 错误及相应描述
        abort(404, description="File not found")


@app.route('/list_folder/<foldername>')
# 定义一个名为 list_folder 的函数，用于列出指定文件夹中的文件列表
def list_folder(foldername):
    # 构建文件夹的完整路径，将 UPLOAD_FOLDER 与传入的 foldername 拼接
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], foldername)
    # 检查该文件夹是否存在，如果不存在则返回错误信息及 404 状态码
    if not os.path.isdir(folder_path):
        return jsonify({'error': 'Folder not found'}), 404

    # 获取文件夹中的文件列表
    files = os.listdir(folder_path)
    # 使用列表推导式筛选出文件列表中是文件的元素（排除文件夹）
    files_list = [file for file in files if os.path.isfile(os.path.join(folder_path, file))]
    
    # 将文件列表以 JSON 格式返回
    return jsonify({'files': files_list})


if __name__ == '__main__':
    # 获取局域网 IP 地址
    local_ip = get_local_ip()
    url=f"http://{local_ip}:7000/"
    webbrowser.open(url)
    time.sleep(2)
    # 启动 ngrok 隧道
    #ngrok_process = start_ngrok()
    
    try:
        # 启动 Flask 应用
        socketio.run(app, host='0.0.0.0', port=7000, debug=True)
    except KeyboardInterrupt:
        print("Shutting down ngrok and Flask.")
    #    ngrok_process.terminate()  # 停止 ngrok 进程
