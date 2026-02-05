import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 환경 변수 로드
load_dotenv()

# static_folder 경로가 올바른지 확인하세요 (frontend 폴더가 backend와 같은 위치에 있을 때)
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Groq 클라이언트 초기화
api_key = os.getenv("GROQ_API_KEY")
client = None

if api_key and api_key != "your_groq_api_key_here":
    try:
        client = Groq(api_key=api_key)
        print("Groq Client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Groq Client: {e}")
else:
    print("Warning: GROQ_API_KEY is not set or valid.")

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "BizTone Converter API"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_text():
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    input_text = data.get('text').strip()
    target_type = data.get('target', 'boss') 
    
    if not input_text:
        return jsonify({"error": "Text is empty"}), 400

    if client:
        try:
            # 대상별 최적화된 프롬프트 엔지니어링
            prompts = {
                "boss": {
                    "role_desc": "상급자에게 보고하는 비즈니스 전문가",
                    "style": "격식 있고 정중한 존댓말(하십시오체 중심)",
                    "instruction": "결론부터 명확하게 제시하는 두괄식 보고 형식을 갖추세요. 불필요한 수식어는 줄이고 신뢰감을 주는 전문 용어를 사용하세요."
                },
                "colleague": {
                    "role_desc": "동료와 협업하는 프로젝트 매니저",
                    "style": "친절하고 상호 존중하는 부드러운 존댓말(해요체 혼용)",
                    "instruction": "협조를 구하는 어투를 사용하며, 요청 사항과 필요 시 마감 기한을 명확히 포함하세요. '부탁드립니다', '감사합니다'와 같은 협업 지향적 표현을 사용하세요."
                },
                "customer": {
                    "role_desc": "최고의 서비스를 제공하는 CS 전문가",
                    "style": "극존칭을 사용하는 정중하고 친절한 어투",
                    "instruction": "고객의 입장에서 생각하는 서비스 마인드를 강조하세요. '도움을 드리고자 합니다', '불편을 끼쳐 드려 죄송합니다' 등 상황에 맞는 격식 있는 표현을 사용하세요."
                }
            }
            
            p = prompts.get(target_type, prompts["boss"])
            
            system_prompt = (
                f"당신은 {p['role_desc']}입니다. "
                f"사용자가 입력한 일상적인 말투를 {p['style']}로 변환하세요. "
                f"지침: {p['instruction']}\n"
                f"규칙:\n"
                f"1. 반드시 한국어로 답변하세요.\n"
                f"2. 변환된 결과 텍스트만 출력하고 설명이나 인사말은 생략하세요.\n"
                f"3. 원문의 의도를 정확히 유지하세요."
            )
            
            completion = client.chat.completions.create(
                model="moonshotai/kimi-k2-instruct-0905", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_text}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            converted_text = completion.choices[0].message.content.strip()
            
            # 로그 기록 (성공)
            print(f"[INFO] Conversion successful: target={target_type}")
            
            return jsonify({
                "original": input_text,
                "converted": converted_text,
                "target": target_type,
                "source": "groq-api"
            }), 200
            
        except Exception as e:
            # 상세 에러 로깅
            import traceback
            error_msg = f"[ERROR] {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            
            # 파일 로깅 (필요 시)
            log_dir = os.path.join(os.path.dirname(__file__), 'logs')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            with open(os.path.join(log_dir, "error.log"), "a", encoding="utf-8") as f:
                from datetime import datetime
                f.write(f"--- {datetime.now()} ---\n{error_msg}\n")
                
            return jsonify({"error": "AI 변환 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}), 500
    else:
        # API 키가 없을 때의 대체 로직 (개발용)
        print(f"[WARN] Groq Client not initialized. Using dummy response.")
        dummy_responses = {
            "boss": f"[상사 보고] {input_text} 건에 대하여 보고드립니다. 해당 사항 확인 부탁드립니다.",
            "colleague": f"[협조 요청] 안녕하세요, {input_text} 관련하여 협조를 부탁드리고자 합니다. 확인 가능하실까요?",
            "customer": f"[고객 안내] 안녕하십니까 고객님. 문의하신 {input_text} 사항에 대해 정성껏 안내 도와드리겠습니다."
        }
        
        return jsonify({
            "original": input_text,
            "converted": dummy_responses.get(target_type, f"변환된 텍스트: {input_text}"),
            "target": target_type,
            "source": "dummy-local"
        }), 200

if __name__ == '__main__':
    # 요청하신 대로 5001번 포트로 설정했습니다.
    app.run(host='127.0.0.1', port=5001, debug=True)