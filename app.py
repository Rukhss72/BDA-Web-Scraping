import sqlite3
import hashlib
import os
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import timedelta
import string


#  CREATE TABLES IF NOT EXISTS
def init_db():
    conn = sqlite3.connect("admin_users.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            user_location TEXT NOT NULL,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            cover_letter TEXT
        )
    """)

    conn.commit()
    conn.close()

# ✅ Call this once when app runs
init_db()





#***kavina Style
# Set page config
st.set_page_config(page_title="ELEV8 Job Platform", layout="wide")

# Global light red theme styling including sidebar
st.markdown("""
    <style>
    body {
        background-color: #FFF5F5 !important;
    }
    .main {
        background-color: #FFF5F5;
    }
    h1, h2, h3, h4, h5, h6, p, .stMarkdown {
        color: #8B0000 !important;
    }
    .stTextInput>div>div>input,
    .stTextArea textarea,
    .stDateInput input {
        background-color: #FFE4E1;
        color: #8B0000;
        border: 1px solid #8B0000;
    }
    .stButton>button {
        background-color: #F8BBD0;
        color: #8B0000;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #F48FB1;
        color: white;
    }
    .stDataFrame {
        background-color: #FFF0F5;
    }
    .st-expanderHeader {
        background-color: #FFE4E1 !important;
        color: #8B0000 !important;
    }
    .stMetric {
        color: #8B0000;
    }

    /* Navigation styling */
    section[data-testid="stSidebar"] {
        background-color: #FFDDE2 !important;
        border-right: 1px solid #F8BBD0;
    }

    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .stRadio div[role="radiogroup"] label {
        background-color: #F8BBD0;
        color: #8B0000 !important;
        padding: 0.6rem 1rem;
        border-radius: 10px;
        border: 1px solid #8B0000;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .stRadio div[role="radiogroup"] label:hover {
        background-color: #F48FB1;
    }
    .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background-color: #8B0000 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title and slogan
st.markdown("""
    <div style="
        background-color: #FFE4EC;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
    ">
        <h1 style='color:#8B0000; margin-bottom: 10px;'>ELEV8 – Elevate your career</h1>
        <p style='color:#8B0000; font-size: 1.1rem;'>
            A platform to lift you up, improve your job search, and advance your professional journey.
        </p>
    </div>
""", unsafe_allow_html=True)

#**kavina


def build_cv_filename(full_name, job_title, extension=""):
    # Remove punctuation from job title
    job_title_clean = job_title.translate(str.maketrans('', '', string.punctuation))

    safe_name = "_".join(full_name.strip().split())  # Replace spaces with _
    safe_title = "_".join(job_title_clean.strip().split())  # Replace spaces with _ after removing punctuation

    return f"{safe_name}_{safe_title}.{extension}" if extension else f"{safe_name}_{safe_title}"


# Load cleaned CSV
@st.cache_data
def load_data():
    return pd.read_csv("C:/Users/baich/.vscode/web scraping - bda/MyJob_List.csv")

data = load_data()

# Today's date
today = pd.Timestamp.today()
last_30_days = today - timedelta(days=30)

# Convert 'Date Posted' from string to datetime
data["Parsed Date"] = pd.to_datetime(data["Date Posted"], dayfirst=True, errors="coerce")

# Filter for jobs in the last 30 days
recent_jobs = data[data["Parsed Date"] >= last_30_days]

#kavina no, so i removed Page title and slogan
#st.title("ELEV8 – Elevate your career")
#st.caption("A platform to lift you up, improve your job search, and advance your professional journey.")

# Initialize login state
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

# Call DB init function to make sure tables exist
#init_db()

# Verify user credentials with SQLite DB
def verify_admin(username, password):
    conn = sqlite3.connect("admin_users.db")
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM admins WHERE username = ? AND password_hash = ?", (username, password_hash))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Login form
def login():
    st.title(" Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if verify_admin(username, password):
            st.session_state['admin_logged_in'] = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# Logout function
def logout():
    if st.button("Logout"):
        st.session_state['admin_logged_in'] = False
        st.success("Logged out.")
        st.rerun()



def insert_application(app_data):
    conn = sqlite3.connect("admin_users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO applications (full_name, email, phone, user_location, job_title, company, cover_letter)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        app_data["Full Name"],
        app_data["Email"],
        app_data["Phone"],
        app_data["User Location"],
        app_data["Job Title"],
        app_data["Company"],
        app_data["Cover Letter"]
    ))
    conn.commit()
    conn.close()

def load_applications():
    conn = sqlite3.connect("admin_users.db")
    df = pd.read_sql_query("SELECT * FROM applications", conn)
    conn.close()
    return df



# Create navigation buttons
# If user is NOT logged in and tries to access "View Applications", force login page
menu = st.sidebar.radio("Navigation", ["Home", "Search Jobs", "Visualization", "View Applications"])

if menu == "View Applications" and not st.session_state['admin_logged_in']:
    login()
