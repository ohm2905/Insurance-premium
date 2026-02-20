import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Insurance Predictor", page_icon="💰")


if "token" not in st.session_state:
    st.session_state.token = None

st.sidebar.title("🔐 Authentication")

auth_option = st.sidebar.radio("Choose Option", ["Login", "Sign Up"])

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if auth_option == "Sign Up":

    if st.sidebar.button("Create Account"):
        response = requests.post(
            f"{API_URL}/register",
            json={
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            st.sidebar.success("Account created successfully ✅")
        else:
            st.sidebar.error("User already exists ❌")

if auth_option == "Login":

    if st.sidebar.button("Login"):
        response = requests.post(
            f"{API_URL}/login",
            data={
                "username": username,
                "password": password,
                "grant_type": "password"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

        st.write("STATUS:", response.status_code)
        st.write("RESPONSE:", response.text)

        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.sidebar.success("Logged in successfully ")
        else:
            st.sidebar.error("Login failed ")


if st.session_state.token:
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout "):
        st.session_state.token = None
        st.sidebar.success("Logged out successfully ")
        st.rerun()


# ---------------- NAVIGATION ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Predict Premium", "View Predictions"])

# ---------------- PAGE 1: PREDICT ----------------
if page == "Predict Premium":

    st.title("💰 Insurance Premium Prediction")

    if not st.session_state.token:
        st.warning("Please login first ")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", 18, 100, 30)
        sex = st.selectbox("Sex", ["male", "female"])
        bmi = st.number_input("BMI", 10.0, 60.0, 25.0)

    with col2:
        children = st.number_input("Children", 0, 10, 0)
        smoker = st.selectbox("Smoker", ["yes", "no"])
        region = st.selectbox(
            "Region",
            ["northeast", "northwest", "southeast", "southwest"]
        )

    if st.button("Predict Premium", use_container_width=True):

        payload = {
            "age": age,
            "sex": sex,
            "bmi": bmi,
            "children": children,
            "smoker": smoker,
            "region": region
        }

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()

            st.success("Prediction Successful ")
            st.metric("Predicted Premium", f"₹ {result['predicted_premium']}")
            st.metric("Risk Level", result["risk_level"])
        else:
            st.error("Prediction failed ")


elif page == "View Predictions":

    st.title("📊 Insurance Dashboard")

    if not st.session_state.token:
        st.warning("Please login first 🔐")
        st.stop()


    st.subheader("Filters & Sorting")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        risk_filter = st.selectbox(
            "Risk Level",
            ["All", "Low", "Medium", "High"]
        )

    with col2:
        smoker_filter = st.selectbox(
            "Smoker",
            ["All", "yes", "no"]
        )

    with col3:
        limit = st.number_input("Limit", min_value=1, max_value=50, value=10)

    with col4:
        sort_option = st.selectbox(
            "Sort By Premium",
            ["Default", "Low → High", "High → Low"]
        )

    params = {
        "skip": 0,
        "limit": limit
    }

    if risk_filter != "All":
        params["risk_level"] = risk_filter

    if smoker_filter != "All":
        params["smoker"] = smoker_filter

    if sort_option == "Low → High":
        params["sort_by"] = "predicted_premium"
        params["order"] = "asc"

    elif sort_option == "High → Low":
        params["sort_by"] = "predicted_premium"
        params["order"] = "desc"

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    response = requests.get(
        f"{API_URL}/predictions",
        params=params,
        headers=headers
    )

    if response.status_code == 200:

        result = response.json()
        records = result["data"]

        if len(records) == 0:
            st.info("No records found.")
        else:
            df = pd.DataFrame(records)


            st.subheader("📈 Summary")

            total_records = result["total"]
            avg_premium = round(df["predicted_premium"].mean(), 2)
            high_risk_count = len(df[df["risk_level"] == "High"])

            m1, m2, m3 = st.columns(3)

            m1.metric("Total Records", total_records)
            m2.metric("Average Premium", f"₹ {avg_premium}")
            m3.metric("High Risk Count", high_risk_count)

            st.divider()

            
            for record in records:

                c1, c2, c3, c4 = st.columns([4, 2, 2, 1])

                c1.write(record["id"])
                c2.write(f"₹ {record['predicted_premium']}")
                c3.write(record["risk_level"])

                if c4.button("❌", key=record["id"]):

                    delete_response = requests.delete(
                        f"{API_URL}/prediction/{record['id']}",
                        headers=headers
                    )

                    if delete_response.status_code == 200:
                        st.success("Deleted successfully ")
                        st.rerun()
                    else:
                        st.error("Delete failed ")

            st.divider()

            # ---------- CHARTS ----------
            st.subheader("📊 Analytics Charts")

            chart1, chart2 = st.columns(2)

            with chart1:
                st.write("Risk Level Distribution")
                st.bar_chart(df["risk_level"].value_counts())

            with chart2:
                st.write("Premium Distribution")
                st.bar_chart(df.set_index("id")["predicted_premium"])

            st.divider()

            st.subheader("📈 Premium Trend")
            df_sorted = df.sort_values("predicted_premium")
            st.line_chart(df_sorted["predicted_premium"])

    else:
        st.error("Failed to fetch data ")
