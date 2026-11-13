
import streamlit as st
import pandas as pd
import re
import sqlite3
from datetime import date
import database
from client import Client

# -------------------------------
# 1. Application setup
# -------------------------------

st.set_page_config(
    page_title="AfyaTrack",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 AfyaTrack")
st.subheader("Community Health Client Registration and Follow-up Management")

st.caption("A simple tool for managing community health client records.")

# Create database if it does not exist
try:
    database.init_db()
except (sqlite3.Error, OSError) as error:
    st.error(f"Could not initialise the database: {error}")
    st.stop()


# -------------------------------
# 2. Input validation
# -------------------------------

def validate_client(name, age, residence):
    """Check that client information is valid."""

    if not name.strip():
        return "Please enter the client's name."

    if not re.fullmatch(r"[A-Za-zÀ-ÿ '\-]+", name.strip()):
        return "Name should contain letters, spaces, apostrophes or hyphens."

    if age < 0 or age > 120:
        return "Please enter an age between 0 and 120."

    if not residence.strip():
        return "Please enter the client's residence."

    return None


# -------------------------------
# 3. Retrieve client information
# -------------------------------

try:
    clients = database.get_all_clients()
    overdue_clients = database.get_overdue_clients(
        date.today().isoformat()
    )

except sqlite3.Error as error:
    st.error(f"Unable to retrieve records: {error}")
    st.stop()


# -------------------------------
# 4. Dashboard summary
# -------------------------------

total_clients = len(clients)

total_visits = sum(
    client["visit_count"] or 0 for client in clients
)

pending_followups = sum(
    1 for client in clients
    if client["followup_date"] and client["followup_done"] == 0
)

total_overdue = len(overdue_clients)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Registered Clients", total_clients)
col2.metric("Visits Recorded", total_visits)
col3.metric("Pending Follow-ups", pending_followups)
col4.metric("Overdue Follow-ups", total_overdue)

st.divider()


# -------------------------------
# 5. Application navigation
# -------------------------------

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Register Client",
        "View Clients",
        "Record Visit",
        "Manage Follow-ups",
        "Overdue Follow-ups",
        "Update / Delete Client",
        "Export Records"
    ]
)


# -------------------------------
# 6. Dashboard
# -------------------------------

if menu == "Dashboard":

    st.header("Dashboard Overview")

    st.write(
        "Welcome to AfyaTrack. Use the navigation menu "
        "to manage client records and follow-up activities."
    )

    if overdue_clients:
        st.warning(
            f"There are {total_overdue} overdue follow-up(s) "
            "requiring attention."
        )
    else:
        st.success("There are currently no overdue follow-ups.")

    st.subheader("Recently Registered Clients")

    if clients:
        df = pd.DataFrame(clients)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No clients have been registered yet.")


# -------------------------------
# 7. Register Client
# -------------------------------

elif menu == "Register Client":

    st.header("Register a New Client")

    with st.form("register_form"):

        name = st.text_input("Client Name")
        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=18
        )

        sex = st.selectbox(
            "Sex",
            ["Female", "Male", "Other"]
        )

        residence = st.text_input("Village / Residence")

        submitted = st.form_submit_button("Register Client")

        if submitted:

            error = validate_client(name, age, residence)

            if error:
                st.error(error)

            else:
                try:
                    new_client = Client(
                        name.strip(),
                        age,
                        sex,
                        residence.strip()
                    )

                    client_id = new_client.register()

                    st.success(
                        f"Client registered successfully! "
                        f"Client ID: {client_id}"
                    )

                except sqlite3.Error as error:
                    st.error(f"Could not register client: {error}")


# -------------------------------
# 8. View and Search Clients
# -------------------------------

elif menu == "View Clients":

    st.header("Registered Clients")

    search = st.text_input("Search by client name or ID")

    filtered_clients = [
        client for client in clients
        if search.lower() in client["name"].lower()
        or search == str(client["id"])
    ]

    if filtered_clients:
        st.dataframe(
            pd.DataFrame(filtered_clients),
            use_container_width=True
        )
    else:
        st.info("No matching client records found.")


# -------------------------------
# 9. Record a Community Health Visit
# -------------------------------

elif menu == "Record Visit":

    st.header("Record Community Health Visit")

    if not clients:
        st.info("Register a client before recording a visit.")

    else:
        client_options = {
            f'{c["id"]} - {c["name"]}': c["id"]
            for c in clients
        }

        with st.form("visit_form"):

            selected = st.selectbox(
                "Select Client",
                list(client_options.keys())
            )

            visit_date = st.date_input(
                "Visit Date",
                value=date.today(),
                max_value=date.today()
            )

            activity = st.text_area("Activity Conducted")

            submitted = st.form_submit_button("Save Visit")

            if submitted:

                if not activity.strip():
                    st.error("Please describe the activity conducted.")

                else:
                    try:
                        client = Client(
                            "", 0, "", "",
                            client_id=client_options[selected]
                        )

                        success = client.record_visit(
                            visit_date.isoformat(),
                            activity.strip()
                        )

                        if success:
                            st.success("Visit recorded successfully!")
                        else:
                            st.error("Client record was not found.")

                    except sqlite3.Error as error:
                        st.error(f"Could not record visit: {error}")


