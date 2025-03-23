import os
import time
from flask import Flask, render_template, request
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from elevenlabs import generate
from elevenlabs import play

# 设置Elevenlabs API密钥
Eleven_API_KEY = os.getenv("Eleven_API_KEY")
set_api_key = Eleven_API_KEY

# 创建一个Flask应用对象
app = Flask(__name__)


# 创建一个线程实例
# 假设这里不再需要OpenAI的client和assistant对象

# 定义一个函数，通过阿里云NLP调用接口获取助手响应
def get_ali_nlp_response(user_input):
    client = AcsClient(
        os.getenv("ALIBABA_ACCESS_KEY_ID"),
        os.getenv("ALIBABA_ACCESS_KEY_SECRET"),
        "cn-shanghai"
    )

    # 使用阿里云的对话生成模型，模型名称及接口详情可能需要根据阿里云的文档进行调整
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('nls-cloud.aliyuncs.com')
    request.set_version('2019-02-28')
    request.set_action_name('Chatbot')
    request.add_query_param('UserMessage', user_input)

    # 调用API并获取结果
    response = client.do_action(request)
    return response.decode("utf-8")  # 假设返回的响应是JSON格式


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
            return "抱歉, 无法识别你的声音. 请重试或输入文本信息."

    # 获取阿里云NLP的响应
    response = get_ali_nlp_response(user_input)

    # 使用ElevenLabs将助手的响应转化为语音并播放
    audio = generate(response, voice="voice_id", model="eleven_multilingual_v2")  # 生成音频
    play(audio)  # 播放音频

    return str(response)  # 返回助手的响应内容


# 启动Flask应用并在本地服务器上运行
if __name__ == "__main__":
    app.run()
