import streamlit as st
import yaml
import os

LOGIC_FILE = "config/logic_filters.yaml"

# Utility to safely rerun app without Pylance warning
def rerun():
    """Universal rerun with zero Pylance issues and full version fallback."""
    rerun_func = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if callable(rerun_func):
        rerun_func()
    else:
        st.warning("⚠️ No rerun method available in this Streamlit version.")

# Load existing YAML logic
def load_logic():
    if not os.path.exists(LOGIC_FILE):
        return {"filter_logic": []}
    with open(LOGIC_FILE, "r") as f:
        return yaml.safe_load(f) or {"filter_logic": []}

# Save YAML logic
def save_logic(data):
    with open(LOGIC_FILE, "w") as f:
        yaml.dump(data, f)

# Streamlit App
st.set_page_config(page_title="ScalpFlow Logic Builder", layout="wide")

st.title("🧠 ScalpFlow Logic Builder (Filter Mode)")

logic_data = load_logic()
filter_logic = logic_data.get("filter_logic", [])

# Display logic rules
st.subheader("📋 Current Filter Rules")

if not filter_logic:
    st.info("No rules defined yet.")
else:
    for i, rule in enumerate(filter_logic):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.code(rule, language="yaml")
        with col2:
            if st.button("🗑️ Delete", key=f"del_{i}"):
                filter_logic.pop(i)
                save_logic({"filter_logic": filter_logic})
                rerun()

# Add new rule
st.subheader("➕ Add New Rule")

new_rule = st.text_input("Enter new filter rule (e.g. `score >= 3 and L1 == 1 and L2 == 1`)")

if st.button("✅ Add Rule"):
    if new_rule.strip() == "":
        st.warning("Please enter a rule.")
    else:
        filter_logic.append(new_rule.strip())
        save_logic({"filter_logic": filter_logic})
        st.success("Rule added!")
        rerun()

# Raw YAML preview
st.subheader("🛠️ YAML Preview")
st.code(yaml.dump({"filter_logic": filter_logic}), language="yaml")

# File location hint
st.caption(f"📁 Rules saved to: `{LOGIC_FILE}`")

