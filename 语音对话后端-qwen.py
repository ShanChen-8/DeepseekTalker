import os
import azure.cognitiveservices.speech as speechsdk
from openai import OpenAI
import time
from flask import Flask, render_template, request
from elevenlabs import generate,play
# from elevenlabs import play
'''

'''


# 设置Elevenlabs API密钥
Eleven_API_KEY=os.getenv("Eleven_API_KEY")
set_api_key = Eleven_API_KEY

# 创建一个客户端对象
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    # api_key=os.getenv("DASHSCOPE_API_KEY"),
    api_key="sk-09482517baae46019056b38ac57bf1bf",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 创建一个助手对象
assistant = client.beta.assistants.retrieve("asst_") # 将双引号中的值替换为自己的助手代号，一般以“asst_”开头
# 创建一个Flask应用对象
app = Flask(__name__) # 创建一个网站后台（类似开一家店，准备好接客）。
thread = client.beta.threads.create() # 创建线程 创建一个“对话线程”，记录你和AI的聊天记录（保证每次对话连贯）
# 定义一个函数，用来调用Azure speech to text API
def recognize_from_microphone():
    # 请提前将"SPEECH_KEY"和"SPEECH_REGION"写入环境变量
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_recognition_language="zh-CN" #中文简体
    auto_detect_source_language_config = \
    speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "ja-JP", "zh-CN"]) #语言自动检测
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config, audio_config=audio_config)

    print("请对麦克风讲话")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("已识别语音: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text # 返回识别的文本
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
'''当用户打开网站首页时，给他看一个HTML页面（就是你看到的输入框和按钮界面）。'''
@app.route("/")
def index():
    return render_template("index.html")
# 定义另一个路由函数，用来处理用户发送消息的请求
@app.route("/get", methods=["GET", "POST"])
def completion_response():
    user_input = request.args.get('msg') # 获取用户输入的内容
    if user_input == " ": # 如果用户输入的是空格，表示要使用麦克风
        user_input = recognize_from_microphone() # 调用Azure speech to text API，将音频转换成文本
        if user_input is None: # 如果没有识别到语音，返回一个错误提示
            return "抱歉, 无法识别你的声音. 请重试或输入文本信息."
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    def wait_on_run(run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run
    run = wait_on_run(run, thread)
    # 等待运行完成
    wait_on_run(run, thread)
    # 检索回复内容
    messages = client.beta.threads.messages.list(
        thread_id=thread.id, limit="10", order="asc", after=message.id # 升序排列
    )
    for msg in messages.data:
        if msg.role == "assistant":
            response = msg.content[0].text.value # 获取助手的响应内容
            audio = generate(response, voice="voice_id", model="eleven_multilingual_v2") # 生成音频
            play(audio) # 播放音频
    return str(response) # 返回助手的响应内容
if __name__ == "__main__":
    app.run()
