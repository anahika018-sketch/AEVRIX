import os
import platform
import urllib.parse
import urllib.request
import json

try:
    import requests
except ImportError:
    requests = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class AIManager:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "").strip()

        if not OpenAI or not api_key or api_key == "your_api_key_here" or not api_key.startswith("sk-"):
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

        # 2. Try Free AI endpoint (Pollinations.ai)
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
                            "You are Aevrix, a helpful voice assistant. "
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
        prompt = (
            f"You are Aevrix voice assistant. Answer in 1 or 2 concise, clear sentences "
            f"suitable for being spoken aloud. No markdown symbols: {question}"
        )
        encoded = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded}?model=openai"

        try:
            if requests:
                resp = requests.get(url, headers={"User-Agent": "AevrixAssistant/1.0"}, timeout=6)
                if resp.status_code == 200 and resp.text.strip():
                    text = resp.text.strip().replace("**", "").replace("*", "").replace("#", "").strip()
                    if len(text) > 5 and not "error" in text.lower():
                        return text
            else:
                req = urllib.request.Request(url, headers={"User-Agent": "AevrixAssistant/1.0"})
                with urllib.request.urlopen(req, timeout=6) as response:
                    body = response.read().decode("utf-8").strip()
                    text = body.replace("**", "").replace("*", "").replace("#", "").strip()
                    if len(text) > 5 and not "error" in text.lower():
                        return text
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
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"

            req = urllib.request.Request(url, headers={"User-Agent": "AevrixAssistant/1.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    extract = data.get("extract")
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
            req = urllib.request.Request(url, headers={"User-Agent": "AevrixAssistant/1.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
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
