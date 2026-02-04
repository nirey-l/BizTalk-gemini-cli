import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)  # 모든 도메인에서의 요청 허용 (개발용)

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
    print("Warning: GROQ_API_KEY is not set or valid. AI features will respond with dummy data.")

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인용 엔드포인트"""
    return jsonify({"status": "healthy", "service": "BizTone Converter API"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_text():
    """텍스트 변환 엔드포인트"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    input_text = data.get('text')
    target_type = data.get('target', 'boss') # boss, colleague, customer
    
    # 1단계: API 연동 테스트를 위한 로직
    # 실제 API 키가 있으면 호출 시도, 없으면 더미 응답 반환
    if client:
        try:
            # 프롬프트 구성 (간단한 예시)
            system_prompt = f"Convert the following text into a professional business tone suitable for a {target_type}. Output only the converted text."
            
            completion = client.chat.completions.create(
                model="llama3-8b-8192", # Groq에서 제공하는 모델 예시
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
            return jsonify({"error": str(e)}), 500
    else:
        # 더미 응답 (API Key 미설정 시)
        dummy_responses = {
            "boss": f"(상사용 변환) {input_text} -> 보고 드립니다. {input_text} 확인 부탁드립니다.",
            "colleague": f"(동료용 변환) {input_text} -> 안녕하세요, {input_text} 관련하여 공유드립니다.",
            "customer": f"(고객용 변환) {input_text} -> 고객님, {input_text} 에 대해 안내해 드리겠습니다."
        }
        
        return jsonify({
            "original": input_text,
            "converted": dummy_responses.get(target_type, input_text),
            "target": target_type,
            "source": "dummy-local"
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
