import ollama

client = ollama.Client()

user_query = input("Enter your query: ")

router =  client.chat(model= "llama3.2:3b", 
                        options={"temperature": 0},
                        messages= [{
                        "role": "system",
                        "content": """
                        You are a query router. Output only a single JSON object.

                        DOMAIN: system control, biomedical, coding, electronics, signal processing, finance, general.

                        DEPTH:
                        1 = Single fact or command, one sentence answer possible
                        2 = Needs definition or comparison, no opinion required
                        3 = Needs judgment, recommendation, or interpretation
                        4 = Requires real-time or recent data (post 2024)
                        5 = Requires reading/analyzing external content OR multi-step reasoning across sources

                        RULES:
                        1. If the question is about system control, the depth is ALWAYS 1. 
                        2. If the question is about finance, the depth is ALWAYS more than 1.
                        3. If uncertain, choose the higher depth.
                        4. Any query asking to explain, analyze, or summarize an external document is ALWAYS depth 5
                        5. If the question is casual, ALWAYS output: {"domain": "general knowledge", "depth": 1, "confidence": 0.95, "web_search": false, "reasoning": "Casual questions are often general knowledge"}
                        6. If the question is about building, making or creating software, apps, or websites it's always in the DOMAIN of coding
                        7. Web search is only required if the question requires real-time or recent data (post 2024) or explicitly requires information lookup. If the question can be answered with general knowledge, web search is not required.
                        8. Reasoning must be one short sentence about why you chose the domain and depth, not an answer to the question
                        9. Do not invent new domains or depths, only use the ones above
                        10. If the question is about economics, markets or finance, the domain is ALWAYS finance
                        11. Output ONLY the JSON object. Stop immediately after the closing brace. Do not explain, do not answer the question.
                        12. Any question that requires BOTH comparison AND recommendation together is ALWAYS depth 5.

                        EXAMPLES:
                        1. What is the current stock price of Apple?
                        Answer: {"domain": "finance", "depth": 4, "confidence": 0.9, "web_search": true, "reasoning": "Current stock price requires real-time data lookup"}
                        2. How to reverse a linked list in Python?
                        Answer: {"domain": "coding", "depth": 2, "confidence":0.95, "web_search": false, "reasoning": "Standard coding concept that requires explanation but no current information"}
                        3. Explain this paper to me?
                        Answer: {"domain": "general", "depth": 5, "confidence": 0.7, "web_search": false, "reasoning": "Analyzing external 
                        content requires multi-step reasoning, domain unknown without seeing the paper"}
                        4. Open Terminal and run ls -l
                        Answer: {"domain": "system control", "depth": 1, "confidence": 0.99, "web_search": false, "reasoning": "Terminal command"}
                        5. Hello
                        Answer: {"domain": "general", "depth": 1, "confidence": 0.95, "web_search": false, "reasoning": "Casual questions are often general knowledge"}
                        6. What is the best way to learn Python?
                        Answer: {"domain": "coding", "depth": 3, "confidence": 0.8, "web_search": false, "reasoning": "Requires judgment, recommendation, or interpretation"}
                        7. What is the capital of France?
                        Answer: {"domain": "general", "depth": 1, "confidence": 0.95, "web_search": false, "reasoning": "Standard factual question"}
                        8. What causes diabetes?
                        Answer: {"domain": "biomedical", "depth": 2, "confidence": 0.9, "web_search": false, "reasoning": "Medical condition requires explanation of causes"}
                        9. What causes inflation?
                        Answer: {"domain": "finance", "depth": 2, "confidence": 0.9, "web_search": false, "reasoning": "Economic concept requires explanation of mechanisms"}
                        10. How does a low pass filter work?
                        Answer: {"domain": "signal processing", "depth": 2, "confidence": 0.9, "web_search": false, "reasoning": "Signal processing concept requires technical explanation"}
                        11. How do you compile a program in C?
                        Answer: {"domain": "coding", "depth": 2, "confidence": 0.9, "web_search": false, "reasoning": "Compilation process requires step by step explanation"}
                        12. Compare the efficacy of CRISPR vs traditional gene therapy, analyze the latest research, and recommend which approach is better for treating sickle cell disease.
                        Answer: {"domain": "general", "depth": 5, "confidence": 0.85, "web_search": true, "reasoning": "Comparative analysis of CRISPR and traditional gene therapy requires multi-step reasoning across sources, including recent research studies."}
                        13. How does FFT analyse frequency components in a signal?
                        Answer: {"domain": "signal processing", "depth": 3, "confidence": 0.9, "web_search": false, "reasoning": "Signal processing concept requires technical explanation"}
                        14. What is the difference between a neural network and a deep learning model?
                        Answer: {"domain": "coding", "depth": 3, "confidence": 0.9, "web_search": false, "reasoning": "Technical explanation of neural networks and deep learning models"}
                        """
                        },
                        {
                        "role": "user",
                        "content":user_query
                        }])

print(router.message.content)