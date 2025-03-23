import os
import time
from flask import Flask, render_template, request

import azure.cognitiveservices.speech as speechsdk
from elevenlabs import generate, play
import dashscope

# ---------------- 1. Elevenlabs API配置 ----------------
Eleven_API_KEY = os.getenv("Eleven_API_KEY")  # 或者你也可以直接写：Eleven_API_KEY = "xxx"
if Eleven_API_KEY:
    # 当你在本地运行/或服务器上，可设置环境变量 ELEVEN_API_KEY
    from elevenlabs import set_api_key
    set_api_key(Eleven_API_KEY)


# ---------------- 2. Qwen(DashScope) API配置 ----------------
# 这里演示的是基于阿里云达摩院 Qwen 模型的兼容/官方接口。
# 注意：可在控制台( https://dashscope.aliyun.com ) 里获取自己的API Key。
# base_url 不同版本可能不同，此处仅示范使用 /v1/chat/completions 接口的通用写法。
QWEN_API_KEY = os.getenv("QWEN_API_KEY") or "替换为你的真实Key"
client = dashscope.Client(api_key=QWEN_API_KEY, base_url="https://dashscope.aliyuncs.com")

def qwen_chat(user_input):
    """
    调用 Qwen Chat 接口获得回复。
    这里演示最简用法：直接调用 /v1/chat/completions
    """
    body = {
        "model": "Qwen-7B-Chat",  # 或更高规格，如 Qwen-14B-Chat, Qwen-7B-Chat-Intl 等
        "messages": [
            {"role": "user", "content": user_input}
        ],
        # 其他可选参数：
        # "temperature": 0.8,
        # "max_tokens": 512,
        # ...
    }
    # 发起请求
    response = client.post("/v1/chat/completions", json=body)
    # 返回内容
    # 确保 response 中结构合法
    if (
        "choices" in response
        and len(response["choices"]) > 0
        and "message" in response["choices"][0]
        and "content" in response["choices"][0]["message"]
    ):
        return response["choices"][0]["message"]["content"]
    else:
        return "抱歉，我暂时无法理解你的问题。"


# ---------------- 3. Azure Speech to Text (可选) ----------------
def recognize_from_microphone():
    """
    使用Azure语音识别，将用户的语音输入转换为文本
    在调用前，需要将环境变量 SPeECH_KEY、SPEECH_REGION 配置好
    """
    speech_key = os.getenv("SPEECH_KEY")
    speech_region = os.getenv("SPEECH_REGION")
    if not speech_key or not speech_region:
        print("未检测到环境变量 SPEECH_KEY 或 SPEECH_REGION，请先配置后再试。")
        return None

    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=speech_region
    )
    speech_config.speech_recognition_language = "zh-CN"  # 设为中文简体
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "ja-JP", "zh-CN"]
    )
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config
    )

    print("请开始说话...")
    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("已识别语音: {}".format(result.text))
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("无法识别语音: {}".format(result.no_match_details))
        return None
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("语音识别已取消: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("错误详情: {}".format(cancellation_details.error_details))
            print("你是否正确配置了SPEECH_KEY以及SPEECH_REGION?")
        return None


# ---------------- 4. Flask Web ----------------
app = Flask(__name__)

@app.route("/")
def index():
    """
    网站首页路由。假设你有一个 index.html 可以展示输入框、按钮等
    """
    return render_template("index.html")

@app.route("/get", methods=["GET", "POST"])
def completion_response():
    """
    当用户在页面前端输入文本或点击语音按钮后，会请求这个路由
    """
    user_input = request.args.get("msg", "")

    # 当前端msg为空，说明可能是点击了语音输入按钮，此时进行识别
    if user_input.strip() == "":
        recognized_text = recognize_from_microphone()
        if recognized_text is None:
            return "抱歉, 无法识别你的声音. 请重试或输入文本。"
        user_input = recognized_text

    # 调用 Qwen 获取回复
    response = qwen_chat(user_input)

    # ElevenLabs TTS 播放（可选）
    # 如果你没有 voice_id，可以到 ElevenLabs 平台创建自己的声音/选择默认声音
    # voice_id 可以写成 "Bella", "Rachel" 等。
    # model="eleven_multilingual_v2" 适合多语言场景；也可用 "eleven_monolingual_v1" 等。
    try:
        audio = generate(
            text=response,
            voice="your_voice_id_here",  # 替换为你实际的 voice_id
            model="eleven_multilingual_v2",
        )
        play(audio)
    except Exception as e:
        print("TTS合成或播放出错: ", e)

    return str(response)


if __name__ == "__main__":
    # 默认端口 5000
    app.run(debug=True)
