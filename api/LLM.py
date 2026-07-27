import ollama
import json
import subprocess
import time
import httpx


class LLM:
    def __init__(self):
        self.client = ollama.AsyncClient()
        self._start_ollama()
        self.message = [
            {
                "role": "system",
                "content": (
                    "Your name is Erasmus. "
                    "You are a helpful assistant. You can understand and generate "
                    "natural language. You can also understand and generate audio. "
                    "You can perform various tasks such as answering questions, "
                    "providing information, and engaging in conversation. "
                    "You can also perform tasks such as summarizing text, translating"
                    "text, and creating text, you will have the ability to use tools soon."
                    "Do not use emojis, emoticons, or any other type of emoticons in your responses. "
                ),
            }
        ]
    
    def _start_ollama(self):
        try:
            httpx.get("http://localhost:11434")
            print("Ollama already running")
            return
        except httpx.ConnectError:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for _ in range(10):
                try:
                    httpx.get("http://localhost:11434")
                    print("Ollama ready")
                    return
                except httpx.ConnectError:
                    time.sleep(1)
            raise RuntimeError("Ollama failed to start")

    async def orchestration_layer (self, user_query):
        classification = await self.router(user_query)
        print(classification)
        try:
            json_content = json.loads(classification)
            depth = json_content["depth"]
        except Exception as e:
            print(f"Router parse error: {e}")
            print(f"Raw router output was: {classification}")
            depth = 1

        if depth < 3:
            self.message.append({"role": "user", "content": user_query})
            response = await self.client.chat(model = "llama3.2:latest", messages = self.message)
            assistant_content = response.message.content
            self.message.append({"role": "assistant", "content": assistant_content})
            return assistant_content
        else:
            self.message.append({"role": "user", "content": user_query})
            assistant_content = "Depth too high"
            return assistant_content



    async def router(self, user_query):
        router = await self.client.chat(model= "llama3.2:3b", 
                        options={"temperature": 0},
                        messages= [{
                        "role": "system",
                        "content": """
                        CRITICAL: Output ONLY a raw JSON object. No explanation. No preamble. 
                        Start your response with { and end with }. Nothing else.
                        """
                        },
                        {
                        "role": "user",
                        "content":user_query
                        }])
        return router.message.content


