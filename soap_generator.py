import google.generativeai as genai
from typing import Dict, Optional
import json
from datetime import datetime

class SOAPGenerator:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def generate_soap(self, consultation_transcript: str, patient_info: Optional[Dict] = None) -> Dict:
        patient_context = ""
        if patient_info:
            patient_context = f"""
患者基本信息：
- 姓名：{patient_info.get('name', '未知')}
- 年龄：{patient_info.get('age', '未知')}
- 性别：{patient_info.get('gender', '未知')}
- 既往史：{patient_info.get('medical_history', '无')}
- 过敏史：{patient_info.get('allergies', '无')}
"""
        
        prompt = f"""
你是一位经验丰富的临床医生。请根据以下问诊记录，生成一份完整的SOAP格式病历。

{patient_context}

问诊记录：
{consultation_transcript}

请按照SOAP格式生成病历，包括：
1. S (Subjective - 主观资料)：患者主诉、现病史、既往史、个人史等
2. O (Objective - 客观资料)：体格检查发现、生命体征等
3. A (Assessment - 评估)：初步诊断、鉴别诊断等
4. P (Plan - 计划)：治疗方案、检查计划、用药计划、随访计划等

请以JSON格式返回，包含以下字段：
- subjective: 主观资料
- objective: 客观资料  
- assessment: 评估
- plan: 计划
- chief_complaint: 主诉（简要）
- preliminary_diagnosis: 初步诊断（列表）

确保内容专业、准确、完整。
"""
        
        try:
            generation_config = {
                "temperature": 0.3,
                "response_mime_type": "application/json",
            }
            
            response = self.model.generate_content(prompt, generation_config=generation_config)
            result = json.loads(response.text)
            result['generated_at'] = datetime.now().isoformat()
            return result
            
        except Exception as e:
            print(f"生成SOAP病历错误: {e}")
            return {
                "error": str(e),
                "subjective": "",
                "objective": "",
                "assessment": "",
                "plan": "",
                "chief_complaint": "",
                "preliminary_diagnosis": []
            }
    
    def format_soap_text(self, soap_data: Dict) -> str:
        if "error" in soap_data:
            return f"错误: {soap_data['error']}"
        
        text = f"""
{'='*60}
SOAP 病历
{'='*60}

【主诉】
{soap_data.get('chief_complaint', '未提供')}

【主观资料 (S - Subjective)】
{soap_data.get('subjective', '')}

【客观资料 (O - Objective)】
{soap_data.get('objective', '')}

【评估 (A - Assessment)】
{soap_data.get('assessment', '')}

【计划 (P - Plan)】
{soap_data.get('plan', '')}

【初步诊断】
{', '.join(soap_data.get('preliminary_diagnosis', []))}

生成时间: {soap_data.get('generated_at', '')}
{'='*60}
"""
        return text

