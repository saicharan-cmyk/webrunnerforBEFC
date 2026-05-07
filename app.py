import streamlit as st
import requests
import pandas as pd
import json
import io
from datetime import datetime

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="BeeforceRunner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# SESSION STATE
# =========================================
if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None

if "users" not in st.session_state:
    st.session_state.users = [
        {
            "username": "admin",
            "password": "admin123",
            "role": "SUPER_ADMIN",
            "active": True
        },
        {
            "username": "operator",
            "password": "operator123",
            "role": "OPERATOR",
            "active": True
        }
    ]

if "api_configs" not in st.session_state:
    st.session_state.api_configs = []

if "logs" not in st.session_state:
    st.session_state.logs = []

# =========================================
# API CONFIGURATION
# =========================================
AUTH_URL = "https://saas-beeforce.labour.tech/authorization-server/oauth/token"
BASE_URL = "https://saas-beeforce.labour.tech/resource-server/api/shift_templates"
CLIENT_AUTH = "Basic YOUR_BASE64_TOKEN"

# =========================================
# CUSTOM CSS
# =========================================
st.markdown(
    """
    <style>
    .main {
        background-color: #0a0a0a;
        color: white;
    }

    .stButton button {
        background: white;
        color: black;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }

    .stTextInput input {
        background: #1a1a1a;
        color: white;
        border-radius: 10px;
    }

    .stDataFrame {
        background: #111111;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================
# LOGIN FUNCTION
# =========================================
def authenticate(username, password):
    for user in st.session_state.users:
        if (
            user["username"] == username
            and user["password"] == password
            and user["active"]
        ):
            return user
    return None

# =========================================
# LOGIN SCREEN
# =========================================
if not st.session_state.token:

    st.markdown("# 🚀 BeeforceRunner")
    st.markdown("### Enterprise API Automation Platform")

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown("---")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Generate Token"):

            user = authenticate(username, password)

            if not user:
                st.error("❌ User not authorized")
            else:
                try:
                    payload = {
                        "username": username,
                        "password": password,
                        "grant_type": "password"
                    }

                    headers = {
                        "Authorization": CLIENT_AUTH,
                        "Content-Type": "application/x-www-form-urlencoded"
                    }

                    response = requests.post(
                        AUTH_URL,
                        data=payload,
                        headers=headers
                    )

                    if response.status_code == 200:
                        token = response.json()["access_token"]

                        st.session_state.token = token
                        st.session_state.username = username
                        st.session_state.role = user["role"]

                        st.success("✅ Login Successful")
                        st.rerun()
                    else:
                        st.error("❌ Invalid API Credentials")

                except Exception as e:
                    st.error(str(e))

    st.stop()

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("🚀 BeeforceRunner")

st.sidebar.success(f"👤 {st.session_state.username}")
st.sidebar.info(f"🔐 {st.session_state.role}")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload Templates",
        "User Management",
        "API Configuration",
        "Logs"
    ]
)

if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

# =========================================
# AUTH HEADERS
# =========================================
headers_auth = {
    "Authorization": f"Bearer {st.session_state.token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# =========================================
# DASHBOARD
# =========================================
if menu == "Dashboard":

    st.title("📊 Enterprise Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Users", len(st.session_state.users))

    with col2:
        st.metric("API Configs", len(st.session_state.api_configs))

    with col3:
        st.metric("Logs", len(st.session_state.logs))

    st.markdown("---")

    st.subheader("Recent Activity")

    if st.session_state.logs:
        df_logs = pd.DataFrame(st.session_state.logs)
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No logs available")

# =========================================
# USER MANAGEMENT
# =========================================
if menu == "User Management":

    if st.session_state.role != "SUPER_ADMIN":
        st.error("❌ Access Denied")
        st.stop()

    st.title("👥 User Management")

    with st.expander("➕ Create User"):

        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password")
        new_role = st.selectbox(
            "Role",
            ["SUPER_ADMIN", "ADMIN", "OPERATOR", "VIEWER"]
        )

        if st.button("Create User"):
            st.session_state.users.append({
                "username": new_username,
                "password": new_password,
                "role": new_role,
                "active": True
            })

            st.success("✅ User Created")

    st.markdown("---")

    users_df = pd.DataFrame(st.session_state.users)
    st.dataframe(users_df, use_container_width=True)

# =========================================
# API CONFIGURATION
# =========================================
if menu == "API Configuration":

    st.title("⚙️ API Configuration")

    with st.form("api_form"):

        endpoint_name = st.text_input("Endpoint Name")
        endpoint_url = st.text_input("Endpoint URL")
        method = st.selectbox(
            "Method",
            ["GET", "POST", "PUT", "DELETE"]
        )

        submit = st.form_submit_button("Save Configuration")

        if submit:
            st.session_state.api_configs.append({
                "name": endpoint_name,
                "url": endpoint_url,
                "method": method,
                "created_by": st.session_state.username,
                "created_at": str(datetime.now())
            })

            st.success("✅ API Configuration Saved")

    st.markdown("---")

    if st.session_state.api_configs:
        api_df = pd.DataFrame(st.session_state.api_configs)
        st.dataframe(api_df, use_container_width=True)

# =========================================
# UPLOAD TEMPLATES
# =========================================
if menu == "Upload Templates":

    st.title("📤 Upload Excel Templates")

    template_df = pd.DataFrame(columns=[
        "id",
        "name",
        "description",
        "startTime",
        "endTime",
        "beforeStartToleranceMinute",
        "afterStartToleranceMinute"
    ])

    st.download_button(
        "⬇️ Download Template",
        template_df.to_csv(index=False),
        file_name="template.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader(
        "Upload CSV/Excel",
        type=["csv", "xlsx"]
    )

    if uploaded_file:

        try:
            if uploaded_file.name.endswith("csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success("✅ File Uploaded")

            st.dataframe(df, use_container_width=True)

            if st.button("🚀 Process Upload"):

                success = 0
                failed = 0

                for _, row in df.iterrows():
                    try:

                        payload = {
                            "name": row["name"],
                            "description": row.get("description", ""),
                            "startTime": row.get(
                                "startTime",
                                "1970-01-01 06:00:00"
                            ),
                            "endTime": row.get(
                                "endTime",
                                "1970-01-01 15:00:00"
                            ),
                            "beforeStartToleranceMinute": int(
                                row.get("beforeStartToleranceMinute", 0)
                            ),
                            "afterStartToleranceMinute": int(
                                row.get("afterStartToleranceMinute", 0)
                            )
                        }

                        response = requests.post(
                            BASE_URL,
                            headers=headers_auth,
                            json=payload
                        )

                        if response.status_code in [200, 201]:
                            success += 1
                        else:
                            failed += 1

                    except Exception:
                        failed += 1

                st.success(f"✅ Success: {success}")
                st.error(f"❌ Failed: {failed}")

                st.session_state.logs.append({
                    "module": "Upload",
                    "user": st.session_state.username,
                    "success": success,
                    "failed": failed,
                    "time": str(datetime.now())
                })

        except Exception as e:
            st.error(str(e))

# =========================================
# LOGS
# =========================================
if menu == "Logs":

    st.title("📜 System Logs")

    if st.session_state.logs:
        logs_df = pd.DataFrame(st.session_state.logs)
        st.dataframe(logs_df, use_container_width=True)
    else:
        st.info("No logs available")


# Deploy to Streamlit Cloud

#Open:

#[https://share.streamlit.io](https://share.streamlit.io)

#1. Upload app.py to GitHub
#2. Connect GitHub to Streamlit
#3. Deploy

# Default Login

#bash
#Username: admin
#Password: admin123


# Features Included

#✅ Login System
#✅ Token Generation
#✅ User Management
#✅ Admin Roles
#✅ Upload Excel
#✅ API Configuration
#✅ Dashboard
#✅ Logs
#✅ Enterprise UI
#✅ API Integration
#✅ Dynamic Future Expansion
