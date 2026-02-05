document.addEventListener('DOMContentLoaded', () => {
    const inputText = document.getElementById('input-text');
    const currentChars = document.getElementById('current-chars');
    const convertBtn = document.getElementById('convert-btn');
    const outputText = document.getElementById('output-text');
    const copyBtn = document.getElementById('copy-btn');
    const copyFeedback = document.getElementById('copy-feedback');
    const loader = document.querySelector('.loader');
    const btnText = document.querySelector('.btn-text');

    // 1. 글자 수 카운트 실시간 업데이트
    inputText.addEventListener('input', () => {
        const length = inputText.value.length;
        currentChars.textContent = length;
    });

    // 2. 변환 로직 (Fetch API)
    convertBtn.addEventListener('click', async () => {
        const text = inputText.value.trim();
        const target = document.querySelector('input[name="target"]:checked').value;

        if (!text) {
            alert('변환할 내용을 입력해주세요.');
            return;
        }

        // 로딩 상태 표시
        convertBtn.disabled = true;
        loader.style.display = 'inline-block';
        btnText.textContent = '변환 중...';
        outputText.textContent = '';

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text, target })
            });

            if (!response.ok) {
                throw new Error('서버 응답 오류가 발생했습니다.');
            }

            const data = await response.json();
            
            // 결과 표시 (애니메이션 효과처럼 순차적으로 표시 가능하나 일단 한 번에)
            outputText.textContent = data.converted;

        } catch (error) {
            console.error('Error:', error);
            alert('변환 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
            outputText.textContent = '오류가 발생했습니다.';
        } finally {
            // 로딩 상태 해제
            convertBtn.disabled = false;
            loader.style.display = 'none';
            btnText.textContent = '변환하기';
        }
    });

    // 3. 복사 기능
    copyBtn.addEventListener('click', () => {
        const text = outputText.textContent;
        if (!text) return;

        navigator.clipboard.writeText(text).then(() => {
            // 시각적 피드백
            copyFeedback.style.opacity = '1';
            setTimeout(() => {
                copyFeedback.style.opacity = '0';
            }, 2000);
        }).catch(err => {
            console.error('Copy failed:', err);
        });
    });
});