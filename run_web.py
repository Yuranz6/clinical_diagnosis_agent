#!/usr/bin/env python3
"""
启动 Web 应用的便捷脚本
"""
import sys
import os

# 检查依赖
try:
    import flask
except ImportError:
    print("错误: 未安装 Flask")
    print("请运行: pip install flask flask-cors")
    sys.exit(1)

# 检查 API Key
from config import GOOGLE_API_KEY

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
    print("错误: 未设置有效的 GOOGLE_API_KEY")
    print("请在 .env 文件中设置您的 Google API Key")
    sys.exit(1)

# 启动应用
if __name__ == '__main__':
    import os
    import sys
    
    # 确保在正确的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    from app import app
    
    print("=" * 60)
    print("EHR Agent Web 应用")
    print("=" * 60)
    print(f"工作目录: {os.getcwd()}")
    print(f"模板文件夹: {app.template_folder}")
    print(f"静态文件夹: {app.static_folder}")
    print("=" * 60)
    
    # 使用 app.py 中的启动逻辑（包含端口自动检测）
    # 这里直接导入并运行
    import socket
    
    def find_free_port(start_port=5000, max_attempts=10):
        """查找可用端口"""
        # 跳过已知被占用的端口（Datadog 使用 5000, 5001, 5002）
        skip_ports = [5000, 5001, 5002]
        
        for port in range(start_port, start_port + max_attempts):
            if port in skip_ports:
                continue
            try:
                # 先尝试连接，检查是否真的可用
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(0.1)
                result = test_sock.connect_ex(('localhost', port))
                test_sock.close()
                
                if result == 0:
                    # 端口已被占用，跳过
                    continue
                
                # 尝试绑定
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', port))
                sock.close()
                return port
            except (OSError, socket.error):
                continue
        return None
    
    port = find_free_port(5000)
    
    if port is None:
        print(f"\n❌ 错误: 无法找到可用端口 (5000-5009)")
        sys.exit(1)
    
    if port != 5000:
        print(f"\n⚠️  端口 5000 被占用，使用端口 {port}")
    
    print(f"\n🌐 访问地址: http://localhost:{port}")
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

