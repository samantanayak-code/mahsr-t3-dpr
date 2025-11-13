import streamlit as st
from datetime import datetime, date
from utils.data_entry import save_daily_report, validate_report_data
from utils.media_upload import upload_image_to_storage
from utils.auth import get_current_user


def show_progress_entry():
    """
    MAHSR-T3-DPR – Daily Progress Entry Screen
    Fully integrated with utils.data_entry and Supabase backend.
    """

    st.header("📋 Daily Progress Entry – MAHSR T3")
    st.write("Submit the daily executed work details for your site.")

    # ------------------------------
    # 1. Authenticate User
    # ------------------------------
    user = get_current_user()
    if not user:
        st.error("⚠️ You must be logged in to submit DPR.")
        st.stop()

    st.info(f"Logged in as **{user['full_name']}** (Site: {user['site_code']})")

    # ------------------------------
    # 2. DPR Form Fields
    # ------------------------------
    with st.form("dpr_form", clear_on_submit=False):
        st.subheader("📝 Work Details")

        work_item = st.text_input(
            "Work Item / Activity",
            placeholder="Eg: Excavation, Formwork, Rebar, Concreting…"
        )

        quantity = st.number_input(
            "Quantity Executed Today",
            min_value=0.00,
            step=0.01,
            format="%.2f"
        )

        unit = st.text_input(
            "Unit",
            placeholder="Eg: Cum, MT, Sqm, Rm…"
        )

        progress_percent = st.slider(
            "Overall Progress (%)", 0, 100, 0
        )

        remarks = st.text_area(
            "Remarks (Optional)",
            placeholder="Any site issues, delays, material shortage etc."
        )

        st.divider()

        # --------------------------
        # Optional Photo Upload
        # --------------------------
        uploaded_photo = st.file_uploader(
            "📸 Upload Site Photo (Optional)",
            type=["jpg", "jpeg", "png"]
        )

        st.divider()

        # Date auto enters "today"
        entry_date = st.date_input(
            "Date",
            value=date.today()
        )

        submitted = st.form_submit_button("Submit DPR", use_container_width=True)

    # ------------------------------
    # 3. Handle Form Submission
    # ------------------------------
    if submitted:
        # --- Validate required data ---
        validation_msg = validate_report_data(
            work_item=work_item,
            quantity=quantity,
            unit=unit
        )
        if validation_msg:
            st.error(validation_msg)
            st.stop()

        # --- Upload image if provided ---
        photo_url = None
        if uploaded_photo:
            with st.spinner("Uploading image…"):
                try:
                    photo_url = upload_image_to_storage(
                        file=uploaded_photo,
                        user_site=user["site_code"],
                        folder="dpr_photos"
                    )
                except Exception as e:
                    st.warning(f"⚠️ Image upload failed: {e}")

        # --- Prepare DPR record ---
        report_data = {
            "entry_date": str(entry_date),
            "site_code": user["site_code"],
            "engineer_name": user["full_name"],
            "work_item": work_item,
            "quantity": float(quantity),
            "unit": unit,
            "progress_percent": progress_percent,
            "remarks": remarks,
            "photo_url": photo_url,
            "created_at": datetime.utcnow().isoformat()
        }

        # ------------------------------
        # Save to Supabase
        # ------------------------------
        with st.spinner("Saving DPR to database…"):
            status, message = save_daily_report(report_data)

        if status:
            st.success("✅ DPR Submitted Successfully!")
            st.json(report_data)
        else:
            st.error(f"❌ Failed to save DPR: {message}")
