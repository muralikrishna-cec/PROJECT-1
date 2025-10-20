from google import genai

client = genai.Client(api_key="AIzaSyDIJYia8LBXkP94LZ8wkmaBtGCzTXmgO-Y")

# List all models available for your API key
for model in client.models.list():
    print(model.name)
