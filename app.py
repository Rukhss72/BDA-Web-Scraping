import os
import streamlit as st
import pandas as pd

# Load cleaned CSV
@st.cache_data
def load_data():
    return pd.read_csv("C:/Users/baich/.vscode/web scraping - bda/MyJob_listings1.csv")

data = load_data()

# Page title and slogan
st.title("ELEV8 – Elevate your career")
st.caption("A platform to lift you up, improve your job search, and advance your professional journey.")

# Admin credentials (change as you like)
ADMIN_USERNAME = "Ruk"
ADMIN_PASSWORD = "1234"

# Initialize login state
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

def login():
    st.title("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state['admin_logged_in'] = True
            st.success("Login successful! You can now access admin pages.")
            st.rerun()
        else:
            st.error("Invalid username or password")

def logout():
    if st.button("Logout"):
        st.session_state['admin_logged_in'] = False
        st.rerun()


# Create navigation buttons
# If user is NOT logged in and tries to access "View Applications", force login page
menu = st.sidebar.radio("Navigation", ["Home", "Search Jobs", "View Applications"])

if menu == "View Applications" and not st.session_state['admin_logged_in']:
    login()
else:
    if menu == "Home":
        # your existing Home page code
        st.subheader("Platform Overview")
        st.metric("Jobs Available", f"{len(data):,}")
        st.metric("Companies", f"{data['Company'].nunique():,}")
        st.metric("Locations", f"{data['Location'].nunique():,}")
        st.metric("Growth This Month", f"{len(data):,} new jobs")

    # Search Jobs page
    elif menu == "Search Jobs":
        st.subheader("Search and Filter Jobs")

        # Search fields
        job_title = st.text_input("Search by Job Title")
        company_name = st.text_input("Search by Company Name")
        location = st.text_input("Filter by Location")
        date_posted = st.text_input("Filter by Date Posted (e.g., '07/05/2025')")

        # Start with all data
        filtered = data.copy()

        # Apply filters
        if job_title:
            filtered = filtered[filtered["Title"].str.lower().str.startswith(job_title.lower())]

        if company_name:
            filtered = filtered[filtered["Company"].str.lower().str.startswith(company_name.lower())]

        if location:
            filtered = filtered[filtered["Location"].str.contains(location, case=False, na=False)]

        if date_posted:
            filtered = filtered[filtered["Date Posted"].str.contains(date_posted, case=False, na=False)]

        st.write(f"Found {len(filtered)} job(s) matching your criteria.")
        st.dataframe(filtered, use_container_width=True)

        # Create an "Apply" button for each job
        for index, row in filtered.iterrows():
            st.markdown(f"**{row['Title']}** at *{row['Company']}* ({row['Location']}) — *{row['Date Posted']}*")
            with st.expander("View & Apply"):
                with st.form(f"apply_form_{index}"):
                    st.write("Fill the form to apply:")
                    full_name = st.text_input("Full Name")
                    email = st.text_input("Email Address")
                    phone = st.text_input("Phone Number")
                    user_location = st.text_input("Your Location")
                    cover_letter = st.text_area("Cover Letter")
                    uploaded_cv = st.file_uploader(
                        "Upload your CV (PDF, DOCX, or image)",
                        type=["pdf", "docx", "jpg", "jpeg", "png"]
                    )
                    submitted = st.form_submit_button("Submit Application")

                    if submitted:
                        if uploaded_cv is None:
                            st.error("Please upload your CV before submitting.")
                        else:
                            # Validate file type
                            head = uploaded_cv.read(4)
                            uploaded_cv.seek(0)

                            file_type = uploaded_cv.type

                            if file_type == "application/pdf":
                                if head != b'%PDF':
                                    st.error("This file does not appear to be a valid PDF.")
                                    valid = False
                                else:
                                    valid = True
                            elif file_type in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document"):
                                valid = True
                            elif file_type in ("image/jpeg", "image/png"):
                                valid = True
                            else:
                                st.error("Unsupported file format.")
                                valid = False

                            if valid:
                                # Save application data
                                app_data = {
                                    "Full Name": full_name,
                                    "Email": email,
                                    "Phone": phone,
                                    "User Location": user_location,
                                    "Job Title": row['Title'],
                                    "Company": row['Company'],
                                    "Cover Letter": cover_letter
                                }
                                apps_df = pd.DataFrame([app_data])

                                # Load any existing applications
                                if os.path.exists("applications.csv"):
                                    existing_apps = pd.read_csv("applications.csv")
                                else:
                                    existing_apps = pd.DataFrame(columns=[
                                        "Full Name", "Email", "Phone", "User Location",
                                        "Job Title", "Company", "Cover Letter"
                                    ])

                                # Create new application dataframe
                                apps_df = pd.DataFrame([{
                                    "Full Name": full_name,
                                    "Email": email,
                                    "Phone": phone,
                                    "User Location": user_location,
                                    "Job Title": row['Title'],
                                    "Company": row['Company'],
                                    "Cover Letter": cover_letter
                                }])

                                # Concatenate existing + new
                                combined_apps = pd.concat([existing_apps, apps_df], ignore_index=True)

                                # Drop ALL duplicate rows (based on ALL columns)
                                combined_apps = combined_apps.drop_duplicates(keep="first")

                                # Overwrite the CSV with deduplicated data
                                combined_apps.to_csv("applications.csv", index=False)

                                # Ensure directory exists
                                os.makedirs(
                                    r"C:\Users\baich\OneDrive\Desktop\Ruk IOT\BDA2\final assignment\uploaded_cvs",
                                    exist_ok=True
                                )

                                # Clean filename
                                safe_title = "".join(
                                    c for c in row['Title'] if c.isalnum() or c in (' ', '_')
                                ).rstrip()
                                safe_name = "".join(
                                    c for c in full_name if c.isalnum() or c in (' ', '_')
                                ).rstrip()
                                extension = uploaded_cv.name.split(".")[-1]

                                cv_path = rf"C:\Users\baich\OneDrive\Desktop\Ruk IOT\BDA2\final assignment\uploaded_cvs\{safe_name.replace(' ', '_')}_{safe_title.replace(' ', '_')}.{extension}"

                                # Save file
                                with open(cv_path, "wb") as f:
                                    f.write(uploaded_cv.getbuffer())

                                st.success("Application submitted successfully!")
        pass

    elif menu == "View Applications":
        st.subheader("Submitted Applications")

        # Load applications
        if os.path.exists("applications.csv"):
            applications = pd.read_csv("applications.csv")
        else:
            st.info("No applications submitted yet.")
            st.stop()

        for idx, app in applications.iterrows():
            with st.container():
                st.subheader(f"Application #{idx + 1}")
                st.markdown(f"**Full Name:** {app['Full Name']}")
                st.markdown(f"**Email:** {app['Email']}")
                st.markdown(f"**Phone:** {app['Phone']}")
                st.markdown(f"**Location:** {app['User Location']}")
                st.markdown(f"**Job Title:** {app['Job Title']}")
                st.markdown(f"**Company:** {app['Company']}")
                st.markdown(f"**Cover Letter:** {app['Cover Letter']}")

                # Recreate safe filename
                safe_title = "".join(
                    c for c in app['Job Title'] if c.isalnum() or c in (' ', '_')
                ).rstrip()
                safe_name = "".join(
                    c for c in app['Full Name'] if c.isalnum() or c in (' ', '_')
                ).rstrip()

                # Check for matching file in uploaded_cvs
                # We look for any file that starts with safe_name_safe_title
                cv_folder = r"C:\Users\baich\OneDrive\Desktop\Ruk IOT\BDA2\final assignment\uploaded_cvs"
                matching_files = [
                    f for f in os.listdir(cv_folder)
                    if f.startswith(f"{safe_name.replace(' ', '_')}_{safe_title.replace(' ', '_')}")
                ]

                if matching_files:
                    cv_file = matching_files[0]
                    cv_path = os.path.join(cv_folder, cv_file)

                    with open(cv_path, "rb") as f:
                        st.download_button(
                            label=f" Download CV ({cv_file.split('.')[-1].upper()})",
                            data=f,
                            file_name=cv_file,
                            mime="application/octet-stream"
                        )
                else:
                    st.warning("No uploaded CV found for this application.")
