"""
Streamlit UI entry point for Nerthus AI.

Run with:
    streamlit run nerthus_ai/ui/app.py
"""

from pathlib import Path

import streamlit as st

from nerthus_ai.core.config import get_settings
from nerthus_ai.core.constants import DEFAULT_COLLECTION_NAME

# ---------------------------------------------------------------------------
# Page config (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Nerthus AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load and inject external HTML layout / CSS
# ---------------------------------------------------------------------------
_TEMPLATE_PATH = Path(__file__).parent / "templates" / "custom_layout.html"

with open(_TEMPLATE_PATH, "r", encoding="utf-8") as _fh:
    _custom_html = _fh.read()

st.markdown(_custom_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar – configuration
# ---------------------------------------------------------------------------
settings = get_settings()

with st.sidebar:
    st.header("⚙️ Configuration")
    st.caption(f"Model: **{settings.model_name}**")
    st.caption(f"Temperature: **{settings.temperature}**")
    st.caption(f"Persist dir: `{settings.chroma_persist_directory}`")

    st.divider()

    collection = st.selectbox(
        "Active collection",
        options=list(settings.available_collections.keys()),
        index=list(settings.available_collections.keys()).index(DEFAULT_COLLECTION_NAME)
        if DEFAULT_COLLECTION_NAME in settings.available_collections
        else 0,
    )

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.subheader("💬 Ask a question")

question = st.text_input(
    "Your question",
    placeholder="What are the extrusion parameters for batch A?",
    label_visibility="collapsed",
)

ask_btn = st.button("Ask", type="primary", use_container_width=False)

if ask_btn and question.strip():
    with st.spinner("Querying the knowledge base…"):
        try:
            from nerthus_ai.core.session import NerthusSession  # lazy import

            session = NerthusSession()
            session.set_context(collection)
            result = session.query(question, collection_name=collection)

            st.success("Answer")
            st.write(result["answer"])

            with st.expander(f"📚 Sources ({result['num_sources']} documents)"):
                for i, ctx in enumerate(result["context"], 1):
                    st.markdown(f"**Source {i}**")
                    st.caption(ctx["content"][:400] + ("…" if len(ctx["content"]) > 400 else ""))
        except Exception as exc:
            st.error(f"Error: {exc}")
elif ask_btn:
    st.warning("Please enter a question.")
