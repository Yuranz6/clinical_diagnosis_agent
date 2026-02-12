// EHR Agent Web 应用前端 JavaScript

let recognition = null;
let isRecording = false;
let soapData = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeSpeechRecognition();
    setupEventListeners();
    updateCharCount();
});

// 初始化语音识别
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.continuous = true;
        recognition.interimResults = true;
        
        recognition.onstart = function() {
            isRecording = true;
            updateRecordingStatus('正在录音...', true);
            document.getElementById('start-recording').disabled = true;
            document.getElementById('stop-recording').disabled = false;
        };
        
        recognition.onresult = function(event) {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            const textarea = document.getElementById('consultation-text');
            const currentText = textarea.value;
            textarea.value = currentText + finalTranscript;
            updateCharCount();
        };
        
        recognition.onerror = function(event) {
            console.error('语音识别错误:', event.error);
            updateRecordingStatus('语音识别错误: ' + event.error, false);
            stopRecording();
        };
        
        recognition.onend = function() {
            if (isRecording) {
                // 如果还在录音状态，自动重新开始（实现连续录音）
                try {
                    recognition.start();
                } catch (e) {
                    stopRecording();
                }
            }
        };
    } else {
        document.getElementById('start-recording').disabled = true;
        document.getElementById('start-recording').innerHTML = '<span class="icon">⚠️</span> 浏览器不支持语音识别';
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 录音控制
    document.getElementById('start-recording').addEventListener('click', startRecording);
    document.getElementById('stop-recording').addEventListener('click', stopRecording);
    document.getElementById('clear-text').addEventListener('click', clearText);
    
    // 文本输入
    document.getElementById('consultation-text').addEventListener('input', function() {
        updateCharCount();
        updateButtonStates();
    });
    
    // 功能按钮
    document.getElementById('generate-soap').addEventListener('click', generateSOAP);
    document.getElementById('recommend-exams').addEventListener('click', recommendExaminations);
    document.getElementById('check-drugs').addEventListener('click', checkDrugConflicts);
    document.getElementById('save-report').addEventListener('click', saveReport);
}

// 开始录音
function startRecording() {
    if (recognition && !isRecording) {
        try {
            recognition.start();
        } catch (e) {
            console.error('启动录音失败:', e);
            updateRecordingStatus('启动录音失败，请检查麦克风权限', false);
        }
    }
}

// 停止录音
function stopRecording() {
    if (recognition && isRecording) {
        isRecording = false;
        recognition.stop();
        updateRecordingStatus('录音已停止', false);
        document.getElementById('start-recording').disabled = false;
        document.getElementById('stop-recording').disabled = true;
    }
}

// 更新录音状态
function updateRecordingStatus(message, isRecording) {
    const statusEl = document.getElementById('recording-status');
    statusEl.textContent = message;
    statusEl.className = 'status-message' + (isRecording ? ' recording' : '');
}

// 清空文本
function clearText() {
    if (confirm('确定要清空问诊记录吗？')) {
        document.getElementById('consultation-text').value = '';
        updateCharCount();
        updateButtonStates();
    }
}

// 更新字符计数
function updateCharCount() {
    const text = document.getElementById('consultation-text').value;
    document.getElementById('char-count').textContent = text.length;
}

// 更新按钮状态
function updateButtonStates() {
    const hasText = document.getElementById('consultation-text').value.trim().length > 0;
    document.getElementById('generate-soap').disabled = !hasText;
}

// 显示加载提示
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

// 隐藏加载提示
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// 获取患者信息
function getPatientInfo() {
    return {
        name: document.getElementById('patient-name').value || '未提供',
        age: document.getElementById('patient-age').value || '未提供',
        gender: document.getElementById('patient-gender').value || '未提供',
        medical_history: document.getElementById('patient-history').value || '无',
        allergies: document.getElementById('patient-allergies').value || '无',
        current_medications: document.getElementById('patient-medications').value || '无'
    };
}

