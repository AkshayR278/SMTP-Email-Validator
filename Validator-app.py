import io
import csv
import streamlit as st
from validator import validate_email, bulk_validate_csv

st.set_page_config(
    page_title="Email Validator",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .result-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    .valid-card {
        border-left-color: #10B981;
        background-color: #F0FDF4;
    }
    .invalid-card {
        border-left-color: #EF4444;
        background-color: #FEF2F2;
    }
    .info-card {
        border-left-color: #3B82F6;
        background-color: #F0F9FF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.title("📧 Email Validator Pro")
st.markdown(
    "Validate email addresses with syntax checking, DNS MX resolution, and SMTP mailbox verification."
)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    smtp_verify_default = st.checkbox(
        "Always attempt SMTP verification",
        value=False,
        help="If checked, SMTP verification is enabled by default in all validation modes."
    )
    
    sender = st.text_input(
        "SMTP Sender Address",
        value="postmaster@localhost",
        help="The sender address to use during SMTP verification.",
    )
    
    timeout = st.number_input(
        "DNS/SMTP Timeout (seconds)",
        min_value=1,
        max_value=60,
        value=10,
        help="How long to wait for DNS or SMTP responses before timing out.",
    )
    
    st.divider()
    st.markdown(
        """
    ### About this tool
    
    - **Syntax validation**: Uses a Lark grammar parser
    - **DNS lookup**: Resolves MX records for the domain
    - **SMTP verification**: Connects to mail servers via `RCPT TO` (does not send email)
    - **Bulk support**: Process CSV files with multiple addresses
    
    ### Limitations
    
    - SMTP may fail due to network, anti-spam, or firewall rules
    - Catch-all servers may show false positives
    - This tool does not guarantee deliverability
    """
    )

# Main content tabs
tab1, tab2 = st.tabs(["🔍 Single Email", "📊 Bulk Validation"])

with tab1:
    st.header("Validate a Single Email")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        email = st.text_input(
            "Email Address",
            placeholder="user@example.com",
            help="Enter the email address you want to validate.",
        )
    
    with col2:
        st.write("")
        st.write("")
        validate_button = st.button("🔍 Validate", use_container_width=True, type="primary")
    
    if email or validate_button:
        # Advanced options
        with st.expander("⚙️ Advanced Options", expanded=False):
            col_smtp, col_sender, col_timeout = st.columns(3)
            
            with col_smtp:
                smtp_verify = st.checkbox(
                    "SMTP Verification",
                    value=smtp_verify_default,
                    help="Attempt to verify the mailbox exists on the mail server.",
                )
            
            with col_sender:
                adv_sender = st.text_input(
                    "Sender",
                    value=sender,
                    help="Override the default sender address.",
                )
            
            with col_timeout:
                adv_timeout = st.number_input(
                    "Timeout",
                    min_value=1,
                    max_value=60,
                    value=int(timeout),
                    help="Override the default timeout.",
                )
        
        if not email:
            st.info("👉 Enter an email address above to get started.")
        elif validate_button:
            with st.spinner("Validating..."):
                result = validate_email(
                    email,
                    smtp_verify=smtp_verify if email or validate_button else smtp_verify_default,
                    sender=adv_sender if email or validate_button else sender,
                    timeout=int(adv_timeout) if email or validate_button else int(timeout),
                )
            
            # Display result in a card-style format
            if result["syntax_valid"]:
                st.markdown(
                    f"""
                    <div class="result-card valid-card">
                        <h3>✅ Valid Email Address</h3>
                        <p><strong>{result['email']}</strong></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="result-card invalid-card">
                        <h3>❌ Invalid Email Address</h3>
                        <p><strong>{result['email']}</strong> does not match the email grammar.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            
            # Domain info
            if result["domain"]:
                with st.expander("🌐 Domain Information", expanded=True):
                    st.write(f"**Domain**: `{result['domain']}`")
            
            # SMTP results
            if result["smtp_result"]:
                smtp_result = result["smtp_result"]
                
                with st.expander("📬 SMTP Verification Results", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if smtp_result["smtp_verified"] is True:
                            st.metric("Status", "✅ Accepted", delta="Mailbox verified")
                        elif smtp_result["smtp_verified"] is False:
                            st.metric("Status", "❌ Failed", delta="See details below")
                        else:
                            st.metric("Status", "⚠️ Unknown")
                    
                    with col2:
                        st.write(f"**SMTP Status**: `{smtp_result.get('smtp_status', 'N/A')}`")
                    
                    with col3:
                        mx_count = len(smtp_result.get("mx_hosts", []))
                        st.write(f"**MX Records**: {mx_count}")
                    
                    if smtp_result.get("mx_hosts"):
                        st.write("**MX Hosts**:")
                        for host in smtp_result["mx_hosts"]:
                            st.write(f"  - `{host}`")
                    
                    if smtp_result.get("smtp_error"):
                        st.warning(f"**Error**: {smtp_result['smtp_error']}")
            
            # Full JSON results
            with st.expander("📋 Full Validation Details (JSON)", expanded=False):
                st.json(result)

with tab2:
    st.header("Bulk Email Validation")
    st.markdown("Upload a CSV file containing email addresses to validate them in bulk.")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="CSV file should contain at least one column with email addresses.",
    )
    
    if uploaded_file is not None:
        st.success("✅ File uploaded successfully")
        
        # Peek at the CSV
        try:
            csv_content = uploaded_file.read().decode("utf-8")
            lines = csv_content.split("\n")
            if len(lines) > 1:
                first_row = lines[0]
                columns = [col.strip() for col in first_row.split(",")]
                
                st.write(f"**Detected columns**: {', '.join(f'`{col}`' for col in columns)}")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            uploaded_file = None
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            email_column = st.selectbox(
                "Email Column",
                options=columns if 'columns' in locals() else ["email"],
                help="Which column contains the email addresses?",
            )
        
        with col2:
            smtp_verify_bulk = st.checkbox(
                "SMTP Verification",
                value=smtp_verify_default,
                help="Verify mailboxes with SMTP for each address.",
            )
        
        if st.button("🚀 Validate All", type="primary", use_container_width=True):
            with st.spinner("Processing... This may take a moment."):
                try:
                    # Save uploaded file temporarily
                    temp_path = "/tmp/email_upload.csv"
                    with open(temp_path, "w", encoding="utf-8") as f:
                        f.write(csv_content)
                    
                    results = bulk_validate_csv(
                        temp_path,
                        output_path=None,
                        email_column=email_column,
                        smtp_verify=smtp_verify_bulk,
                        sender=sender,
                        timeout=int(timeout),
                    )
                    
                    # Display summary statistics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    total = len(results)
                    syntax_valid = sum(1 for r in results if r["syntax_valid"])
                    smtp_verified = sum(1 for r in results if r.get("smtp_verified") is True)
                    
                    with col1:
                        st.metric("Total Addresses", total)
                    
                    with col2:
                        st.metric("Syntax Valid", syntax_valid, f"{syntax_valid/total*100:.1f}%")
                    
                    with col3:
                        if smtp_verify_bulk:
                            st.metric("SMTP Verified", smtp_verified, f"{smtp_verified/total*100:.1f}%")
                        else:
                            st.metric("SMTP Checked", "—", "disabled")
                    
                    with col4:
                        invalid = total - syntax_valid
                        st.metric("Invalid", invalid, f"{invalid/total*100:.1f}%")
                    
                    st.divider()
                    
                    # Display results table
                    st.subheader("Validation Results")
                    
                    # Prepare data for display
                    display_results = []
                    for r in results:
                        display_results.append({
                            "Email": r[email_column],
                            "Syntax": "✅" if r["syntax_valid"] else "❌",
                            "Domain": r.get("domain", "—"),
                            "SMTP": "✅" if r.get("smtp_verified") is True else ("❌" if r.get("smtp_verified") is False else "—"),
                            "Status": r.get("smtp_status", "—"),
                        })
                    
                    st.dataframe(display_results, use_container_width=True, hide_index=True)
                    
                    # Download results
                    output_csv = io.StringIO()
                    fieldnames = list(results[0].keys()) if results else []
                    writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in results:
                        writer.writerow(row)
                    
                    st.download_button(
                        label="⬇️ Download Results (CSV)",
                        data=output_csv.getvalue(),
                        file_name="validation_results.csv",
                        mime="text/csv",
                    )
                    
                except Exception as e:
                    st.error(f"Error processing CSV: {e}")
    else:
        st.info("👉 Upload a CSV file to get started with bulk validation.")
