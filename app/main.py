import streamlit as st

from app.agents.orchestrator import process_query
from app.utils.memory import save_long_term_memory


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="TechNova Office Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

if "employee_id" not in st.session_state:
    st.session_state.employee_id = "TN0001"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_text(value, fallback="I could not generate a response."):
    """
    Return only valid plain text for the UI.
    """

    if value is None:
        return fallback

    if not isinstance(value, str):
        return fallback

    value = value.strip()

    if not value:
        return fallback

    return value


def add_message(role, content):
    """
    Store only valid user/assistant messages.
    """

    if role not in {"user", "assistant"}:
        return

    content = safe_text(content)

    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
        }
    )


def process_user_query(query):
    """
    Process a user query and display only the final
    natural-language answer.

    Internal tool results, exceptions, routes, intents,
    and Python objects are never displayed.
    """

    query = query.strip()

    if not query:
        return

    employee_id = (
        st.session_state.employee_id
        .strip()
        .upper()
    )

    # -----------------------------------------------------
    # Employee ID validation at UI level
    # -----------------------------------------------------

    if not employee_id:
        st.warning(
            "Please enter your employee ID first."
        )
        return

    # -----------------------------------------------------
    # Save user message
    # -----------------------------------------------------

    add_message(
        "user",
        query,
    )

    # -----------------------------------------------------
    # Display user message
    # -----------------------------------------------------

    with st.chat_message(
        "user",
        avatar="👤",
    ):
        st.write(query)

    # -----------------------------------------------------
    # Process request
    # -----------------------------------------------------

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):

        with st.spinner(
            "Processing your request..."
        ):

            try:

                result = process_query(
                    query=query,
                    employee_id=employee_id,
                    conversation_history=(
                        st.session_state.messages[:-1]
                    ),
                )

                # -------------------------------------------------
                # Extract ONLY final response
                # -------------------------------------------------

                response = None

                if isinstance(result, dict):

                    response = result.get(
                        "response"
                    )

                    if not response:
                        response = result.get(
                            "message"
                        )

                response = safe_text(
                    response,
                    "I could not process your request.",
                )

            except Exception:

                # Never expose exception details,
                # traceback, paths, or internal code.
                response = (
                    "Sorry, I couldn't complete "
                    "that request. Please try again."
                )

        # -----------------------------------------------------
        # Plain text rendering
        # -----------------------------------------------------

        st.write(response)

    # -----------------------------------------------------
    # Save assistant message
    # -----------------------------------------------------

    add_message(
        "assistant",
        response,
    )

    # -----------------------------------------------------
    # Save long-term memory
    # -----------------------------------------------------

    try:

        save_long_term_memory(
            employee_id=employee_id,
            user_message=query,
            assistant_response=response,
        )

    except Exception:
        # Memory errors are intentionally hidden
        # from the employee.
        pass


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🤖 TechNova")

    st.caption("AI Office Assistant")

    st.divider()

    # -----------------------------------------------------
    # Employee
    # -----------------------------------------------------

    st.subheader("Employee")

    employee_id = st.text_input(
        "Employee ID",
        value=st.session_state.employee_id,
        placeholder="TN0001",
        help="Enter your TechNova employee ID.",
    )

    employee_id = (
        employee_id
        .strip()
        .upper()
    )

    st.session_state.employee_id = employee_id

    st.divider()

    # -----------------------------------------------------
    # Session
    # -----------------------------------------------------

    st.subheader("Session")

    if employee_id:

        st.success(
            "Assistant Active"
        )

        st.caption(
            f"Employee ID: {employee_id}"
        )

    else:

        st.warning(
            "Enter your employee ID to continue."
        )

    st.caption(
        f"Messages: {len(st.session_state.messages)}"
    )

    st.divider()

    # -----------------------------------------------------
    # Available services
    # -----------------------------------------------------

    st.subheader(
        "Available Services"
    )

    st.write(
        "👤 Employee information"
    )

    st.write(
        "📅 Leave management"
    )

    st.write(
        "📚 Company policies"
    )

    st.write(
        "💳 Expense information"
    )

    st.write(
        "💻 IT assets"
    )

    st.write(
        "🏢 Office information"
    )

    st.divider()

    # -----------------------------------------------------
    # Clear conversation
    # -----------------------------------------------------

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.session_state.pending_query = None

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.title(
    "TechNova Office Assistant"
)

