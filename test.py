# from openai import OpenAI
# client = OpenAI(base_url="https://genai.science-cloud.hu/ollama/v1/", api_key="sk-78f50a026b6445c99a14dc7ccef78fde")

# print(client.models.list())

# response = client.chat.completions.create(
#   model="llama3.1:8b",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "What is a LLM?"}
#   ]
# )

# print(response)

# from openai import OpenAI

# client = OpenAI(
#     base_url = 'http://localhost:11434/v1',
#     api_key='ollama', # required, but unused
# )

# response = client.chat.completions.create(
#   model="llama2",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The LA Dodgers won in 2020."},
#     {"role": "user", "content": "Where was it played?"}
#   ]
# )
# print(response.choices[0].message.content)

# import ee
# ee.Authenticate()
# ee.Initialize(project='scarlettlee33')
# print(ee.String('Hello from the Earth Engine servers!').getInfo())

import ee

try:
    # Try to initialize without authentication first
    ee.Initialize(project='scarlettlee33')
    print('get here')
except Exception as e:
    # If initialization fails, try authenticating first
    ee.Authenticate()
    ee.Initialize(project='scarlettlee33')
    print('get here 1')

# Test the connection
print(ee.String('Hello from the Earth Engine servers!').getInfo())

# import ee
# ee.Reset()  # Clear existing credentials
# ee.Authenticate()  # Re-authenticate
# ee.Initialize()