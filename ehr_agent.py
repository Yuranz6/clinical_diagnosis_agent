import os
from datetime import datetime
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from config import (
    GOOGLE_API_KEY, GEMINI_MODEL, RECORDINGS_DIR, OUTPUT_DIR,
    MICROPHONE_INDEX
)
from voice_recorder import VoiceRecorder
from speech_to_text import SpeechToText
from soap_generator import SOAPGenerator
from examination_recommender import ExaminationRecommender
from drug_checker import DrugChecker

console = Console()

class EHRAgent:
    
    def __init__(self):
        # 检查API密钥
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
            console.print("\n[red]错误: 未设置有效的 GOOGLE_API_KEY[/red]")
            console.print("[yellow]请在 .env 文件中设置您的 Google API Key[/yellow]")
            console.print("[dim]获取 API Key: https://makersuite.google.com/app/apikey[/dim]")
            console.print("[dim]注意: Google API Key 是必需的，用于生成SOAP病历、检查推荐、药物冲突检查和语音识别[/dim]\n")
            raise ValueError("GOOGLE_API_KEY 未设置或无效")
        
       
        # init
        self.voice_recorder = VoiceRecorder()
        self.speech_to_text = SpeechToText(google_api_key=GOOGLE_API_KEY)
        self.soap_generator = SOAPGenerator(GOOGLE_API_KEY, GEMINI_MODEL)
        self.exam_recommender = ExaminationRecommender(GOOGLE_API_KEY, GEMINI_MODEL)
        self.drug_checker = DrugChecker(GOOGLE_API_KEY, GEMINI_MODEL)
        
        self.consultation_transcript = ""
        self.patient_info = {}
        self.soap_data = {}
        
        os.makedirs(RECORDINGS_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def collect_patient_info(self) -> Dict:
        console.print("\n[bold cyan]收集患者基本信息[/bold cyan]")
        info = {}
        
        info['name'] = Prompt.ask("患者姓名", default="未提供")
        info['age'] = Prompt.ask("年龄", default="未提供")
        info['gender'] = Prompt.ask("性别", choices=["男", "女", "其他"], default="未提供")
        info['medical_history'] = Prompt.ask("既往史", default="无")
        info['allergies'] = Prompt.ask("过敏史", default="无")
        info['current_medications'] = Prompt.ask("当前用药（用逗号分隔）", default="无")
        
        return info
    
    def record_consultation(self) -> str:
        console.print("\n[bold cyan]开始问诊录制[/bold cyan]")
        
        transcript_parts = []
        
        try:
            while True:
                console.print("[dim]正在录音，请说话...[/dim]")
                text = self.speech_to_text.transcribe_realtime(MICROPHONE_INDEX)
                
                if text:
                    transcript_parts.append(text)
                    console.print(f"[green]✓ 转录:[/green] {text}\n")
                    if not Confirm.ask("继续录制下一段？", default=True):
                        break
                else:
                    if not Confirm.ask("未检测到语音，是否重试？", default=True):
                        break
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]录制中断[/yellow]")
        except Exception as e:
            console.print(f"[red]录制错误: {e}[/red]")
        
        full_transcript = " ".join(transcript_parts)
        self.consultation_transcript = full_transcript
        
        if full_transcript:
            console.print(f"\n[green]录制完成，共 {len(transcript_parts)} 段录音[/green]")
            console.print(f"[dim]完整转录文本:[/dim]\n{full_transcript}\n")
        else:
            console.print("\n[yellow]未获取到转录文本[/yellow]\n")
        
        return full_transcript
    
    def generate_soap_note(self) -> Dict:
        console.print("\n[bold cyan]正在生成SOAP病历...[/bold cyan]")
        soap_data = self.soap_generator.generate_soap(
            self.consultation_transcript,
            self.patient_info
        )
        self.soap_data = soap_data
        soap_text = self.soap_generator.format_soap_text(soap_data)
        console.print(Panel(soap_text, title="SOAP 病历", border_style="cyan"))
        return soap_data
    
    def recommend_examinations(self) -> List[Dict]:
        console.print("\n[bold cyan]正在推荐检查项目...[/bold cyan]")
        examinations = self.exam_recommender.recommend_examinations(
            self.soap_data,
            self.consultation_transcript
        )
        exam_text = self.exam_recommender.format_recommendations(examinations)
        console.print(Panel(exam_text, title="检查项目推荐", border_style="green"))
        return examinations
    
    def check_drug_conflicts(self) -> Dict:
        console.print("\n[bold cyan]正在检查药物冲突...[/bold cyan]")
        plan_text = self.soap_data.get('plan', '')
        prescribed_drugs = self.drug_checker.extract_drugs_from_plan(plan_text)
        
        if not prescribed_drugs:
            console.print("[yellow]未在治疗计划中发现药物，跳过药物冲突检查[/yellow]")
            return {}
        
        allergies = []
        if self.patient_info.get('allergies') and self.patient_info['allergies'] != '无':
            allergies = [a.strip() for a in self.patient_info['allergies'].split(',')]
        
        current_meds = []
        if self.patient_info.get('current_medications') and self.patient_info['current_medications'] != '无':
            current_meds = [m.strip() for m in self.patient_info['current_medications'].split(',')]
        
        check_results = self.drug_checker.check_drug_conflicts(
            prescribed_drugs=prescribed_drugs,
            patient_allergies=allergies if allergies else None,
            current_medications=current_meds if current_meds else None,
            medical_history=self.patient_info.get('medical_history')
        )
        
        check_text = self.drug_checker.format_check_results(check_results)
        console.print(Panel(check_text, title="药物冲突检查", border_style="yellow"))
        return check_results
    
    def save_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ehr_report_{timestamp}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("EHR Agent 问诊报告\n")
            f.write("="*60 + "\n\n")
            
            f.write("【患者信息】\n")
            for key, value in self.patient_info.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            f.write("【问诊记录】\n")
            f.write(self.consultation_transcript + "\n\n")
            
            f.write(self.soap_generator.format_soap_text(self.soap_data))
            f.write("\n")
            
            examinations = self.exam_recommender.recommend_examinations(
                self.soap_data, self.consultation_transcript
            )
            f.write(self.exam_recommender.format_recommendations(examinations))
            f.write("\n")
            
            plan_text = self.soap_data.get('plan', '')
            prescribed_drugs = self.drug_checker.extract_drugs_from_plan(plan_text)
            if prescribed_drugs:
                allergies = []
                if self.patient_info.get('allergies') and self.patient_info['allergies'] != '无':
                    allergies = [a.strip() for a in self.patient_info['allergies'].split(',')]
                current_meds = []
                if self.patient_info.get('current_medications') and self.patient_info['current_medications'] != '无':
                    current_meds = [m.strip() for m in self.patient_info['current_medications'].split(',')]
                
                check_results = self.drug_checker.check_drug_conflicts(
                    prescribed_drugs=prescribed_drugs,
                    patient_allergies=allergies if allergies else None,
                    current_medications=current_meds if current_meds else None,
                    medical_history=self.patient_info.get('medical_history')
                )
                f.write(self.drug_checker.format_check_results(check_results))
        
        console.print(f"\n[green]报告已保存至: {filepath}[/green]")
        return filepath
    
    def run(self):
        """运行主流程"""
        console.print(Panel.fit(
            "[bold cyan]EHR Agent - 电子病历辅助系统[/bold cyan]\n\n"
            "功能：\n"
            "1. 实时语音转文字记录问诊\n"
            "2. 自动生成SOAP病历\n"
            "3. 推荐检查项目\n"
            "4. 药物冲突检查",
            border_style="cyan"
        ))
        
        try:
            self.patient_info = self.collect_patient_info()
            
            use_voice = Confirm.ask("是否使用语音输入？", default=True)
            
            if use_voice:
                transcript = self.record_consultation()
            else:
                console.print("\n[bold cyan]手动输入问诊记录[/bold cyan]")
                lines = []
                while True:
                    line = Prompt.ask("", default="", show_default=False)
                    if not line:
                        break
                    lines.append(line)
                transcript = "\n".join(lines)
                self.consultation_transcript = transcript
            
            if not transcript:
                console.print("[red]未获取到问诊记录，程序退出[/red]")
                return
            
            self.generate_soap_note()
            self.recommend_examinations()
            self.check_drug_conflicts()
            
            if Confirm.ask("\n是否保存报告到文件？"):
                self.save_results()
            
            console.print("\n[bold green]✓ 问诊流程完成！[/bold green]\n")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]程序被用户中断[/yellow]")
        except Exception as e:
            console.print(f"\n[red]错误: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        finally:
            self.voice_recorder.cleanup()

def main():
    agent = EHRAgent()
    agent.run()

if __name__ == "__main__":
    main()

