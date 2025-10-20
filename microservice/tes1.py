from google import genai

client = genai.Client(api_key="AIzaSyDIJYia8LBXkP94LZ8wkmaBtGCzTXmgO-Y")

resp = client.models.generate_content(
    model="models/gemini-2.5-flash",
    contents="Explain recursion in Python in 3 sentences."
)

print(resp.text)
