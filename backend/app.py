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
    
    input_text = data.get('text')
    target_type = data.get('target', 'boss') 
    
    if client:
        try:
            # 대상별 한국어 프롬프트 정의
            target_prompts = {
                "boss": "상사(상급자)에게 보고하는 격식 있고 정중한 비즈니스 한국어 말투",
                "colleague": "동료에게 협업을 요청하거나 정보를 공유하는 예의 바르고 친절한 비즈니스 한국어 말투",
                "customer": "고객에게 안내하거나 응대하는 극존칭의 친절한 서비스 한국어 말투"
            }
            
            target_desc = target_prompts.get(target_type, "정중한 비즈니스 한국어 말투")
            
            system_prompt = (
                f"당신은 비즈니스 커뮤니케이션 전문가입니다. "
                f"입력된 텍스트를 {target_desc}로 변환해 주세요. "
                f"반드시 한국어로 답변하고, 변환된 결과 텍스트만 출력하세요."
            )
            
            completion = client.chat.completions.create(
                # [중요] 기존 llama3-8b-8192 대신 이 모델명을 정확히 입력해야 에러가 안 납니다.
                model="llama-3.3-70b-versatile", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_text}
                ],
                temperature=0.7,
                max_tokens=500
            )
            converted_text = completion.choices[0].message.content
            return jsonify({
                "original": input_text,
                "converted": converted_text,
                "target": target_type,
                "source": "groq-api"
            }), 200
            
        except Exception as e:
            # 상세 에러 기록
            with open("error_debug.log", "a", encoding="utf-8") as f:
                import traceback
                f.write(f"Error: {str(e)}\n")
                f.write(traceback.format_exc())
            return jsonify({"error": str(e)}), 500
    else:
        # 더미 응답 (API Key 미설정 시)
        dummy_responses = {
            "boss": f"(상사용 변환) {input_text} -> 보고 드립니다. {input_text} 확인 부탁드립니다.",
            "colleague": f"(동료용 변환) {input_text} -> 안녕하세요, {input_text} 관련하여 공유드립니다.",
            "customer": f"(고객님용 변환) {input_text} -> 고객님, {input_text} 에 대해 안내해 드리겠습니다."
        }
        
        return jsonify({
            "original": input_text,
            "converted": dummy_responses.get(target_type, input_text),
            "target": target_type,
            "source": "dummy-local"
        }), 200

if __name__ == '__main__':
    # 요청하신 대로 5001번 포트로 설정했습니다.
    app.run(host='127.0.0.1', port=5001, debug=True)