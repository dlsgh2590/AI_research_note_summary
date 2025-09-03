# AI 학습/연구 메모 요약기
# 기능: 사용자가 긴 글(논문 초록, 블로그 글, 수업 필기)을 입력 → LLaMA 모델로 핵심 요약
# 결과: Gradio UI에서 "원문 / 요약 탭으로 보기

# -*- coding: utf-8 -*-
import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# =========================
# 1) 모델 로드 (한국어 요약)
# =========================
summarizer_model_name = "lcw99/t5-base-korean-text-summary"
summarizer_tokenizer = AutoTokenizer.from_pretrained(summarizer_model_name)
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(summarizer_model_name)

# =========================
# 2) 요약 함수
# =========================
def summarize_text(text, length_option="보통"):
    text = text.strip()
    
    # 짧은 글 예외 처리
    if len(text) < 100:
        return text
    
    if length_option == "짧게":
        max_len, min_len = 80, 30
    else:  # 보통
        max_len, min_len = 200, 50
    
    inputs = summarizer_tokenizer(
        text, 
        return_tensors="pt", 
        max_length=1024, 
        truncation=True
    )
    summary_ids = summarizer_model.generate(
        inputs['input_ids'], 
        max_length=max_len, 
        min_length=min_len, 
        num_beams=4, 
        early_stopping=True,
        no_repeat_ngram_size=3
    )
    summary = summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def summarize_and_process(text, length_option):
    text = text.strip()
    original_len = len(text)
    
    if not text:
        return "원문을 입력하세요.", ""
    
    summary = summarize_text(text, length_option)
    summary_len = len(summary)
    
    out_original = f"{text}\n\n(총 글자수: {original_len})"
    out_summary = f"{summary}\n\n(총 글자수: {summary_len})"
    
    return out_original, out_summary

# =========================
# 3) Gradio UI
# =========================
with gr.Blocks() as demo:
    gr.Markdown("## 📝 한국어 AI 요약 (예시 글 입력해놨음)")

    inp = gr.Textbox(
        lines=12, 
        placeholder="여기에 한국어 텍스트를 붙여넣으세요. 100글자 이상", 
        label="원문 입력",
        value="""트랜스포머 모델은 2017년에 소개된 딥러닝 모델로, 자연어 처리에서 큰 혁신을 가져왔다.  
이 모델은 셀프 어텐션(Self-Attention) 메커니즘을 사용하여 입력 시퀀스를 병렬로 처리할 수 있다.  
기존의 RNN과 달리 장기 의존성 문제를 효과적으로 해결할 수 있어 번역, 요약, 질문응답 등 다양한 NLP 태스크에서 우수한 성능을 보인다.  
트랜스포머 기반의 모델들은 이후 BERT, GPT, T5 등 여러 파생 모델의 기초가 되었으며, 현재 자연어 처리 연구에서 표준으로 자리 잡았다.  
이러한 발전 덕분에 챗봇, 기계번역, 자동 요약 등 실제 서비스에 바로 활용할 수 있는 수준까지 도달하였다."""
    )
    
    length_option = gr.Radio(["짧게", "보통"], label="요약 길이 선택", value="보통")
    btn = gr.Button("실행")

    with gr.Tabs():
        with gr.Tab("원문"):
            out_original = gr.Textbox(label="원문 + 글자수", lines=8)
        with gr.Tab("요약"):
            out_summary = gr.Textbox(label="요약 + 글자수", lines=8)

    btn.click(
        summarize_and_process,
        inputs=[inp, length_option],
        outputs=[out_original, out_summary]
    )

# =========================
# 4) 실행
# =========================
if __name__ == "__main__":
    demo.launch(share=True)
 