# -------------------------------
# 10. Manage Follow-ups
# -------------------------------

elif menu == "Manage Follow-ups":

    st.header("Schedule and Complete Follow-ups")

    if not clients:
        st.info("No clients available.")

    else:
        client_options = {
            f'{c["id"]} - {c["name"]}': c["id"]
            for c in clients
        }

        st.subheader("Schedule a Follow-up")

        with st.form("followup_form"):

            selected = st.selectbox(
                "Select Client",
                list(client_options.keys()),
                key="followup_client"
            )

            followup_date = st.date_input(
                "Follow-up Date",
                min_value=date.today()
            )

            submitted = st.form_submit_button("Schedule Follow-up")

            if submitted:

                try:
                    client = Client(
                        "", 0, "", "",
                        client_id=client_options[selected]
                    )

                    success = client.schedule_followup(
                        followup_date.isoformat()
                    )

                    if success:
                        st.success("Follow-up scheduled successfully!")
                    else:
                        st.error("Client record was not found.")

                except sqlite3.Error as error:
                    st.error(f"Could not schedule follow-up: {error}")

        st.divider()

        st.subheader("Mark Follow-up as Completed")

        pending = [
            c for c in clients
            if c["followup_date"] and c["followup_done"] == 0
        ]

        if pending:

            pending_options = {
                f'{c["id"]} - {c["name"]} ({c["followup_date"]})': c["id"]
                for c in pending
            }

            selected_pending = st.selectbox(
                "Select Follow-up",
                list(pending_options.keys())
            )

            if st.button("Mark as Completed"):

                try:
                    client = Client(
                        "", 0, "", "",
                        client_id=pending_options[selected_pending]
                    )

                    if client.complete_followup():
                        st.success("Follow-up marked as completed!")
                    else:
                        st.error("Could not update the follow-up.")

                except sqlite3.Error as error:
                    st.error(f"Could not update record: {error}")

        else:
            st.info("There are no pending follow-ups.")


# -------------------------------
# 11. Overdue Follow-ups
# -------------------------------

elif menu == "Overdue Follow-ups":

    st.header("Overdue Follow-ups")

    if overdue_clients:

        st.warning(
            f"{len(overdue_clients)} client(s) have overdue follow-ups."
        )

        st.dataframe(
            pd.DataFrame(overdue_clients),
            use_container_width=True
        )

    else:
        st.success("No overdue follow-ups at the moment.")


# -------------------------------
# 12. Update or Delete Client
# -------------------------------

elif menu == "Update / Delete Client":

    st.header("Update or Delete Client Records")

    if not clients:
        st.info("No client records available.")

    else:
        client_options = {
            f'{c["id"]} - {c["name"]}': c
            for c in clients
        }

        selected = st.selectbox(
            "Select Client",
            list(client_options.keys())
        )

        selected_client = client_options[selected]

        st.subheader("Update Client Information")

        with st.form("update_form"):

            name = st.text_input(
                "Client Name",
                value=selected_client["name"]
            )

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=selected_client["age"] or 0
            )

            sex = st.selectbox(
                "Sex",
                ["Female", "Male", "Other"],
                index=["Female", "Male", "Other"].index(
                    selected_client["sex"]
                    if selected_client["sex"] in ["Female", "Male", "Other"]
                    else "Other"
                )
            )

            residence = st.text_input(
                "Residence",
                value=selected_client["residence"] or ""
            )

            submitted = st.form_submit_button("Update Client")

            if submitted:

                error = validate_client(name, age, residence)

                if error:
                    st.error(error)

                else:
                    try:
                        client = Client(
                            name.strip(),
                            age,
                            sex,
                            residence.strip(),
                            client_id=selected_client["id"]
                        )

                        if client.update():
                            st.success("Client updated successfully!")
                        else:
                            st.error("Client record was not found.")

                    except sqlite3.Error as error:
                        st.error(f"Could not update client: {error}")

        st.divider()

        st.subheader("Delete Client")

        confirm_delete = st.checkbox(
            f"I confirm that I want to delete {selected_client['name']}'s record."
        )

        if st.button("Delete Client", type="primary"):

            if not confirm_delete:
                st.warning("Please confirm before deleting the record.")

            else:
                try:
                    client = Client(
                        "", 0, "", "",
                        client_id=selected_client["id"]
                    )

                    if client.delete():
                        st.success("Client deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Client record was not found.")

                except sqlite3.Error as error:
                    st.error(f"Could not delete client: {error}")


# -------------------------------
# 13. Export Records to CSV
# -------------------------------

elif menu == "Export Records":

    st.header("Export Client Records")

    if clients:

        df = pd.DataFrame(clients)

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Client Records (CSV)",
            data=csv_data,
            file_name="afya_track_clients.csv",
            mime="text/csv"
        )

        st.success("Your client records are ready for export.")

    else:
        st.info("There are no records to export.")





