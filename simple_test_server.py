#!/usr/bin/env python3
"""
简单的测试服务器 - 用于诊断问题
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <html>
    <head><title>测试服务器</title></head>
    <body>
        <h1>✅ 服务器运行正常！</h1>
        <p>如果您看到这个页面，说明 Flask 服务器工作正常。</p>
        <p>现在可以启动完整的 EHR Agent 应用了。</p>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return {'status': 'ok', 'message': 'API 工作正常'}

if __name__ == '__main__':
    import socket
    
    def find_free_port(start_port=5000):
        for port in range(start_port, start_port + 10):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                continue
        return None
    
    port = find_free_port(5000)
    
    if port is None:
        print("❌ 无法找到可用端口")
        exit(1)
    
    print("=" * 60)
    print("简单测试服务器")
    print("=" * 60)
    print(f"🌐 访问地址: http://localhost:{port}")
    print(f"📝 测试页面: http://localhost:{port}/test")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
    except KeyboardInterrupt:
        print("\n服务器已停止")

