#!/usr/bin/env python3
"""
查找 EHR Agent 应用实际运行的端口
"""
import socket
import requests
import sys

def check_port(port):
    """检查端口是否运行我们的应用"""
    try:
        response = requests.get(f'http://localhost:{port}/', timeout=1)
        if response.status_code == 200:
            content = response.text.lower()
            # 检查是否包含我们的应用特征
            if any(keyword in content for keyword in ['ehr agent', '电子病历', 'soap', '问诊记录', '患者信息']):
                return True, 'EHR Agent'
            elif 'datadog' in content:
                return False, 'Datadog Agent'
            else:
                return False, 'Unknown'
    except:
        pass
    return None, None

def find_app():
    """查找应用端口"""
    print("=" * 60)
    print("查找 EHR Agent Web 应用")
    print("=" * 60)
    
    # 检查常见端口
    ports_to_check = list(range(5000, 5010))
    
    found = False
    for port in ports_to_check:
        print(f"检查端口 {port}...", end=' ')
        is_app, service = check_port(port)
        
        if is_app:
            print(f"✅ 找到 EHR Agent！")
            print("=" * 60)
            print(f"🌐 访问地址: http://localhost:{port}")
            print("=" * 60)
            found = True
            break
        elif service:
            print(f"⚠️  {service}")
        else:
            print("❌ 无响应")
    
    if not found:
        print("\n" + "=" * 60)
        print("❌ 未找到运行中的 EHR Agent 应用")
        print("=" * 60)
        print("\n请启动应用:")
        print("  python run_web.py")
        print("  或")
        print("  python app.py")
        sys.exit(1)

if __name__ == '__main__':
    find_app()

