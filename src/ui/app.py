import os, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.graph.matching_workflow import workflow
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

    # radio 자체에 key를 두고 state는 Streamlit에게 맡김
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
    st.subheader("Upload Resume (PDF)")
    uploaded = st.file_uploader("Upload PDF resume", type=["pdf"])
    if uploaded:
        st.success("Resume uploaded!")
        # TODO: resume 처리 워크플로우 연결

elif menu == "📁 Employee List":
    st.subheader("Employee List")
    EMP_PATH = os.path.join(ROOT_DIR, "src", "data", "employees.json")
    if os.path.exists(EMP_PATH):
        with open(EMP_PATH, "r", encoding="utf-8") as f:
            employees = json.load(f)
        st.table([e["name"] for e in employees])
    else:
        st.info("No employees found.")

elif menu == "📦 Project List":

    st.subheader("Projects")

    PROJ_PATH = os.path.join("data", "projects.json")
    if os.path.exists(PROJ_PATH):
        with open(PROJ_PATH, "r", encoding="utf-8") as f:
            projects = json.load(f)

        # 프로젝트 이름 리스트
        project_names = [p["project_name"] for p in projects]

        # 프로젝트 선택 UI
        selected_project_name = st.selectbox("Select project", project_names)

        # 전체 프로젝트 dict 가져오기
        project_obj = next(p for p in projects if p["project_name"] == selected_project_name)
        project_id = project_obj["project_id"]

    

        # -----------------------------------------
        if (
            "analysis_result" in st.session_state
            and project_id in st.session_state["analysis_result"]
        ):
            st.success("Analysis Result Found!")

            result = st.session_state["analysis_result"][project_id]

            # -----------------------------------------
            # ROLE VIEWER
            # -----------------------------------------
            st.header("Role-based Result Viewer")

            roles = [r["role_name"] for r in result["roles"]]
            selected_role = st.selectbox("Select Role", roles)

            role_data = next(r for r in result["roles"] if r["role_name"] == selected_role)
            candidates = role_data["candidates"]

            # 표 영역
            st.subheader(f"Candidates for {selected_role}")

            table_rows = [
                {
                    "Employee": c["name"],
                    "Final Score": c["final_score"],
                    "Domain Score": c["per_matcher"]["domain"]["score"],
                    "Skill Score": c["per_matcher"]["skill"]["score"],
                    "Experience": c["experience_years"],
                }
                for c in candidates
            ]

            st.dataframe(table_rows, use_container_width=True)

            # 상세 정보
            st.subheader("Candidate Details")
            selected_employee = st.selectbox(
                "Select Employee",
                [c["name"] for c in candidates]
            )
            person = next(c for c in candidates if c["name"] == selected_employee)

            st.markdown(f"### 📌 {selected_employee}")
            st.write(f"**Experience:** {person['experience_years']} years")
            st.write(f"**Final Score:** {person['final_score']}")
            st.write(f"**Note Score:** {person['note_score']}")

            st.subheader("Matcher Breakdown")
            for matcher_name, matcher_info in person["per_matcher"].items():
                with st.expander(f"🔹 {matcher_name}"):
                    st.write("Score:", matcher_info["score"])
                    st.write("Reason:", matcher_info["reason"])

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
        selected = st.selectbox("Select project", [p["project_name"] for p in projects])
        requirement_text = st.text_area("Describe what kind of team you want:")
        
        if st.button("Start Analysis"):
            # Load employee data
            EMP_PATH = os.path.join("data", "employees.json")
            with open(EMP_PATH, "r", encoding="utf-8") as f:
                employees = json.load(f)

            selected_project = next(
                p for p in projects if p["project_name"] == selected
            )

            # Initialize State
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

            # ------------------------------
            # RUN WORKFLOW WITH LOADING SPINNER
            # ------------------------------
            with st.spinner("Analyzing..."):
                result = workflow.invoke(state)

                # Wait for output file
                import time
                timeout = 30
                waited = 0
                while not os.path.exists(OUTPUT_PATH) and waited < timeout:
                    time.sleep(0.3)
                    waited += 0.3

                if not os.path.exists(OUTPUT_PATH):
                    st.error("Analysis failed: output file not created.")
                    st.stop()

            if "analysis_result" not in st.session_state:
                st.session_state["analysis_result"] = {}
          

            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                st.session_state["analysis_result"][selected_project["project_id"]] = json.load(f)

            st.success("Analysis complete!")

        # ----------------------
        # SHOW UI AFTER ANALYSIS
        # ----------------------
        if "analysis_result" in st.session_state and "selected_project" in st.session_state:
            result = st.session_state["analysis_result"][selected_project["project_id"]]

            st.header("Role-based Result Viewer")

            roles = [r["role_name"] for r in result["roles"]]
            selected_role = st.selectbox("Select Role", roles)

            role_data = next(r for r in result["roles"] if r["role_name"] == selected_role)
            candidates = role_data["candidates"]

            st.subheader(f"Candidates for {selected_role}")

            print(candidates[0])

            table_rows = [
                {
                    "Employee": c["name"],
                    "Final Score": c["final_score"],
                    "Domain Score": c["per_matcher"]["domain"]['score'],
                    "Skill Score": c["per_matcher"]["skill"]['score'],
                    "Experience Year": c["experience_years"],
                }
                for c in candidates
            ]

            st.dataframe(table_rows, use_container_width=True)

            # Candidate Detail
            st.subheader("Candidate Details")
            selected_employee = st.selectbox("Select Employee", [c["name"] for c in candidates])
            person = next(c for c in candidates if c["name"] == selected_employee)

            st.markdown(f"### 📌 {selected_employee}")
            # st.write(f"**Experience:** {person['experience_years']} years")
            # st.write(f"**Final Score:** {person['final_score']}")
            # st.write(f"**Note Score:** {person['note_score']}")

            st.subheader("Matcher Breakdown")
            for k, v in person["per_matcher"].items():
                with st.expander(f"🔹 {k}"):
                    st.write("Score:", v["score"])
                    st.write("Reason:", v["reason"])