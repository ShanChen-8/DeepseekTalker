import os
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, render_template, request

# 创建Flask应用对象
app = Flask(__name__)


# 定义一个函数，用来调用Azure Speech to Text API
def recognize_from_microphone():
    # 获取Azure的API密钥和区域
    speech_config = speechsdk.SpeechConfig(subscription=os.getenv('SPEECH_KEY'), region=os.getenv('SPEECH_REGION'))
    speech_config.speech_recognition_language = "zh-CN"  # 设置中文简体语言

    # 配置自动语言检测
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "ja-JP", "zh-CN"])

    # 配置音频输入源（使用默认麦克风）
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config
    )

    print("请对麦克风讲话...")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"已识别语音: {speech_recognition_result.text}")
        return speech_recognition_result.text  # 返回识别的文本
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print(f"无法识别语音: {speech_recognition_result.no_match_details}")
        return None
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print(f"语音识别已取消: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"错误详情: {cancellation_details.error_details}")
        return None


# 定义Flask路由，处理根页面请求
@app.route("/")
def index():
    return render_template("index.html") # 渲染html

'''将URL路径 / 和一个函数绑定在一起。当用户访问这个路径时，Flask会自动调用接下来最近定义的函数'''
# 定义另一个路由函数，用来处理语音识别
@app.route("/get", methods=["GET", "POST"])
def get_speech_recognition():
    user_input = request.args.get('msg')  # 获取用户输入的内容

    if user_input == " ":  # 如果输入是空格，表示要使用麦克风进行语音识别
        user_input = recognize_from_microphone()  # 调用Azure Speech API将音频转换为文本
        if user_input is None:  # 如果语音识别失败
            return "抱歉, 无法识别你的声音. 请重试或输入文本信息。"

    return f"识别结果: {user_input}"


# 启动Flask应用并运行
if __name__ == "__main__":
    app.run()
