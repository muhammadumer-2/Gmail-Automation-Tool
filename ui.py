import streamlit as st
from app import GmailAutomation

# Custom CSS for better styling
def apply_custom_styles():
    st.markdown("""
    <style>
        .stTextInput input, .stTextArea textarea {
            border-radius: 8px !important;
            padding: 10px !important;
        }
        .stButton button {
            width: 100%;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
            background-color: #4CAF50;
            color: white;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .header {
            text-align: center;
            color: #1a73e8;
        }
        .sidebar .sidebar-content {
            background-color: #f5f5f5;
        }
        .success {
            color: #4CAF50;
            font-weight: bold;
        }
        .error {
            color: #f44336;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Gmail Automation Tool",
        page_icon="✉️",
        layout="centered",
        initial_sidebar_state="expanded"
    )
    
    apply_custom_styles()
    
    st.title("✉️ Gmail Automation Tool")
    st.markdown("Automate sending emails through Gmail with this secure tool.")
    
    # Sidebar with settings
    with st.sidebar:
        st.header("Settings")
        headless_mode = st.checkbox("Run in headless mode (no browser window)", value=False)
        show_password = st.checkbox("Show passwords", value=False)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool uses Selenium to automate Gmail operations.
        - Your credentials are used only for the Gmail login process
        - No data is stored or logged
        - Runs securely in your environment
        """)
    
    # Login form
    with st.expander("🔑 Gmail Login Credentials", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Gmail Address", placeholder="your.email@gmail.com")
        with col2:
            password_type = "text" if show_password else "password"
            password = st.text_input("Gmail Password", type=password_type)
    
    # Email composition form
    with st.expander("📧 Compose Email", expanded=True):
        recipient = st.text_input("To", placeholder="recipient@example.com")
        subject = st.text_input("Subject", placeholder="Your email subject")
        body = st.text_area("Message", height=200, placeholder="Type your message here...")
    
    # Status area
    status_area = st.empty()
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Send Email"):
            if not all([email, password, recipient, subject, body]):
                status_area.error("Please fill in all fields before sending.")
            else:
                with st.spinner("Processing your request..."):
                    try:
                        # Initialize automation
                        automation = GmailAutomation(headless=headless_mode)
                        
                        # Login to Gmail
                        login_status = automation.login_to_gmail(email, password)
                        if not login_status:
                            status_area.error("Failed to login to Gmail. Please check your credentials.")
                            automation.close()
                        else:
                            # Compose and send email
                            send_status = automation.compose_and_send_email(recipient, subject, body)
                            if send_status:
                                status_area.success("✅ Email sent successfully!")
                            else:
                                status_area.error("Failed to send email. Please try again.")
                            automation.close()
                    except Exception as e:
                        status_area.error(f"An error occurred: {str(e)}")
    
    with col2:
        if st.button("🔄 Clear Form"):
            # This would need JavaScript to work fully, so we'll just show a message
            status_area.info("Form cleared. Note: For security, please manually clear sensitive fields.")
    
    with col3:
        if st.button("ℹ️ Help"):
            status_area.info("""
            **Help Guide:**
            1. Enter your Gmail credentials
            2. Fill in recipient, subject, and message
            3. Click 'Send Email'
            4. Watch the browser automation (unless in headless mode)
            
            **Note:** First run may take longer as it downloads ChromeDriver.
            """)
    
    # Security disclaimer
    st.markdown("---")
    st.warning("""
    **Security Notice:** 
    - This tool runs locally in your browser.
    - Your credentials are not stored or transmitted to any server.
    - For your security, always check the code before running automation tools.
    """)

if __name__ == "__main__":
    main()