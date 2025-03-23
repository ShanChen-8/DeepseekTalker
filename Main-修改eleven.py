import os
from openai import OpenAI
import time
from flask import Flask, render_template, request
from elevenlabs import generate, play, set_api_key  # 导入 `set_api_key` 方法
import azure.cognitiveservices.speech as speechsdk

# 设置ElevenLabs API密钥
Eleven_API_KEY = "sk_30e93e4ceddf26facfa6a230eb6d5fe85fe8612ab5bb6796"  # 确保密钥是有效的

# 设置 API 密钥到 elevenlabs
set_api_key(Eleven_API_KEY)

# 创建一个OpenAI客户端对象
client = OpenAI(
    api_key="sk-09482517baae46019056b38ac57bf1bf",  # 替换为你的API密钥
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 创建一个Flask应用对象
app = Flask(__name__)

# 定义一个函数，用来调用Azure speech to text API
def recognize_from_microphone():
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                           region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_recognition_language = "zh-CN"  # 中文简体
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "ja-JP", "zh-CN"])  # 语言自动检测
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,
                                                   auto_detect_source_language_config=auto_detect_source_language_config,
                                                   audio_config=audio_config)

    print("请对麦克风讲话")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("已识别语音: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text  # 返回识别的文本
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("无法识别语音: {}".format(speech_recognition_result.no_match_details))
        return None
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("语音识别已取消: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("错误详情: {}".format(cancellation_details.error_details))
            print("你是否正确配置了SPEECH_KEY以及SPEECH_REGION?")
        return None

# 定义一个路由函数，用来处理用户访问你的网页的请求
@app.route("/")
def index():
    return render_template("index.html")

# 定义另一个路由函数，用来处理用户发送消息的请求
@app.route("/get", methods=["GET", "POST"])
def completion_response():
    user_input = request.args.get('msg')  # 获取用户输入的内容
    if user_input == " ":  # 如果用户输入的是空格，表示要使用麦克风
        user_input = recognize_from_microphone()  # 调用Azure speech to text API，将音频转换成文本
        if user_input is None:  # 如果没有识别到语音，返回一个错误提示
            return "抱歉, 无法识别你的声音. 请重试或输入文本信息。"

    try:
        # 调用Qwen接口生成对话
        completion = client.chat.completions.create(
            model="qwen-plus",  # 使用qwen模型
            messages=[
                {'role': 'system', 'content': '你是一个助手，所有内容以二十个字之内回复我.现在你需要教会我快速傅里叶变换'},
                {'role': 'user', 'content': user_input}
            ]
        )
        response = completion.choices[0].message.content  # 获取回复内容
        print(completion.choices[0].message.content)
        # 生成并播放音频
        audio = generate(response, voice="2EiwWnXFnvU5JabPnv8n", model="eleven_multilingual_v2")  # 生成音频
        play(audio)  # 播放音频

        return str(response)  # 返回助手的响应内容
    except Exception as e:
        return f"发生错误: {e}"

if __name__ == "__main__":
    app.run()
