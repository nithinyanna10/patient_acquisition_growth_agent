import sys
from pathlib import Path

# Ensure project root is on sys.path regardless of how Streamlit is invoked
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

import ui.checklist as checklist_page
import ui.milestones as milestones_page
import ui.overview as overview_page
import ui.post_launch_dashboard as post_launch_page
import ui.raid_dashboard as raid_page
import ui.scenario_simulator as simulator_page
import ui.status_generator as status_page
import ui.workstreams as workstreams_page
from models.checklist import ChecklistItem
from models.milestone import Milestone
from models.raid import RAIDItem
from models.workstream import Workstream
from scoring.readiness import compute_readiness
from utils.helpers import load_data

st.set_page_config(
    page_title="Launch Control — Patient Acquisition Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "Executive Overview": overview_page,
    "Workstream Health": workstreams_page,
    "Milestone Tracker": milestones_page,
    "RAID Dashboard": raid_page,
    "Go / No-Go Checklist": checklist_page,
    "Status Update Generator": status_page,
    "Scenario Simulator": simulator_page,
    "── Post-Launch ──": None,
    "Post-Launch Dashboard": post_launch_page,
}


@st.cache_data
def load_all():
    workstreams = [Workstream(**item) for item in load_data("data/workstreams.json")]
    milestones = [Milestone(**item) for item in load_data("data/milestones.json")]
    raid_items = [RAIDItem(**item) for item in load_data("data/raid.json")]
    checklist = [ChecklistItem(**item) for item in load_data("data/checklist.json")]
    history = load_data("data/history.json")
    return workstreams, milestones, raid_items, checklist, history


def main() -> None:
    st.sidebar.title("🏥 Launch Control")
    st.sidebar.caption("Patient Acquisition & Growth Agent")
    st.sidebar.caption("Meridian Health System · Week 4 / 8")
    st.sidebar.divider()

    page_name = st.sidebar.radio("Navigate", list(PAGES.keys()))
    st.sidebar.divider()
    st.sidebar.caption(
        "Score formula: Workstream Health (30%) + Milestone Completion (25%) "
        "+ RAID Risk (20%) + Go/No-Go (25%)"
    )

    workstreams, milestones, raid_items, checklist, history = load_all()
    readiness = compute_readiness(workstreams, milestones, raid_items, checklist)

    page = PAGES[page_name]

    if page_name == "Executive Overview":
        page.render(workstreams, milestones, raid_items, checklist, readiness, history)
    elif page_name == "Workstream Health":
        page.render(workstreams)
    elif page_name == "Milestone Tracker":
        page.render(milestones)
    elif page_name == "RAID Dashboard":
        page.render(raid_items)
    elif page_name == "Go / No-Go Checklist":
        page.render(checklist)
    elif page_name == "Status Update Generator":
        page.render(workstreams, milestones, raid_items, checklist, readiness)
    elif page_name == "Scenario Simulator":
        page.render(workstreams, milestones, raid_items, checklist)
    elif page_name == "Post-Launch Dashboard":
        page.render()
    elif page == None:
        st.info("Select a page from the sidebar.")


if __name__ == "__main__":
    main()