st.write(
    "Your intelligent workplace assistant for "
    "employee information, leave management, "
    "company policies, expenses and IT support."
)

st.success(
    "Assistant Online"
)


# =========================================================
# QUICK ACTIONS
# =========================================================

st.subheader("Quick Actions")

col1, col2, col3, col4 = st.columns(
    4,
    gap="medium",
)


# =========================================================
# PROFILE CARD
# =========================================================

with col1:

    with st.container(
        border=True,
        height=170,
    ):

        st.markdown(
            "**👤 My Profile**"
        )

        st.caption(
            "View your employee information."
        )

        if st.button(
            "View Profile",
            key="profile_button",
            use_container_width=True,
        ):

            st.session_state.pending_query = (
                "what is my profile"
            )

            st.rerun()


# =========================================================
# LEAVE BALANCE CARD
# =========================================================

with col2:

    with st.container(
        border=True,
        height=170,
    ):

        st.markdown(
            "**📅 Leave Balance**"
        )

        st.caption(
            "Check your available leave."
        )

        if st.button(
            "Check Balance",
            key="leave_button",
            use_container_width=True,
        ):

            st.session_state.pending_query = (
                "what is my leave balance"
            )

            st.rerun()


# =========================================================
# POLICY CARD
# =========================================================

with col3:

    with st.container(
        border=True,
        height=170,
    ):

        st.markdown(
            "**📚 Policies**"
        )

        st.caption(
            "Ask about company policies."
        )

        if st.button(
            "View Policies",
            key="policy_button",
            use_container_width=True,
        ):

            st.session_state.pending_query = (
                "what are the company policies"
            )

            st.rerun()


# =========================================================
# IT ASSET CARD
# =========================================================

with col4:

    with st.container(
        border=True,
        height=170,
    ):

        st.markdown(
            "**💻 IT Assets**"
        )

        st.caption(
            "Check your assigned IT assets."
        )

        if st.button(
            "View Assets",
            key="asset_button",
            use_container_width=True,
        ):

            st.session_state.pending_query = (
                "what IT assets are assigned to me"
            )

            st.rerun()


# =========================================================
# CONVERSATION
# =========================================================

st.write("")

st.subheader("Conversation")


# =========================================================
# EMPTY STATE
# =========================================================

if not st.session_state.messages:

    with st.container(
        border=True,
    ):

        st.info(
            "🤖 How can I help you today?\n\n"
            "Ask a question or choose one of the "
            "quick actions above to get started."
        )


# =========================================================
# DISPLAY CONVERSATION
# =========================================================

for message in st.session_state.messages:

    role = message.get(
        "role"
    )

    content = message.get(
        "content"
    )

    if role not in {
        "user",
        "assistant",
    }:
        continue

    content = safe_text(
        content,
        "",
    )

    if not content:
        continue

    if role == "user":

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.write(content)

    else:

        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            st.write(content)


# =========================================================
# CHAT INPUT
# =========================================================

chat_query = st.chat_input(
    "Ask about leave, policies, expenses, IT assets..."
)


# =========================================================
# HANDLE NORMAL CHAT INPUT
# =========================================================

if chat_query:

    process_user_query(
        chat_query
    )


# =========================================================
# HANDLE QUICK ACTION
# =========================================================

if st.session_state.pending_query:

    pending_query = (
        st.session_state.pending_query
    )

    st.session_state.pending_query = None

    process_user_query(
        pending_query
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "TechNova Pvt. Ltd. · Internal AI Office Assistant"
)