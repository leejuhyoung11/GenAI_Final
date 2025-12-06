import os, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DATA_DIR = os.path.join(ROOT_DIR, "data")

from src.graph.matching_workflow import workflow
from src.graph.resume_workflow import run_resume_ingestion
import streamlit as st
import json


st.set_page_config(layout="wide")


# ================== SIDEBAR STYLE =====================
st.markdown("""
    <style>
       
        [data-testid="stSidebar"] {
            background-color: #f5f7fa;
        }

        /* 사이드바 제목 */
        .sidebar-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 16px;
            color: #0f172a;
        }

        /* 라디오 그룹을 세로로 꽉 차게 */
        [data-testid="stSidebar"] div[role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 0px;
        }

        /* 각 항목(label)을 버튼처럼 보이게 */
        [data-testid="stSidebar"] div[role="radiogroup"] > label {
            width: 100%;
            padding: 12px 16px;
            margin-bottom: 4px;
            border-radius: 8px;
            background-color: #e2e8f0;
            color: #1e293b;
            font-size: 18px;
            font-weight: 500;
            cursor: pointer;
        }

        /* hover 효과 */
        [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: #cbd5e1;
        }

        /* 동그란 라디오 아이콘 숨기기 */
        [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
            display: none;
        }

        /* 선택된 메뉴 강조 (Streamlit 버전에 따라 data-selected, aria-checked 등 달라질 수 있음) */
        [data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] {
            background-color: #1e40af !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# ================== SIDEBAR LOGIC =====================

menu_items = [
    "🏷 Add Resume",
    "📁 Employee List",
    "📦 Project List",
    "🤖 Analyze Project",
]

with st.sidebar:
    st.markdown('<div class="sidebar-title">TalentMatch AI</div>', unsafe_allow_html=True)

    # 첫 실행 시 기본 메뉴 설정
    if "menu" not in st.session_state:
        st.session_state.menu = menu_items[0]

    # radio 
    menu = st.radio(
        "Menu",
        options=menu_items,
        label_visibility="collapsed",
        key="menu",   # st.session_state["menu"]에 저장됨
    )

# ================== MAIN AREA =========================

st.title("TalentMatch AI Dashboard")

# 여기서 menu 값은 st.session_state.menu 와 동일
if menu == "🏷 Add Resume":
    st.subheader("Upload Resume(s) (PDF)")

    uploaded_files = st.file_uploader(
        "Upload up to 3 PDF resumes",
        type=["pdf"],
        accept_multiple_files=True,
        key="add_resume_uploader",   # unique key
    )

    if uploaded_files:
        st.info(f"{len(uploaded_files)} file(s) selected. Only the first 3 will be processed.")

        if st.button("Process Resumes", key="process_resume_btn"):
            results = []

            with st.spinner("Processing resumes with agents (extraction + validation + save)..."):
                # Hard cap at 3 resumes per run
                for f in uploaded_files[:3]:
                    file_bytes = f.getvalue()
                    final_state = run_resume_ingestion(file_bytes)
                    results.append((f.name, final_state))

            st.success(f"✅ Processed {len(results)} resume(s) and appended to `data/employees.json`")

            for filename, state in results:
                st.markdown(f"**{filename}** → Parsed profile:")
                st.json(state.get("parsed_employee_json"))

elif menu == "📁 Employee List":
    st.subheader("Employee List")

    emp_path = os.path.join(DATA_DIR, "employees.json")
    if os.path.exists(emp_path):
        with open(emp_path, "r", encoding="utf-8") as f:
            employees = json.load(f)

        if not employees:
            st.info("Employee store is empty. Try adding a resume first.")
        else:
            rows = []
            for e in employees:
                rows.append(
                    {
                        "ID": e.get("id"),
                        "Name": e.get("name"),
                        "Role": e.get("role"),
                        "Seniority": e.get("seniority"),
                        "Availability": e.get("availability"),
                        "Source": e.get("source", "internal"),
                    }
                )
            st.dataframe(rows, use_container_width=True)
    else:
        st.info("No employees found. `data/employees.json` does not exist yet.")


elif menu == "📦 Project List":

    st.subheader("Projects")

    PROJ_PATH = os.path.join("data", "projects.json")
    if os.path.exists(PROJ_PATH):
        with open(PROJ_PATH, "r", encoding="utf-8") as f:
            projects = json.load(f)

        project_names = [p["project_name"] for p in projects]
        selected_project_name = st.selectbox("Select project", project_names)

        project_obj = next(p for p in projects if p["project_name"] == selected_project_name)
        project_id = project_obj["project_id"]

        # --- 분석 결과 있는 경우 ---
        if (
            "analysis_result" in st.session_state
            and project_id in st.session_state["analysis_result"]
        ):
            st.success("Analysis Result Found!")
            result = st.session_state["analysis_result"][project_id]

            st.header("Role-based Result Viewer")
            roles = [r["role_name"] for r in result["roles"]]
            selected_role = st.selectbox("Select Role", roles)

            role_data = next(r for r in result["roles"] if r["role_name"] == selected_role)
            candidates = role_data["candidates"]

            st.subheader(f"Candidates for {selected_role}")

            table_rows = [
                {
                    "Employee": c["name"],
                    "Final Score": c["final_score"],
                    "Domain Score": c.get("per_matcher", {}).get("domain", {}).get("score", 0),
                    "Skill Score": c.get("per_matcher", {}).get("skill", {}).get("score", 0),
                    "Experience Year": c["experience_years"],
                }
                for c in candidates
            ]

            st.dataframe(table_rows, use_container_width=True)

            # 상세 정보
            st.subheader("Candidate Details")
            selected_employee = st.selectbox("Select Employee", [c["name"] for c in candidates])
            person = next(c for c in candidates if c["name"] == selected_employee)

            st.markdown(f"### 📌 {selected_employee}")

            st.subheader("Matcher Breakdown")
            for matcher_name, matcher_info in person["per_matcher"].items():
                with st.expander(f"🔹 {matcher_name}"):
                    st.write("Score:", matcher_info.get("score", 0))
                    st.write("Reason:", matcher_info.get("reason", ""))

        else:
            st.info("No analysis result stored for this project yet.")

    else:
        st.info("No projects yet.")


elif menu == "🤖 Analyze Project":

    st.subheader("Analyze Project")

    PROJ_PATH = os.path.join("data", "projects.json")
    if not os.path.exists(PROJ_PATH):
        st.warning("No project file.")
    else:
        with open(PROJ_PATH, "r", encoding="utf-8") as f:
            projects = json.load(f)

        selected_name = st.selectbox("Select project", [p["project_name"] for p in projects])
        requirement_text = st.text_area("Describe what kind of team you want:")

        if st.button("Start Analysis"):

            # employee load
            EMP_PATH = os.path.join("data", "employees.json")
            with open(EMP_PATH, "r", encoding="utf-8") as f:
                employees = json.load(f)

            selected_project = next(p for p in projects if p["project_name"] == selected_name)

            # store project in session
            st.session_state["selected_project"] = selected_project

            # INITIAL STATE
            state = {
                "requirement_text": requirement_text,
                "project": selected_project,
                "employees": employees,
                "router_config": {},
                "role_scores": [],
                "final_result": {}
            }

            OUTPUT_PATH = f"output/{selected_project['project_id']}.json"

            if os.path.exists(OUTPUT_PATH):
                os.remove(OUTPUT_PATH)

            # RUN WORKFLOW
            with st.spinner("Analyzing..."):
                workflow.invoke(state)

                # wait for file
                import time
                for _ in range(100):
                    if os.path.exists(OUTPUT_PATH):
                        break
                    time.sleep(0.3)

            # save to session
            if "analysis_result" not in st.session_state:
                st.session_state["analysis_result"] = {}

            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                st.session_state["analysis_result"][selected_project["project_id"]] = json.load(f)

            st.success("Analysis complete!")

    # ---- SHOW RESULT IF PROJECT EXISTS IN SESSION ----
    if "selected_project" in st.session_state:
        proj = st.session_state["selected_project"]
        pid = proj["project_id"]

        if "analysis_result" in st.session_state and pid in st.session_state["analysis_result"]:
            result = st.session_state["analysis_result"][pid]

            st.header("Role-based Result Viewer")
            roles = [r["role_name"] for r in result["roles"]]
            selected_role = st.selectbox("Select Role", roles)

            role_data = next(r for r in result["roles"] if r["role_name"] == selected_role)
            candidates = role_data["candidates"]

            table_rows = [
                {
                    "Employee": c["name"],
                    "Final Score": c["final_score"],
                    "Domain Score": c.get("per_matcher", {}).get("domain", {}).get("score", 0),
                    "Skill Score": c.get("per_matcher", {}).get("skill", {}).get("score", 0),
                    "Experience Year": c["experience_years"],
                }
                for c in candidates
            ]

            st.dataframe(table_rows, use_container_width=True)