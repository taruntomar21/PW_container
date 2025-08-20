import os
import base64
import fitz  # PyMuPDF
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

# Optional (for big-PDF viewing). App will still work if these aren't installed.
try:
    import fitz  # PyMuPDF
    from PIL import Image
    HAS_FITZ = True
except Exception:
    HAS_FITZ = False

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="📚 PDF Library", layout="wide")
BASE_DIR = "pdfs"

# Define your sections (folder names on disk)
SECTIONS = {
    "Current Affairs": "Current Affairs",
    "Static GK" : "Static GK",
    "Geography" : "Geography",
    "History": "History",
    "Advanced Maths": "Advanced Maths",
    "Arithmatic Maths": "Arithmatic Maths",
    "Science": "Science",
    "Polity" : "Polity",
    "Computer" : "Computer",
    "English" : "English",
    "Reasoning" : "Reasoning",
    "Economics" : "Economics"
}

# Ensure folders exist
for folder in SECTIONS.values():
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

# Session state
if "selected_section" not in st.session_state:
    st.session_state.selected_section = None
if "selected_pdf" not in st.session_state:
    st.session_state.selected_pdf = None

# -----------------------------
# Helpers
# -----------------------------
def list_pdfs(folder_path: str):
    try:
        return sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")])
    except FileNotFoundError:
        return []


def render_pdf_viewer(pdf_path: str):
    """Page-by-page viewer using PyMuPDF"""
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    st.subheader(f"Total Pages: {total_pages}")
    page_num = st.number_input("Go to Page", 1, total_pages, 1)

    page = doc[page_num - 1]
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    st.image(img, use_column_width=True)


def show_section_ui(section_label: str):
    """UI for a selected section"""
    section_folder = os.path.join(BASE_DIR, SECTIONS[section_label])

    st.header(f"📂 {section_label}")
    # Back button
    if st.button("⬅️ Back to Sections"):
        st.session_state.selected_section = None
        st.session_state.selected_pdf = None
        st.rerun()

    # Upload
    st.subheader("Upload a new PDF")
    uploaded = st.file_uploader(f"Upload to {section_label}", type="pdf", key=f"uploader_{section_label}")
    if uploaded is not None:
        save_path = os.path.join(section_folder, uploaded.name)
        with open(save_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"✅ `{uploaded.name}` uploaded to {section_label}")
        st.session_state.selected_pdf = uploaded.name  # auto-select

    # List PDFs
    st.subheader("Your PDFs")
    pdf_files = list_pdfs(section_folder)

    if not pdf_files:
        st.info("No PDFs in this section yet. Upload one above.")
        return

    # Select PDF
    selected_pdf = st.selectbox("Choose a PDF to view", pdf_files, key=f"select_{section_label}")
    st.session_state.selected_pdf = selected_pdf
    pdf_path = os.path.join(section_folder, selected_pdf)

    # Download
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Download PDF", f, file_name=selected_pdf, mime="application/pdf", key=f"dl_{section_label}")

    # Render PDF Page by Page
    st.divider()
    render_pdf_viewer(pdf_path)
    st.divider()

    # (Optional) Delete button — comment out if you don’t want deletion
    with st.expander("Danger Zone"):
        if st.button("🗑️ Delete this PDF"):
            try:
                os.remove(selected_pdf)
                st.success(f"Deleted `{selected_pdf}`")
                st.session_state.selected_pdf = None
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete: {e}")

# -----------------------------
# UI
# -----------------------------
st.title("📚 Best Teachers Notes — PDF Library")

# If no section chosen → show buttons grid
if not st.session_state.selected_section:
    st.subheader("Choose a Section")
    section_labels = list(SECTIONS.keys())

    # Create a neat button grid (3 per row)
    n_cols = 3
    rows = (len(section_labels) + n_cols - 1) // n_cols
    idx = 0
    for _ in range(rows):
        cols = st.columns(n_cols)
        for c in cols:
            if idx < len(section_labels):
                label = section_labels[idx]
                if c.button(label, use_container_width=True):
                    st.session_state.selected_section = label
                    st.rerun()
                idx += 1
else:
    # Show selected section UI
    show_section_ui(st.session_state.selected_section)