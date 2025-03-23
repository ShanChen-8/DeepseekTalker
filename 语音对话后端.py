import os
import azure.cognitiveservices.speech as speechsdk
from openai import OpenAI
import time
from flask import Flask, render_template, request
from elevenlabs import generate
from elevenlabs import play
'''

'''


'''
os.getenv("Eleven_API_KEY")：从环境变量中获取Elevenlabs的API密钥。
set_api_key：将获取到的API密钥赋值给set_api_key变量，后续用于认证Elevenlabs服务。
'''
# 设置Elevenlabs API密钥
Eleven_API_KEY=os.getenv("Eleven_API_KEY")
set_api_key = Eleven_API_KEY
'''
创建一个OpenAI客户端实例，用于与OpenAI的API交互，后续用于获取助手的响应。
'''
# 创建一个客户端对象
client = OpenAI()
'''
调用client.beta.assistants.retrieve("asst_")，使用助手ID（在这个示例中是asst_）来获取一个助手实例。这个助手将负责处理用户输入并生成响应。
助手自己在官网创建，基于某种GPT（如GPT-3或GPT-4）模型的实例，它有自己的设置、训练数据和对话规则
'''
# 创建一个助手对象
assistant = client.beta.assistants.retrieve("asst_") # 将双引号中的值替换为自己的助手代号，一般以“asst_”开头
'''
创建一个Flask Web应用实例。Flask是Python中的Web框架，用于快速开发Web应用。__name__标识当前的Python文件。
'''
# 创建一个Flask应用对象
app = Flask(__name__)
'''
创建一个线程实例。线程代表与助手的会话，所有消息和请求都通过这个线程进行交流。
'''
thread = client.beta.threads.create() # 创建线程
'''
这个函数用于通过Azure的语音识别API从麦克风获取用户的语音并转换成文本。
返回文本
首先，它配置了Azure语音识别API的密钥和区域信息。
speechsdk.SpeechRecognizer用来创建一个语音识别器，并从默认麦克风捕获音频。
之后通过recognize_once_async()进行语音识别，并根据结果进行判断：如果识别成功，返回文本；如果识别失败或被取消，返回相应的错误信息。
'''
# 定义一个函数，用来调用Azure speech to text API
def recognize_from_microphone():
    # 请提前将"SPEECH_KEY"和"SPEECH_REGION"写入环境变量
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_recognition_language="zh-CN" #中文简体
    '''
    语言自动检测
    speechsdk.languageconfig.AutoDetectSourceLanguageConfig：这是Azure语音SDK中的一个配置对象，用于启用语言自动检测功能。SDK算是一个工具箱
    languages=["en-US", "ja-JP", "zh-CN"]：指定一个语言列表，Azure将从这些语言中自动检测输入的语音语言。这里的示例指定了：
    en-US：美国英语
    ja-JP：日语
    zh-CN：简体中文
    '''
    auto_detect_source_language_config = \
    speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "ja-JP", "zh-CN"]) #语言自动检测
    '''
    配置音频输入源，具体来说，使用默认麦克风作为音频输入源来进行语音识别。
    speechsdk.audio.AudioConfig：这是Azure语音SDK中的一个类，用于配置音频输入和输出设置。在此代码中，AudioConfig类用于设置音频输入设备。
    use_default_microphone=True：该参数告诉Azure语音识别服务使用系统的默认麦克风设备来接收语音输入。True表示启用默认麦克风。如果你希望使用其他的音频设备（比如外部麦克风），可以指定设备的音频文件路径或其他音频配置。
    '''
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
'''
这个路由处理根URL /，即当用户访问网站时，返回一个HTML页面（index.html）。render_template会加载这个HTML文件。
app是一个flask应用对象
路由（Route）： Flask使用路由来决定不同的URL请求该调用哪个Python函数。路由是一种将访问的URL与处理该请求的Python函数关联的方式。

例如，在下面的代码中：

@app.route("/")
def index():
    return render_template("index.html")

    @app.route("/") 这一行是一个装饰器，它告诉Flask：“当用户访问根路径（/，即首页）时，应该调用index()函数”。
    @app.route("/") 表示URL路径 /，也就是网站的首页。
    def index() 是定义的函数，当用户访问首页时，这个函数会被执行。

视图函数（View Function）： 在Flask中，视图函数是处理路由请求并返回响应的Python函数。视图函数会处理请求并返回一些内容，通常是HTML页面、JSON数据、或者重定向等。

在这个例子中，index()函数是一个视图函数：

def index():
    return render_template("index.html")

这个函数的作用是：

    调用 render_template("index.html")，告诉Flask去找并渲染index.html文件，这个HTML文件通常保存在templates文件夹中。
    然后，Flask会将渲染后的index.html内容返回给浏览器，浏览器会展示该HTML页面。

Flask的工作流程：

    用户访问网页：当用户在浏览器中访问http://127.0.0.1:5000/（本地Flask服务器）时，浏览器会发送一个HTTP请求。
    Flask匹配路由：Flask会检查请求的URL是否与任何定义的路由匹配。在本例中，根路径/会匹配@app.route("/")。
    执行视图函数：Flask找到匹配的路由后，会执行关联的视图函数（即index()）。
    返回响应：index()函数调用render_template("index.html")，Flask会从templates文件夹中找到index.html，将其渲染成HTML，并返回给浏览器。
    浏览器显示页面：浏览器接收到HTML内容后，展示给用户。
'''
@app.route("/")
def index():
    return render_template("index.html")
# 定义另一个路由函数，用来处理用户发送消息的请求
'''
这个路由处理/get路径，当用户发送请求时，根据msg参数的值来处理：

    如果用户输入的是一个空格（" "），则会调用recognize_from_microphone()函数来使用麦克风进行语音识别。
    如果语音识别失败，返回一条错误信息。
'''
@app.route("/get", methods=["GET", "POST"])
def completion_response():
    user_input = request.args.get('msg') # 获取用户输入的内容
    if user_input == " ": # 如果用户输入的是空格，表示要使用麦克风
        user_input = recognize_from_microphone() # 调用Azure speech to text API，将音频转换成文本
        if user_input is None: # 如果没有识别到语音，返回一个错误提示
            return "抱歉, 无法识别你的声音. 请重试或输入文本信息."
    '''
     创建并等待OpenAI助手的回应
    这部分代码将用户的输入（user_input）发送到OpenAI的助手，并创建一个任务（run）。
    wait_on_run()函数通过循环检查任务状态，直到任务完成。
    time.sleep(0.5)确保每次检查任务状态之间有适当的延时。
    '''
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
    '''
    获取助手响应并生成音频
    获取助手的回答（response），并通过Elevenlabs的API将其转化为音频。
    使用generate()生成音频文件，使用play()播放音频。
    最后，返回助手的文本响应，以便在Web页面上显示。
    '''
    messages = client.beta.threads.messages.list(
        thread_id=thread.id, limit="10", order="asc", after=message.id # 升序排列
    )
    for msg in messages.data:
        if msg.role == "assistant":
            response = msg.content[0].text.value # 获取助手的响应内容
            audio = generate(response, voice="voice_id", model="eleven_multilingual_v2") # 生成音频
            play(audio) # 播放音频
    return str(response) # 返回助手的响应内容
'''
启动Flask应用并在本地服务器上运行。这个命令使得Flask应用能够接受Web请求。
'''
if __name__ == "__main__":
    app.run()