else:
    if menu == "Home": #Ajmiirah
        # your existing Home page code
        st.subheader("Platform Overview")
        st.metric("Jobs Available", f"{len(data):,}")
        st.metric("Companies", f"{data['Company'].nunique():,}")
        st.metric("Locations", f"{data['Location'].nunique():,}")
        st.metric("Growth This Month (last 30 days)", f"{len(recent_jobs):,} Jobs")

    # Search Jobs page
    elif menu == "Search Jobs":
        st.subheader("Search and Filter Jobs")

        # Search fields
        job_title = st.text_input("Search by Job Title")
        company_name = st.text_input("Search by Company Name")
        location = st.text_input("Filter by Location")
        #date_posted = st.text_input("Filter by Date Posted (e.g., '07/05/2025')")
        date_posted = st.date_input("Filter by Date Posted", format="DD/MM/YYYY", value=None)

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
            #filtered = filtered[filtered["Date Posted"].str.contains(date_posted, case=False, na=False)]
            filtered = filtered[filtered["Parsed Date"].dt.date == date_posted]

        st.write(f"Found {len(filtered)} job(s) matching your criteria.")
        st.dataframe(filtered.drop(columns=["Parsed Date"]), use_container_width=True)

        # Create an "Apply" button for each job
        for index, row in filtered.iterrows():
            st.markdown(f"{row['Title']}** at {row['Company']} ({row['Location']}) — {row['Date Posted']}")
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
                                app_data = {
                                    "Full Name": full_name,
                                    "Email": email,
                                    "Phone": phone,
                                    "User Location": user_location,
                                    "Job Title": row['Title'],
                                    "Company": row['Company'],
                                    "Cover Letter": cover_letter
                                }

                                insert_application(app_data)  # Save application in SQLite DB

                                # Your existing CV file saving logic goes here (unchanged)

                                #st.success("Application submitted successfully!")

                                # Load any existing applications from SQLite DB
                                #existing_apps = load_applications()  # call your DB load function

                                # If no applications found, create empty DataFrame with columns (optional)
                                #if existing_apps.empty:
                                 #   existing_apps = pd.DataFrame(columns=[
                                  #      "Full Name", "Email", "Phone", "User Location",
                                   #     "Job Title", "Company", "Cover Letter"
                                    #])

                                # Create new application dataframe
                             #   apps_df = pd.DataFrame([{
                              #      "Full Name": full_name,
                               #     "Email": email,
                                #    "Phone": phone,
                                 #   "User Location": user_location,
                                  #  "Job Title": row['Title'],
                                   # "Company": row['Company'],
                                    #"Cover Letter": cover_letter
                              #  }])


                                #def insert_application(app_data):
                                 #   conn = sqlite3.connect("admin_users.db")
                                  #  cursor = conn.cursor()
                                   # cursor.execute("""
                                    #    INSERT INTO applications (full_name, email, phone, user_location, job_title, company, cover_letter)
                                     #   VALUES (?, ?, ?, ?, ?, ?, ?)
                                   # """, (
                                    #    app_data["Full Name"],
                                     #   app_data["Email"],
                                      #  app_data["Phone"],
                                       # app_data["User Location"],
                                        #app_data["Job Title"],
                                       # app_data["Company"],
                                       # app_data["Cover Letter"]
                                    #))
                                    #conn.commit()
                                    #conn.close()


                                #insert_application(app_data)


                                # Ensure directory exists
                                os.makedirs(
                                    r"C:\Users\baich\OneDrive\Desktop\Ruk IOT\BDA2\final assignment\uploaded_cvs",
                                    exist_ok=True
                                )

                                # Clean filename
                                extension = uploaded_cv.name.split(".")[-1]
                                cv_folder = r"C:\Users\baich\OneDrive\Desktop\Ruk IOT\BDA2\final assignment\uploaded_cvs"
                                filename = build_cv_filename(full_name, row['Title'], extension)
                                cv_path = os.path.join(cv_folder, filename)

                                # Save file
                                with open(cv_path, "wb") as f:
                                    f.write(uploaded_cv.getbuffer())

                                st.success("Application submitted successfully!")
        pass

    elif menu == "View Applications" and st.session_state.get('admin_logged_in', False):
        logout()  # Show logout button
        st.subheader("Submitted Applications")

        # Load applications
        def load_applications():
            conn = sqlite3.connect("admin_users.db")
            df = pd.read_sql_query("SELECT * FROM applications", conn)
            conn.close()
            return df


        try:
            applications = load_applications()

        except Exception as e:
            st.info("No applications submitted yet or table is missing.")
            st.stop()

        if st.button(" Remove Duplicate Applications"):
            conn = sqlite3.connect("admin_users.db")
            cursor = conn.cursor()
            cursor.execute("""
                    DELETE FROM applications
                    WHERE id NOT IN (
                        SELECT MIN(id)
                        FROM applications
                        GROUP BY
                            full_name, email, phone, user_location,
                            job_title, company, cover_letter
                    )
                """)
            conn.commit()
            conn.close()
            st.success(" Duplicate applications removed.")
            st.rerun()

        # TEMPORARY DELETE BUTTON FOR DEBUGGING
        #if st.button(" Delete last 2 applications (Debug)"):
         #   applications = applications[:-2]
          #  applications.to_csv("applications.csv", index=False)
           # st.success("Last 2 applications deleted.")
            #st.rerun()

        #  1. Show tabular list view (without cover letter for clarity)
        st.markdown("###  Application Summary Table")
        st.dataframe(applications.drop(columns=["Cover Letter"], errors='ignore'), use_container_width=True)

        #  2. Show detailed view with expanders and download button
        st.markdown("---")
        st.markdown("###  Full Application Details")
        for idx, app in applications.iterrows():
            with st.expander(f"{app['full_name']} – {app['job_title']} at {app['company']}"):
                st.markdown(f"**Email:** {app['email']}")
                st.markdown(f"**Phone:** {app['phone']}")
                st.markdown(f"**Location:** {app['user_location']}")
                st.markdown(f"**Job Title:** {app['job_title']}")
                st.markdown(f"**Company:** {app['company']}")
                st.markdown(f"**Cover Letter:**\n\n{app['cover_letter']}")

                # CV download logic
                cv_folder = r"C:\Users\baich\OneDrive\Desktop\Ruk IOT\BDA2\final assignment\uploaded_cvs"
                #expected_prefix = build_cv_filename(app['Full Name'], app['Job Title']).rsplit(".", 1)[0]
                expected_prefix = build_cv_filename(app['full_name'], app['job_title']).rsplit(".", 1)[0]

                matching_files = [
                    f for f in os.listdir(cv_folder)
                    if f.startswith(expected_prefix)
                ]

                #st.write("Looking for file starting with:", expected_prefix)
                #st.write("Files in folder:", os.listdir(cv_folder))

                if matching_files:
                    cv_file = matching_files[0]
                    cv_path = os.path.join(cv_folder, cv_file)
                    with open(cv_path, "rb") as f:
                        st.download_button(
                            label=f" Download CV ({cv_file.split('.')[-1].upper()})",
                            data=f,
                            file_name=cv_file,
                            mime="application/octet-stream",
                            key = f"download_cv_{idx}"  #  unique key using loop index
                        )
                else:
                    st.warning(" No uploaded CV found for this application.")






