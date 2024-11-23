
# Flask File Transfer with Progress | 基于 Flask 的文件传输工具

A simple and user-friendly file transfer application built using Flask.  
这是一个基于 Flask 构建的简单且用户友好的文件传输工具。

---

## Features | 功能特点

- **File Upload with Progress | 上传进度显示**: 
  Users can upload files through a browser and see the upload progress and speed in real time.  
  用户可以通过浏览器上传文件，并实时查看上传进度和速度。

- **File Download | 文件下载**: 
  Easily download files directly from the browser.  
  可以直接通过浏览器轻松下载文件。

- **Responsive UI | 响应式界面**: 
  Optimized for both desktop and mobile devices with a clean and modern design.  
  界面设计简洁现代，支持桌面端和移动端。

- **Folder Structure Support | 支持文件夹结构**: 
  Organize files in nested folders, dynamically rendered in the UI.  
  支持嵌套文件夹结构，并在界面上动态展示。

- **Real-time Updates | 实时更新**: 
  File lists are updated in real time after uploads using Socket.IO.  
  通过 Socket.IO 实现文件列表实时更新。

---

## Demo | 演示

![PixPin_2024-11-24_00-24-50](https://github.com/user-attachments/assets/b4816b49-24ea-4ff5-8fb4-6a755bb69d3e)


---

## Requirements | 环境要求

- Python 3.7 or above | Python 3.7 或更高版本
- Flask
- Flask-SocketIO
- Flask-CORS

---

## Installation | 安装步骤

### 1. Clone the repository | 克隆仓库
```bash
git clone https://github.com/yourusername/Flask-File-Transfer-with-Progress.git
cd Flask-File-Transfer-with-Progress
```

### 2. Install dependencies | 安装依赖
```bash
pip install -r requirements.txt
```

### 3. Run the application | 启动应用
```bash
python backend.py
```

### 4. Access the application | 访问应用
Open your browser and navigate to `http://127.0.0.1:7001`.  
打开浏览器并访问 `http://127.0.0.1:7001`。

---

## Folder Structure | 文件结构

```
Flask-File-Transfer-with-Progress/
├── backend.py             # Main backend logic (Flask app) | 主后端逻辑（Flask 应用）
├── templates/
│   └── backendpy.html     # HTML template for the application | 应用的 HTML 模板
├── UPLOAD_FOLDER/         # Directory where uploaded files are stored | 上传文件存储目录
├── requirements.txt       # Python dependencies | Python 依赖列表
└── README.md              # Project documentation | 项目文档
```

---

## API Endpoints | API 接口

### 1. File Upload | 文件上传
- **Endpoint | 接口**: `/upload`
- **Method | 请求方式**: `POST`
- **Description | 描述**: Upload a file to the server.  
  将文件上传到服务器。
- **Response | 响应**: 
    ```json
    {
      "message": "File uploaded successfully",
      "filename": "example.txt"
    }
    ```

### 2. File List | 文件列表
- **Endpoint | 接口**: `/files`
- **Method | 请求方式**: `GET`
- **Description | 描述**: Retrieve the list of files and folders.  
  获取文件和文件夹列表。

### 3. File Download | 文件下载
- **Endpoint | 接口**: `/download/<file_path>`
- **Method | 请求方式**: `GET`
- **Description | 描述**: Download a specific file.  
  下载指定文件。

---

## Screenshots | 截图

### 1. File Upload Page | 文件上传界面

![PixPin_2024-11-24_00-21-13](https://github.com/user-attachments/assets/c15377e3-d0f3-4588-b4ea-d5f4051d587d)


### 2. File List | 文件列表

![PixPin_2024-11-24_00-22-39](https://github.com/user-attachments/assets/d5b05a5f-c621-4064-875e-036a3abdabd4)


---

## Contributing | 贡献

Contributions are welcome! Feel free to open an issue or submit a pull request.  
欢迎贡献代码或建议！您可以提交问题或创建拉取请求。

---

## License | 许可协议

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.  
此项目基于 MIT 协议授权 - 详情请查看 [LICENSE](LICENSE) 文件。