// 生成 SOAP 病历
async function generateSOAP() {
    const transcript = document.getElementById('consultation-text').value.trim();
    if (!transcript) {
        alert('请先输入问诊记录');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/generate-soap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                transcript: transcript,
                patient_info: getPatientInfo()
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            soapData = result.data;
            displaySOAP(result.data);
            document.getElementById('recommend-exams').disabled = false;
            document.getElementById('check-drugs').disabled = false;
        } else {
            alert('生成 SOAP 病历失败: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 显示 SOAP 病历
function displaySOAP(data) {
    if (data.error) {
        document.getElementById('soap-content').textContent = '错误: ' + data.error;
    } else {
        let html = `
            <h3>主诉</h3>
            <p>${data.chief_complaint || '未提供'}</p>
            
            <h3>主观资料 (S - Subjective)</h3>
            <p>${data.subjective || ''}</p>
            
            <h3>客观资料 (O - Objective)</h3>
            <p>${data.objective || ''}</p>
            
            <h3>评估 (A - Assessment)</h3>
            <p>${data.assessment || ''}</p>
            
            <h3>计划 (P - Plan)</h3>
            <p>${data.plan || ''}</p>
            
            <h3>初步诊断</h3>
            <ul>
                ${(data.preliminary_diagnosis || []).map(d => `<li>${d}</li>`).join('')}
            </ul>
        `;
        document.getElementById('soap-content').innerHTML = html;
        document.getElementById('soap-section').classList.remove('hidden');
    }
}

// 推荐检查项目
async function recommendExaminations() {
    if (!soapData) {
        alert('请先生成 SOAP 病历');
        return;
    }
    
    showLoading();
    
    try {
        const transcript = document.getElementById('consultation-text').value.trim();
        const response = await fetch('/api/recommend-examinations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                soap_data: soapData,
                transcript: transcript
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayExaminations(result.data);
        } else {
            alert('推荐检查项目失败: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 显示检查项目推荐
function displayExaminations(examinations) {
    if (!examinations || examinations.length === 0) {
        document.getElementById('examinations-content').textContent = '未推荐检查项目';
    } else {
        // 按优先级分组
        const high = examinations.filter(e => e.priority === '高');
        const medium = examinations.filter(e => e.priority === '中');
        const low = examinations.filter(e => e.priority === '低');
        
        let html = '';
        
        if (high.length > 0) {
            html += '<h3>高优先级</h3><ul>';
            high.forEach(e => {
                html += `<li><strong>${e.name}</strong> (${e.type})<br>理由: ${e.reason}</li>`;
            });
            html += '</ul>';
        }
        
        if (medium.length > 0) {
            html += '<h3>中优先级</h3><ul>';
            medium.forEach(e => {
                html += `<li><strong>${e.name}</strong> (${e.type})<br>理由: ${e.reason}</li>`;
            });
            html += '</ul>';
        }
        
        if (low.length > 0) {
            html += '<h3>低优先级</h3><ul>';
            low.forEach(e => {
                html += `<li><strong>${e.name}</strong> (${e.type})<br>理由: ${e.reason}</li>`;
            });
            html += '</ul>';
        }
        
        document.getElementById('examinations-content').innerHTML = html;
        document.getElementById('examinations-section').classList.remove('hidden');
    }
}

// 检查药物冲突
async function checkDrugConflicts() {
    if (!soapData || !soapData.plan) {
        alert('请先生成 SOAP 病历');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/check-drug-conflicts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                plan_text: soapData.plan,
                patient_info: getPatientInfo()
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayDrugCheck(result.data, result.prescribed_drugs);
            document.getElementById('save-report').disabled = false;
        } else {
            alert('检查药物冲突失败: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 显示药物冲突检查结果
function displayDrugCheck(data, prescribedDrugs) {
    let html = '';
    
    if (prescribedDrugs && prescribedDrugs.length > 0) {
        html += `<h3>检测到的药物</h3><p>${prescribedDrugs.join(', ')}</p>`;
    }
    
    if (data.message) {
        html += `<p>${data.message}</p>`;
    } else {
        const severity = data.severity || '未知';
        const severityText = {
            '高': '⚠️ 高风险',
            '中': '⚡ 中等风险',
            '低': 'ℹ️ 低风险',
            '无': '✅ 无风险'
        };
        
        html += `<h3>总体评估</h3><p>${severityText[severity] || severity}</p>`;
        
        if (data.allergy_warnings && data.allergy_warnings.length > 0) {
            html += '<h3>过敏警告</h3><ul>';
            data.allergy_warnings.forEach(w => html += `<li>⚠️ ${w}</li>`);
            html += '</ul>';
        }
        
        if (data.drug_interactions && data.drug_interactions.length > 0) {
            html += '<h3>药物相互作用</h3><ul>';
            data.drug_interactions.forEach(i => {
                if (typeof i === 'object') {
                    html += `<li>⚠️ ${i.drugs}: ${i.description}</li>`;
                } else {
                    html += `<li>⚠️ ${i}</li>`;
                }
            });
            html += '</ul>';
        }
        
        if (data.contraindications && data.contraindications.length > 0) {
            html += '<h3>禁忌症</h3><ul>';
            data.contraindications.forEach(c => html += `<li>🚫 ${c}</li>`);
            html += '</ul>';
        }
        
        if (data.dosage_warnings && data.dosage_warnings.length > 0) {
            html += '<h3>剂量警告</h3><ul>';
            data.dosage_warnings.forEach(w => html += `<li>⚠️ ${w}</li>`);
            html += '</ul>';
        }
        
        if (data.recommendations && data.recommendations.length > 0) {
            html += '<h3>建议</h3><ul>';
            data.recommendations.forEach(r => html += `<li>💡 ${r}</li>`);
            html += '</ul>';
        }
        
        if (!data.has_conflicts && (!data.allergy_warnings || data.allergy_warnings.length === 0) && 
            (!data.drug_interactions || data.drug_interactions.length === 0)) {
            html += '<p>✅ 未发现明显的药物冲突或安全风险。</p>';
        }
    }
    
    document.getElementById('drug-check-content').innerHTML = html;
    document.getElementById('drug-check-section').classList.remove('hidden');
}

// 保存报告
async function saveReport() {
    showLoading();
    
    try {
        // 构建报告内容
        let report = '='.repeat(60) + '\n';
        report += 'EHR Agent 问诊报告\n';
        report += '='.repeat(60) + '\n\n';
        
        // 患者信息
        const patientInfo = getPatientInfo();
        report += '【患者信息】\n';
        report += `姓名: ${patientInfo.name}\n`;
        report += `年龄: ${patientInfo.age}\n`;
        report += `性别: ${patientInfo.gender}\n`;
        report += `既往史: ${patientInfo.medical_history}\n`;
        report += `过敏史: ${patientInfo.allergies}\n`;
        report += `当前用药: ${patientInfo.current_medications}\n\n`;
        
        // 问诊记录
        report += '【问诊记录】\n';
        report += document.getElementById('consultation-text').value + '\n\n';
        
        // SOAP 病历
        if (soapData) {
            report += '【SOAP 病历】\n';
            report += `主诉: ${soapData.chief_complaint || '未提供'}\n\n`;
            report += `主观资料 (S):\n${soapData.subjective || ''}\n\n`;
            report += `客观资料 (O):\n${soapData.objective || ''}\n\n`;
            report += `评估 (A):\n${soapData.assessment || ''}\n\n`;
            report += `计划 (P):\n${soapData.plan || ''}\n\n`;
            report += `初步诊断: ${(soapData.preliminary_diagnosis || []).join(', ')}\n\n`;
        }
        
        const response = await fetch('/api/save-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: report
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`报告已保存: ${result.filename}`);
        } else {
            alert('保存报告失败: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('保存失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

