
import streamlit as st
import heapq
import itertools

# --------------------------------
# DATA STRUCTURE 1: NORMAL QUEUE
# FIFO - First In First Out
# --------------------------------
class PatientQueue:
    def __init__(self):
        self.items = []

    def enqueue(self, patient):
        self.items.append(patient)

    def dequeue(self):
        if self.items:
            return self.items.pop(0)
        return None

    def get_all(self):
        return self.items.copy()


# --------------------------------
# DATA STRUCTURE 2: PRIORITY QUEUE
# Emergency patients get priority
# --------------------------------
class EmergencyQueue:
    def __init__(self):
        self.items = []
        self.counter = itertools.count()

    def enqueue(self, patient):
        heapq.heappush(
            self.items,
            (next(self.counter), patient)
        )

    def dequeue(self):
        if self.items:
            return heapq.heappop(self.items)[1]
        return None

    def get_all(self):
        return [item[1] for item in sorted(self.items)]


# --------------------------------
# DATA STRUCTURE 3: LINKED LIST
# Stores served patient history
# --------------------------------
class Node:
    def __init__(self, patient):
        self.patient = patient
        self.next = None


class PatientHistory:
    def __init__(self):
        self.head = None

    def add(self, patient):
        new_node = Node(patient)

        if self.head is None:
            self.head = new_node
            return

        current = self.head

        while current.next:
            current = current.next

        current.next = new_node

    def get_all(self):
        result = []
        current = self.head

        while current:
            result.append(current.patient)
            current = current.next

        return result


# --------------------------------
# STREAMLIT PAGE CONFIGURATION
# --------------------------------
st.set_page_config(
    page_title="Hospital Queue Management",
    page_icon="🏥",
    layout="centered"
)

st.title("🏥 Hospital Queue Management System")
st.caption("SPPU Data Structures Mini Project")
st.divider()


# --------------------------------
# INITIALIZE APPLICATION DATA
# --------------------------------
if "normal_queue" not in st.session_state:
    st.session_state.normal_queue = PatientQueue()

if "emergency_queue" not in st.session_state:
    st.session_state.emergency_queue = EmergencyQueue()

if "history" not in st.session_state:
    st.session_state.history = PatientHistory()

if "next_token" not in st.session_state:
    st.session_state.next_token = 1

if "message" not in st.session_state:
    st.session_state.message = ""


normal = st.session_state.normal_queue
emergency = st.session_state.emergency_queue
history = st.session_state.history

waiting = emergency.get_all() + normal.get_all()
served = history.get_all()


# --------------------------------
# DASHBOARD
# --------------------------------
st.subheader("📊 Hospital Dashboard")

c1, c2 = st.columns(2)

c1.metric("Total Registered", len(waiting) + len(served))
c2.metric("Waiting Patients", len(waiting))

c3, c4 = st.columns(2)

c3.metric("Patients Served", len(served))
c4.metric("Emergency Waiting", len(emergency.get_all()))

st.divider()


# --------------------------------
# PATIENT REGISTRATION
# --------------------------------
st.subheader("➕ Patient Registration")

with st.form("registration_form"):
    name = st.text_input("Patient Name")
    age = st.number_input("Patient Age", min_value=1, max_value=120, value=18)
    symptoms = st.text_input("Symptoms")

    category = st.selectbox(
        "Patient Category",
        ["Normal", "Emergency"]
    )

    register = st.form_submit_button(
        "Generate Token & Register",
        use_container_width=True
    )

    if register:
        if not name.strip() or not symptoms.strip():
            st.error("Please enter patient name and symptoms.")

        else:
            patient = {
                "token": st.session_state.next_token,
                "name": name.strip(),
                "age": age,
                "symptoms": symptoms.strip(),
                "category": category
            }

            if category == "Emergency":
                emergency.enqueue(patient)
            else:
                normal.enqueue(patient)

            st.session_state.next_token += 1

            st.session_state.message = (
                f"Patient registered successfully! "
                f"Token: {patient['token']}"
            )


if st.session_state.message:
    st.success(st.session_state.message)


st.divider()


# --------------------------------
# WAITING PATIENT QUEUE
# --------------------------------
st.subheader("👥 Waiting Patient Queue")

waiting = emergency.get_all() + normal.get_all()

if waiting:
    for patient in waiting:
        st.write(
            f"**Token #{patient['token']}** | "
            f"{patient['name']} | "
            f"Age: {patient['age']} | "
            f"{patient['category']}"
        )
        st.caption(f"Symptoms: {patient['symptoms']}")
else:
    st.info("No patients are waiting.")


# --------------------------------
# SERVE NEXT PATIENT
# --------------------------------
st.subheader("🩺 Serve Next Patient")

if st.button("Serve Next Patient", use_container_width=True):

    patient = emergency.dequeue()

    if patient is None:
        patient = normal.dequeue()

    if patient:
        history.add(patient)
        st.success(
            f"Now serving Token #{patient['token']} - "
            f"{patient['name']}"
        )
    else:
        st.warning("No patients are waiting.")

st.divider()


# --------------------------------
# SEARCH PATIENT BY TOKEN
# --------------------------------
st.subheader("🔍 Search Patient")

search_token = st.number_input(
    "Enter Patient Token Number",
    min_value=1,
    step=1,
    value=1
)

if st.button("Search Patient", use_container_width=True):

    all_patients = (
        emergency.get_all()
        + normal.get_all()
        + history.get_all()
    )

    found = None

    for patient in all_patients:
        if patient["token"] == search_token:
            found = patient
            break

    if found:
        st.success("Patient found!")

        st.write(f"Name: {found['name']}")
        st.write(f"Token: {found['token']}")
        st.write(f"Age: {found['age']}")
        st.write(f"Symptoms: {found['symptoms']}")
        st.write(f"Category: {found['category']}")

        if found in history.get_all():
            st.write("Status: Served")
        else:
            st.write("Status: Waiting")

    else:
        st.error("Patient not found.")


st.divider()


# --------------------------------
# SERVED PATIENT HISTORY
# --------------------------------
st.subheader("📋 Served Patient History")

served = history.get_all()

if served:
    for patient in served:
        st.write(
            f"Token #{patient['token']} - "
            f"{patient['name']} - "
            f"{patient['category']}"
        )
else:
    st.info("No served patient history available.")


st.divider()


# --------------------------------
# DEMO AND RESET OPTIONS
# --------------------------------
st.subheader("⚙️ Project Controls")

if st.button("Add Demo Patients"):
    demo_patients = [
        {
            "name": "Rahul",
            "age": 19,
            "symptoms": "Fever",
            "category": "Normal"
        },
        {
            "name": "Priya",
            "age": 25,
            "symptoms": "Headache",
            "category": "Normal"
        },
        {
            "name": "Amit",
            "age": 40,
            "symptoms": "Injury",
            "category": "Emergency"
        }
    ]

    for data in demo_patients:
        patient = {
            "token": st.session_state.next_token,
            **data
        }

        if patient["category"] == "Emergency":
            emergency.enqueue(patient)
        else:
            normal.enqueue(patient)

        st.session_state.next_token += 1

    st.success("Demo patients added successfully!")


if st.button("Clear All Data"):
    st.session_state.normal_queue = PatientQueue()
    st.session_state.emergency_queue = EmergencyQueue()
    st.session_state.history = PatientHistory()
    st.session_state.next_token = 1
    st.session_state.message = ""

    st.rerun()


st.divider()
st.caption(
    "Hospital Queue Management System | "
    "Python Data Structures Project"
)
st.caption(
    "Educational demonstration only. "
    "Not intended for real clinical use."
)
