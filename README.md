# DeepseekTalker - 基于 Deepseek 引擎的语音对话产品

## 项目背景

豆包语音大模型在语音对话领域表现出色，尤其在自然语言理解和生成方面，但其思考深度较浅，限制了复杂对话场景的处理能力。为了解决这一问题，我们开发了一款基于 **Deepseek** 引擎的语音对话产品（目前由阿里云 **Qwen-V1** 模型提供支持）。该产品旨在提供更深层次的推理能力，同时在 **音色处理** 和 **反应速度** 上达到与豆包相媲美的水平。

DeepseekTalker 结合了 **深度推理**、**语音识别**、**文字生成** 和 **语音合成** 技术，能够在用户交互中进行更加复杂和深刻的对话，提升用户体验。其目标是为用户提供自然流畅的语音交互，同时解决现有语音助手在复杂情境下的推理不足问题。

目前我们的产品具备以下几项核心功能：
- **语音识别**：将语音转换为文本。
- **文字生成**：根据用户输入的文本生成回复。
- **语音合成**：将生成的文本转化为自然流畅的语音。

为促进更多开发者的参与，我们已将项目源代码开源，并托管在 GitHub 上：[DeepseekTalker GitHub 主页](https://github.com/ShanChen-8/DeepseekTalker)。

同时，项目的演示视频也已经上传到 Bilibili，用户可以通过以下链接观看演示：[DeepseekTalker 演示视频](https://www.bilibili.com/video/BV1ryXYYiE1J/?spm_id_from=333.1387.homepage.video_card.click&vd_source=a595c4e8a0afd5b410d6ebe278dae843)。

## 项目概述

DeepseekTalker 是一款基于 **Deepseek** 引擎的语音对话系统，具有出色的语音识别、文本生成和语音合成功能。它不仅保持了快速响应速度，还通过深度推理提供了更丰富的对话内容。该系统集成了多种先进技术，包括 **OpenAI** 的语言模型、**Azure** 语音识别技术和 **ElevenLabs** 的自然语音合成技术，致力于为用户提供更加自然、精准的对话体验。

## 安装和配置

在开始使用 DeepseekTalker 之前，请确保你已经安装了以下依赖库：

- `openai`：用于生成对话内容。
- `elevenlabs`：用于将文本转换为语音。
- `azure-cognitiveservices-speech`：用于语音识别。

### 安装依赖

```bash
pip install openai elevenlabs azure-cognitiveservices-speech flask
