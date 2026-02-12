import google.generativeai as genai
from typing import List, Dict
import json

class ExaminationRecommender:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def recommend_examinations(self, soap_data: Dict, consultation_transcript: str) -> List[Dict]:
        prompt = f"""
你是一位经验丰富的临床医生。请根据以下SOAP病历和问诊记录，推荐必要的检查项目。

SOAP病历摘要：
- 主诉：{soap_data.get('chief_complaint', '未提供')}
- 初步诊断：{', '.join(soap_data.get('preliminary_diagnosis', []))}
- 评估：{soap_data.get('assessment', '')}

问诊记录：
{consultation_transcript[:1000]}...

请推荐必要的检查项目，包括：
1. 常规检查（血常规、尿常规等）
2. 生化检查（肝肾功能、血糖等）
3. 影像学检查（X光、CT、MRI、超声等）
4. 特殊检查（根据病情需要）

对于每个推荐的检查项目，请说明：
- 检查名称
- 检查类型（常规/生化/影像/特殊）
- 推荐理由
- 优先级（高/中/低）

请以JSON格式返回，包含一个examinations数组，每个元素包含：
- name: 检查名称
- type: 检查类型
- reason: 推荐理由
- priority: 优先级
"""
        
        try:
            generation_config = {
                "temperature": 0.3,
                "response_mime_type": "application/json",
            }
            
            response = self.model.generate_content(prompt, generation_config=generation_config)
            result = json.loads(response.text)
            return result.get('examinations', [])
            
        except Exception as e:
            print(f"推荐检查项目错误: {e}")
            return []
    
    def format_recommendations(self, examinations: List[Dict]) -> str:
        if not examinations:
            return "未推荐检查项目"
        
        text = "\n【推荐检查项目】\n"
        text += "="*60 + "\n\n"
        
        high_priority = [e for e in examinations if e.get('priority') == '高']
        medium_priority = [e for e in examinations if e.get('priority') == '中']
        low_priority = [e for e in examinations if e.get('priority') == '低']
        
        if high_priority:
            text += "【高优先级】\n"
            for i, exam in enumerate(high_priority, 1):
                text += f"{i}. {exam.get('name', '未知')} ({exam.get('type', '未知')})\n"
                text += f"   理由: {exam.get('reason', '未提供')}\n\n"
        
        if medium_priority:
            text += "【中优先级】\n"
            for i, exam in enumerate(medium_priority, 1):
                text += f"{i}. {exam.get('name', '未知')} ({exam.get('type', '未知')})\n"
                text += f"   理由: {exam.get('reason', '未提供')}\n\n"
        
        if low_priority:
            text += "【低优先级】\n"
            for i, exam in enumerate(low_priority, 1):
                text += f"{i}. {exam.get('name', '未知')} ({exam.get('type', '未知')})\n"
                text += f"   理由: {exam.get('reason', '未提供')}\n\n"
        
        return text

