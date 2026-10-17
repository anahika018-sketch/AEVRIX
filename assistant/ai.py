import os
import platform
import urllib.parse
import requests
from openai import OpenAI


class AIManager:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "").strip()

        # Real OpenAI keys always start with 'sk-'
        if not api_key or api_key == "your_api_key_here" or not api_key.startswith("sk-"):
            self.client = None
            return

        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            print("AI Init Error:", e)
            self.client = None

    def ask(self, question: str) -> str:
        """
        Answers any question and returns a concise, natural response
        ready to be spoken aloud.
        """
        # 1. If user has a valid OpenAI key, use GPT
        if self.client:
            answer = self._ask_openai(question)
            if answer:
                return answer

        # 2. Try Free AI endpoint (Pollinations.ai - no key needed, returns real AI answers)
        free_ai_answer = self._ask_free_ai(question)
        if free_ai_answer:
            return free_ai_answer

        # 3. Try Wikipedia Knowledge API
        wiki_answer = self._ask_wikipedia(question)
        if wiki_answer:
            return wiki_answer

        # 4. Try DuckDuckGo Instant Answer API
        ddg_answer = self._ask_duckduckgo(question)
        if ddg_answer:
            return ddg_answer

        # 5. Last resort: open Google search
        try:
            import webbrowser
            encoded = urllib.parse.quote(question.strip())
            webbrowser.open(f"https://www.google.com/search?q={encoded}")
        except Exception:
            pass
        return f"I couldn't find a direct answer, so I opened Google search for {question}."

    def _ask_openai(self, question: str) -> str:
        """Query OpenAI API if a valid key is provided."""
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are JARVIS, a helpful voice assistant. "
                            "Give concise, natural answers in 1 to 2 sentences "
                            "suitable for being spoken aloud. Never use markdown symbols like asterisks or hashtags."
                        ),
                    },
                    {"role": "user", "content": question},
                ],
                max_tokens=120,
            )
            return completion.choices[0].message.content.strip()
        except Exception as error:
            print("OpenAI Error:", error)
            return None

    def _ask_free_ai(self, question: str) -> str:
        """Use free AI endpoint to generate direct, spoken answers without an API key."""
        try:
            prompt = (
                f"You are Jarvis voice assistant. Answer in 1 or 2 concise, clear sentences "
                f"suitable for being spoken aloud. No markdown symbols: {question}"
            )
            encoded = urllib.parse.quote(prompt)
            url = f"https://text.pollinations.ai/{encoded}?model=openai"
            resp = requests.get(url, headers={"User-Agent": "JarvisAssistant/1.0"}, timeout=6)
            if resp.status_code == 200 and resp.text.strip():
                answer = resp.text.strip()
                # Clean any markdown or code artifacts
                answer = answer.replace("**", "").replace("*", "").replace("#", "").strip()
                if len(answer) > 10 and not "error" in answer.lower():
                    return answer
        except Exception:
            pass
        return None

    def _ask_wikipedia(self, question: str) -> str:
        """Free instant knowledge fallback using Wikipedia REST & Search APIs."""
        try:
            topic = question.lower().strip("?.! ")
            for prefix in [
                "can you tell me about ",
                "tell me about ",
                "what is the meaning of ",
                "what is ",
                "what are ",
                "who is ",
                "who was ",
                "where is ",
                "explain ",
                "define ",
                "why is ",
                "how does ",
            ]:
                if topic.startswith(prefix):
                    topic = topic[len(prefix):].strip()
                    break

            if not topic:
                return None

            encoded = urllib.parse.quote(topic.strip())
            headers = {"User-Agent": "JarvisAssistant/1.0"}

            # 1. Try direct summary
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
            resp = requests.get(url, headers=headers, timeout=4)
            if resp.status_code == 200:
                extract = resp.json().get("extract")
                if extract:
                    sentences = extract.split(". ")
                    return ". ".join(sentences[:2]) + "."

            # 2. Try opensearch to find closest page title
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={encoded}&limit=1&namespace=0&format=json"
            s_resp = requests.get(search_url, headers=headers, timeout=4)
            if s_resp.status_code == 200:
                s_data = s_resp.json()
                if len(s_data) > 1 and s_data[1]:
                    best_title = s_data[1][0]
                    best_enc = urllib.parse.quote(best_title)
                    best_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{best_enc}"
                    b_resp = requests.get(best_url, headers=headers, timeout=4)
                    if b_resp.status_code == 200:
                        extract = b_resp.json().get("extract")
                        if extract:
                            sentences = extract.split(". ")
                            return ". ".join(sentences[:2]) + "."
        except Exception:
            pass
        return None

    def _ask_duckduckgo(self, question: str) -> str:
        """Query DuckDuckGo Instant Answer API for quick facts."""
        try:
            encoded = urllib.parse.quote(question.strip())
            url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
            resp = requests.get(url, headers={"User-Agent": "JarvisAssistant/1.0"}, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                abstract = data.get("AbstractText", "").strip()
                if abstract:
                    sentences = abstract.split(". ")
                    return ". ".join(sentences[:2]) + "."
                answer = data.get("Answer", "").strip()
                if answer:
                    return answer
        except Exception:
            pass
        return None
