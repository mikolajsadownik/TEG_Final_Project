from __future__ import annotations
import streamlit as st
from services.api_client import ask_question

st.set_page_config(
    page_title="TEG Legal AI Assistant",
    page_icon="⚖️",
    layout="wide",
)


if "messages" not in st.session_state:
    st.session_state.messages: list[dict[str, str]] = [
        {"role": "assistant", "content": "Tu mega mądry student prawa na pierwszym roku jak ci mogę pomóc?"}
    ]


def reset_chat() -> None:
    st.session_state.messages = [
        {"role": "assistant", "content": "Historia wyczyszczona. O co chcesz zapytać?"}
    ]



with st.sidebar:
    st.title("Ustawienia")
    st.button("Wyczyść rozmowę", on_click=reset_chat, use_container_width=True)

    st.markdown(
        """
**Tu mega mądry student prawa na pierwszym roku jak ci mogę pomóc?**

1. Wpisz pytanie.
2. Studnet znajdzie fragmenty w bazie i wygeneruje odpowiedź.
3. Źródła pojawią się pod odpowiedzią.

"""
    )


st.header("Asystent prawny TEG")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if user_input := st.chat_input(placeholder="Twoje pytanie…"):
    # pokaż pytanie użytkownika
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # zapytaj backend
    with st.chat_message("assistant"):
        answer_container = st.empty()
        answer_container.markdown("Myślę…")

        try:
            response = ask_question(user_input)
            answer_text = response.get("answer", "_Brak odpowiedzi_")
            sources = response.get("sources", [])

            md_sources = ""
            if sources:
                md_sources = "\n\n---\n\n##### Źródła\n" + "\n".join(
                    f"- {src}" for src in sources
                )

            answer_container.markdown(answer_text + md_sources)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer_text + md_sources}
            )
        except Exception as exc:
            error_msg = f":red[Błąd zapytania: {exc}]"
            answer_container.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
