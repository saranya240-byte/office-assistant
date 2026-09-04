import streamlit as st

from app.agents.orchestrator import process_query


st.set_page_config(
    page_title="TechNova Office Assistant",
    page_icon="🤖",
    layout="centered",
)


def main():
    st.title("🤖 TechNova Office Assistant")
    st.caption("AI-powered employee assistant")

    # Employee session
    if "employee_id" not in st.session_state:
        st.session_state.employee_id = "TN0001"

    employee_id = st.text_input(
        "Employee ID",
        value=st.session_state.employee_id,
    ).strip().upper()

    st.session_state.employee_id = employee_id

    # Conversation memory
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    query = st.chat_input(
        "Ask about policies, leave, expenses, IT assets..."
    )

    if query:

        st.session_state.messages.append({
            "role": "user",
            "content": query,
        })

        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:
                    result = process_query(
                        query=query,
                        employee_id=employee_id,
                    )

                    response = result.get(
                        "response",
                        result.get(
                            "message",
                            "I could not process your request.",
                        ),
                    )

                    st.markdown(response)

                except Exception as exc:

                    response = (
                        "Sorry, I encountered an error "
                        "while processing your request."
                    )

                    st.error(str(exc))
                    st.markdown(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
        })


if __name__ == "__main__":
    main()