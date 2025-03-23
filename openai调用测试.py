from openai import OpenAI

client = OpenAI(
  api_key="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"
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);
