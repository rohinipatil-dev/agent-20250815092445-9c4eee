import os
import streamlit as st
from typing import List, Dict
from openai import OpenAI


APP_TITLE = "Respectful Relationship & Consent Assistant"

SYSTEM_PROMPT = """You are a safe, respectful assistant that supports users with healthy relationships, communication, consent, boundaries, dating safety, and emotional well-being.
Safety rules (follow strictly):
- Do not engage in, produce, or roleplay erotic/sexual content, explicit descriptions, or pornographic material.
- Refuse requests for sexual acts, explicit sexting, NSFW roleplay, fetish or kink instructions, or sexual fantasy fulfillment.
- Keep responses PG-13 and non-graphic. No step-by-step sexual techniques or explicit anatomy details beyond high-level education.
- If a user asks for sexual/erotic content, briefly refuse and offer helpful alternatives (communication skills, consent education, boundaries, healthy intimacy ideas without explicit detail, emotional connection, date planning, conflict resolution, safety).
- Educational sexual health questions are allowed at a high level, non-graphically. Encourage consulting qualified professionals for medical concerns.
- Be empathetic, concise, and practical. Do not provide medical, legal, or mental health diagnoses; suggest seeking professionals when appropriate.
"""


def get_client() -> OpenAI:
    return OpenAI()


def generate_response(
    client: OpenAI,
    model: str,
    system_prompt: str,
    chat_history: List[Dict[str, str]],
    user_message: str,
    temperature: float = 0.4,
) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model" not in st.session_state:
        st.session_state.model = "gpt-4"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.4


def sidebar_controls():
    with st.sidebar:
        st.header("Settings")
        st.session_state.model = st.selectbox(
            "Model",
            options=["gpt-4", "gpt-3.5-turbo"],
            index=0,
            help="Use gpt-4 for higher quality. gpt-3.5-turbo is faster and cheaper.",
        )
        st.session_state.temperature = st.slider(
            "Creativity (temperature)",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
        )
        st.markdown("---")
        st.subheader("About")
        st.write(
            "This assistant focuses on healthy relationships, communication, consent, boundaries, "
            "dating safety, and emotional well-being. It will refuse erotic or explicit content."
        )
        st.markdown("• It keeps responses PG-13 and non-graphic.")
        st.markdown("• For medical or legal concerns, please consult a qualified professional.")
        st.markdown("---")
        if st.button("Clear chat"):
            st.session_state.messages = []
            st.experimental_rerun()


def show_initial_message():
    if not st.session_state.messages:
        intro = (
            "Hi! I can help with communication skills, consent, boundaries, healthy intimacy (non-graphic), "
            "date planning, conflict resolution, and emotional well-being. I won’t engage in erotic or explicit content. "
            "How can I support you today?"
        )
        st.session_state.messages.append({"role": "assistant", "content": intro})


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="💬", layout="centered")
    st.title(APP_TITLE)

    init_session_state()
    sidebar_controls()
    show_initial_message()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Type your message...")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Prepare client and generate a safe response
        api_key_set = os.environ.get("OPENAI_API_KEY") is not None
        if not api_key_set:
            assistant_reply = (
                "I’m ready to help, but I don’t see an API key configured. "
                "Please set the OPENAI_API_KEY environment variable and try again."
            )
        else:
            try:
                client = get_client()
                assistant_reply = generate_response(
                    client=client,
                    model=st.session_state.model,
                    system_prompt=SYSTEM_PROMPT,
                    chat_history=[m for m in st.session_state.messages if m["role"] in ("user", "assistant")][:-1],
                    user_message=user_input,
                    temperature=st.session_state.temperature,
                )
            except Exception as e:
                assistant_reply = (
                    "Sorry, I ran into an issue generating a response. "
                    f"Details: {e}"
                )

        with st.chat_message("assistant"):
            st.write(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})


if __name__ == "__main__":
    main()