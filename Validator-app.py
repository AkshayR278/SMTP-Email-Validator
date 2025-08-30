import streamlit as st
from validator import validate_email_address

st.title("Email Validator")

email = st.text_input("Enter an email address:")

if st.button("Validate"):
    if email:
        is_valid = validate_email_address(email)
        if is_valid:
            st.success(f"✅ '{email}' is a valid email address!")
        else:
            st.error(f"❌ '{email}' is NOT a valid email address.")
    else:
        st.warning("Please enter an email to validate.")
