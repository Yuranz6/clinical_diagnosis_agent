from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from config import GOOGLE_API_KEY, GEMINI_MODEL
from soap_generator import SOAPGenerator
from examination_recommender import ExaminationRecommender
from drug_checker import DrugChecker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
CORS(app)

soap_generator = None
exam_recommender = None
drug_checker = None

def init_components():
    global soap_generator, exam_recommender, drug_checker
    if soap_generator is None:
        try:
            soap_generator = SOAPGenerator(GOOGLE_API_KEY, GEMINI_MODEL)
            exam_recommender = ExaminationRecommender(GOOGLE_API_KEY, GEMINI_MODEL)
            drug_checker = DrugChecker(GOOGLE_API_KEY, GEMINI_MODEL)
        except Exception as e:
            print(f"AI 组件初始化失败: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '页面未找到'}), 404

@app.route('/api/generate-soap', methods=['POST'])
def generate_soap():
    try:
        init_components()
        if soap_generator is None:
            return jsonify({'error': 'AI 组件未初始化'}), 500
        
        data = request.json
        consultation_transcript = data.get('transcript', '')
        patient_info = data.get('patient_info', {})
        
        if not consultation_transcript:
            return jsonify({'error': '问诊记录不能为空'}), 400
        
        soap_data = soap_generator.generate_soap(consultation_transcript, patient_info)
        return jsonify({'success': True, 'data': soap_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommend-examinations', methods=['POST'])
def recommend_examinations():
    try:
        init_components()
        if exam_recommender is None:
            return jsonify({'error': 'AI 组件未初始化'}), 500
        
        data = request.json
        soap_data = data.get('soap_data', {})
        consultation_transcript = data.get('transcript', '')
        
        if not soap_data:
            return jsonify({'error': 'SOAP 数据不能为空'}), 400
        
        examinations = exam_recommender.recommend_examinations(soap_data, consultation_transcript)
        return jsonify({'success': True, 'data': examinations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check-drug-conflicts', methods=['POST'])
def check_drug_conflicts():
    try:
        init_components()
        if drug_checker is None:
            return jsonify({'error': 'AI 组件未初始化'}), 500
        
        data = request.json
        plan_text = data.get('plan_text', '')
        patient_info = data.get('patient_info', {})
        
        if not plan_text:
            return jsonify({'error': '治疗计划不能为空'}), 400
        
        prescribed_drugs = drug_checker.extract_drugs_from_plan(plan_text)
        
        if not prescribed_drugs:
            return jsonify({
                'success': True,
                'data': {'has_conflicts': False, 'message': '未在治疗计划中发现药物'}
            })
        
        allergies = []
        if patient_info.get('allergies') and patient_info['allergies'] != '无':
            allergies = [a.strip() for a in patient_info['allergies'].split(',')]
        
        current_meds = []
        if patient_info.get('current_medications') and patient_info['current_medications'] != '无':
            current_meds = [m.strip() for m in patient_info['current_medications'].split(',')]
        
        check_results = drug_checker.check_drug_conflicts(
            prescribed_drugs=prescribed_drugs,
            patient_allergies=allergies if allergies else None,
            current_medications=current_meds if current_meds else None,
            medical_history=patient_info.get('medical_history')
        )
        
        return jsonify({
            'success': True,
            'data': check_results,
            'prescribed_drugs': prescribed_drugs
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save-report', methods=['POST'])
def save_report():
    try:
        data = request.json
        report_content = data.get('content', '')
        
        if not report_content:
            return jsonify({'error': '报告内容不能为空'}), 400
        
        os.makedirs('output', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ehr_report_{timestamp}.txt"
        filepath = os.path.join('output', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return jsonify({'success': True, 'filename': filename, 'filepath': filepath})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
        print("警告: 未设置有效的 GOOGLE_API_KEY")
    else:
        try:
            init_components()
        except Exception as e:
            print(f"AI 组件初始化失败: {e}")
    
    import socket
    
    def find_free_port(start_port=5000, max_attempts=10):
        skip_ports = [5000, 5001, 5002]
        for port in range(start_port, start_port + max_attempts):
            if port in skip_ports:
                continue
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(0.1)
                result = test_sock.connect_ex(('localhost', port))
                test_sock.close()
                if result == 0:
                    continue
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', port))
                sock.close()
                return port
            except (OSError, socket.error):
                continue
        return None
    
    port = find_free_port(5000) or 5000
    print(f"启动服务器: http://localhost:{port}")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"端口 {port} 已被占用")
        else:
            raise

