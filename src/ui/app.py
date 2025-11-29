from src.graph.matching_workflow import workflow
import streamlit as st
import json
import os, sys

st.set_page_config(layout="wide")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ================== SIDEBAR STYLE =====================
st.markdown("""
    <style>
        /* 사이드바 배경 */
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
    PROJ_PATH = os.path.join(ROOT_DIR, "src", "data", "projects.json")
    if os.path.exists(PROJ_PATH):
        with open(PROJ_PATH, "r", encoding="utf-8") as f:
            projects = json.load(f)
        st.table([p["name"] for p in projects])
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
        selected = st.selectbox("Select project", [p["name"] for p in projects])
        if st.button("Start Analysis"):
            st.write("Start")
            
            # Load employee data
            EMP_PATH = os.path.join("data", "employees.json")
            with open(EMP_PATH, "r", encoding="utf-8") as f:
                employees = json.load(f)

            requirement_text = st.text_area("Describe what kind of team you want:")
            
            # Initialize State
            state = {
                "requirement_text": "",
                "project": selected,
                "employees": employees,
                "partial_scores": {},
                "final_result": {}
            }

            result = workflow.invoke(state)

            st.json(result)