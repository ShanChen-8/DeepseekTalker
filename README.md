# DeepseekTalker - 基于 Deepseek 引擎的语音对话产品

## 项目背景

豆包语音大模型在语音对话方面表现出色，尤其在自然语言理解和生成方面，但其思考深度相对较浅。我们希望开发一款基于 **Deepseek** 引擎的语音对话产品，（目前由阿里云qwen-v1模型支持）旨在提供更深层次的思考和推理能力，同时在 **音色处理** 和 **反应速度** 上达到与豆包相媲美的水平。

目前我们的产品包括以下几项核心功能：

- **语音识别**：将语音转换为文本。
- **文字生成**：基于用户输入的文本生成回复。
- **语音合成**：将生成的文本转化为自然流畅的语音。

为了让更多的开发者能够参与到这个项目中，我们已经将项目源代码开源，并托管在 GitHub 上：[DeepseekTalker](https://github.com/ShanChen-8/DeepseekTalker)

## 项目概述

DeepseekTalker 是一款基于 **Deepseek** 引擎的语音对话系统，具有出色的语音识别、生成和合成功能，能够在保持快速响应的同时，提供更深层次的思考和对话内容。通过集成多种先进的技术，包括 **OpenAI**、**Azure 语音识别** 和 **ElevenLabs** 的语音合成，DeepseekTalker 将为用户提供更加自然、精准的对话体验。

## 安装和配置

首先，请确保你已经安装了以下依赖库：
- `openai`：用于生成对话内容。
- `elevenlabs`：用于将文本转换为语音。
- `azure-cognitiveservices-speech`：用于语音识别。

### 安装依赖

```bash
pip install openai elevenlabs azure-cognitiveservices-speech flask