#Ajmiirah
    elif menu == "Visualization":
        #st.subheader(" Job Data Visualizations")
        st.markdown("<h2 style='text-align: center;'>Job Data Visualizations</h2>", unsafe_allow_html=True)

        # Pre-check: Add dummy columns if needed
        if "Category" not in data.columns:
            data["Category"] = "Unknown"

        if "Parsed Date" not in data.columns:
            data["Parsed Date"] = pd.to_datetime(data["Date Posted"], errors='coerce')

        # 1. Jobs per Company   Horizontal Bar Chart
        #st.markdown("###  Jobs Posted per Company")
        st.markdown("<h3 style='text-align: center;'>Jobs Posted per Company</h3>", unsafe_allow_html=True)

        #company_counts = data['Company'].value_counts().head(10).reset_index()
        # Replace 'No Company' with 'Others' before counting
        data['Company'] = data['Company'].replace("No Company", "Others")

        company_counts = data['Company'].value_counts().head(10).reset_index()

        company_counts.columns = ["Company", "Job Count"]
        chart1 = alt.Chart(company_counts).mark_bar(color="palevioletred").encode(
            x="Job Count:Q", y=alt.Y("Company:N", sort='-x')
        ).properties(height=400)
        st.altair_chart(chart1)


        #Pie Chart – Job Distribution by Location
        st.markdown("<h3 style='text-align: center;'>Job Distribution by Location </h3>",
                    unsafe_allow_html=True)

        top_locations = data["Location"].value_counts().nlargest(5).reset_index()
        top_locations.columns = ["Location", "Count"]

        # Replace "Mauritius" with "Others" just for visualization
        top_locations["Location"] = top_locations["Location"].replace("Mauritius", "Others")

        #  Define custom gradient-style or themed colors (pick your preferred palette)
        custom_colors = ["#872657", "#A23E71", "#C94C88", "#E07BAF", "#F9B7D1"]  # Dark Raspberry gradient

        #fig, ax = plt.subplots(figsize=(3, 3))  # Smaller width and height in inches
        #ax.pie(top_locations["Count"], labels=top_locations["Location"], autopct="%1.1f%%", colors=custom_colors)
        #ax.set_title("\nTop 5 Job Locations")
        #st.pyplot(fig)

        fig, ax = plt.subplots(figsize=(2.0, 2.0), dpi=400)

        wedges, texts, autotexts = ax.pie(
            top_locations["Count"],
            labels=top_locations["Location"],
            autopct="%1.1f%%",
            colors=custom_colors,
            startangle=90
        )

        # Set font sizes smaller explicitly
        for text in texts:
            text.set_fontsize(4)
        for autotext in autotexts:
            autotext.set_fontsize(5)

        ax.set_title("Top 5 Job Locations", fontsize=4, pad=7)

        st.pyplot(fig)
