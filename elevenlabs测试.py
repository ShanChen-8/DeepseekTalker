import elevenlabs

# 设置你的API密钥
elevenlabs.set_api_key("sk_453abee09bc9e03594a046312da4de2e828122241dfc664c4")  # 替换为你的API密钥

# 尝试生成一个简单的文本到语音请求
response = elevenlabs.generate(
    text="Hello, this is a test of ElevenLabs API.",
    voice="21m00Tcm4TlvDq8ikWAM",  # 替换为一个有效的voice_id
    model="eleven_multilingual_v2"  # 确保你选择了正确的模型
)

# 播放生成的音频
elevenlabs.play(response)
