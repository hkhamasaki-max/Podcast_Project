from __future__ import annotations

import io
from typing import Any

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


DEFAULT_COLUMNS = [
    "program_id",
    "status",
    "program_type",
    "source_keywords",
    "external_concepts",
    "title",
    "summary",
    "goal",
    "concepts",
    "small_experiment",
    "user_note",
    "favorite",
]

DISPLAY_FIELDS = [
    ("summary", "summary"),
    ("goal", "goal"),
    ("concepts", "concepts"),
    ("small_experiment", "small_experiment"),
    ("source_keywords", "source_keywords"),
    ("external_concepts", "external_concepts"),
    ("status", "status"),
]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


st.set_page_config(
    page_title="Program Card Viewer",
    page_icon="□",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def css() -> None:
    st.markdown(
        """
        <style>
        :root {
          --bg: #f7f7f4;
          --surface: #ffffff;
          --surface-soft: #f0f3f1;
          --ink: #202622;
          --muted: #6c746d;
          --line: #d9ded8;
          --accent: #176b5c;
          --accent-strong: #0f4c42;
          --favorite: #b06a00;
        }

        .stApp {
          background: var(--bg);
          color: var(--ink);
        }

        .block-container {
          max-width: 1040px;
          padding-top: 1.3rem;
          padding-bottom: 2.5rem;
        }

        h1, h2, h3, p {
          letter-spacing: 0;
        }

        .topline {
          color: var(--accent);
          font-size: 0.8rem;
          font-weight: 800;
          text-transform: uppercase;
          margin-bottom: 0.1rem;
        }

        .card {
          border: 1px solid var(--line);
          border-radius: 8px;
          background: var(--surface);
          box-shadow: 0 16px 40px rgba(26, 38, 32, 0.08);
          overflow: hidden;
          margin-top: 0.8rem;
        }

        .card-head {
          display: flex;
          justify-content: space-between;
          gap: 1rem;
          padding: 1.4rem;
          border-bottom: 1px solid var(--line);
          background: linear-gradient(180deg, #ffffff, #f5f7f5);
        }

        .meta-line {
          color: var(--muted);
          font-size: 0.92rem;
          line-height: 1.45;
          margin-bottom: 0.65rem;
        }

        .record-id {
          border: 1px solid var(--line);
          border-radius: 999px;
          background: var(--surface);
          color: var(--muted);
          padding: 0.42rem 0.75rem;
          white-space: nowrap;
          height: fit-content;
        }

        .section-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 1px;
          background: var(--line);
        }

        .data-section {
          min-height: 110px;
          background: var(--surface);
          padding: 1rem;
        }

        .data-section.wide {
          grid-column: 1 / -1;
        }

        .section-label {
          color: var(--accent-strong);
          font-size: 0.86rem;
          font-weight: 800;
          margin-bottom: 0.55rem;
        }

        .section-body {
          color: var(--ink);
          line-height: 1.75;
          white-space: pre-wrap;
          overflow-wrap: anywhere;
        }

        .muted {
          color: var(--muted);
        }

        .note-panel {
          border: 1px solid var(--line);
          border-radius: 8px;
          background: var(--surface);
          padding: 1rem;
          margin-top: 0.8rem;
        }

        div[data-testid="stButton"] button {
          border-radius: 8px;
        }

        @media (max-width: 720px) {
          .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
          }

          .card-head {
            display: block;
            padding: 1rem;
          }

          .record-id {
            display: inline-block;
            margin-top: 0.8rem;
          }

          .section-grid {
            grid-template-columns: 1fr;
          }

          .data-section {
            min-height: auto;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def secret_value(section: str, key: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(section, {}).get(key, default))
    except Exception:
        return default


@st.cache_resource(show_spinner=False)
def get_worksheet():
    spreadsheet_id = secret_value("google_sheets", "spreadsheet_id")
    worksheet_name = secret_value("google_sheets", "worksheet_name", "シート1")
    service_account_info = dict(st.secrets["google_service_account"])
    credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(spreadsheet_id)
    return spreadsheet.worksheet(worksheet_name)


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    return text in {"true", "1", "yes", "on", "checked", "✓"}


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(column).strip() for column in df.columns]
    for column in DEFAULT_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    ordered = [column for column in DEFAULT_COLUMNS if column in df.columns]
    ordered += [column for column in df.columns if column not in ordered]
    df = df[ordered].fillna("")
    df["favorite"] = df["favorite"].map(normalize_bool)
    df["user_note"] = df["user_note"].astype(str)
    return df


def sheet_cell_value(value: Any) -> Any:
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if hasattr(value, "item"):
        return value.item()
    return value


def read_sheet() -> pd.DataFrame:
    worksheet = get_worksheet()
    rows = worksheet.get_all_records()
    if not rows:
        return pd.DataFrame(columns=DEFAULT_COLUMNS)
    return clean_dataframe(pd.DataFrame(rows))


def replace_sheet(df: pd.DataFrame) -> None:
    worksheet = get_worksheet()
    df = clean_dataframe(df)
    values = [[sheet_cell_value(value) for value in row] for row in df.values.tolist()]
    worksheet.clear()
    worksheet.update([df.columns.tolist()] + values, value_input_option="USER_ENTERED")
    st.cache_data.clear()


def update_cell(row_number: int, column_name: str, value: Any) -> None:
    worksheet = get_worksheet()
    headers = worksheet.row_values(1)
    if column_name not in headers:
        worksheet.update_cell(1, len(headers) + 1, column_name)
        headers.append(column_name)
    column_number = headers.index(column_name) + 1
    worksheet.update_cell(row_number, column_number, value)


@st.cache_data(ttl=20, show_spinner=False)
def cached_read_sheet() -> pd.DataFrame:
    return read_sheet()


def html_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_card(record: pd.Series) -> None:
    program_type = html_escape(record.get("program_type", ""))
    keywords = html_escape(record.get("source_keywords", ""))
    title = html_escape(record.get("title", "未入力"))
    program_id = html_escape(record.get("program_id", ""))
    meta = " / ".join([part for part in [program_type, keywords] if part])

    sections = []
    for key, label in DISPLAY_FIELDS:
        if key not in record:
            continue
        body = html_escape(record.get(key, "")) or "未入力"
        wide = " wide" if key in {"summary", "goal", "concepts", "small_experiment"} else ""
        muted = " muted" if body == "未入力" else ""
        sections.append(
            f"""
            <section class="data-section{wide}">
              <div class="section-label">{html_escape(label)}</div>
              <div class="section-body{muted}">{body}</div>
            </section>
            """
        )

    st.markdown(
        f"""
        <article class="card">
          <div class="card-head">
            <div>
              <div class="meta-line">{meta}</div>
              <h2>{title}</h2>
            </div>
            <div class="record-id">{program_id}</div>
          </div>
          <div class="section-grid">
            {''.join(sections)}
          </div>
        </article>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    css()
    st.markdown('<div class="topline">Program List</div>', unsafe_allow_html=True)
    st.title("カードビュー")

    with st.sidebar:
        st.subheader("Google Sheets")
        st.caption(secret_value("google_sheets", "worksheet_name", "シート1"))
        if st.button("再読み込み", use_container_width=True):
            cached_read_sheet.clear()
            st.rerun()

        uploaded_file = st.file_uploader("xlsx取り込み", type=["xlsx"])
        if uploaded_file is not None:
            uploaded_df = pd.read_excel(uploaded_file)
            st.write(f"{len(uploaded_df)}件")
            if st.button("Google Sheetsへ反映", type="primary", use_container_width=True):
                replace_sheet(uploaded_df)
                cached_read_sheet.clear()
                st.success("反映しました")
                st.rerun()

    try:
        df = cached_read_sheet()
    except Exception as exc:
        st.error(f"Google Sheetsに接続できません: {exc}")
        st.stop()

    if df.empty:
        st.info("表示できるデータがありません")
        st.stop()

    total = len(df)
    if "current_index" not in st.session_state:
        st.session_state.current_index = 1

    st.session_state.current_index = max(1, min(int(st.session_state.current_index), total))

    nav_left, nav_mid, nav_right, nav_fav = st.columns([1, 2.3, 1, 1.9])
    with nav_left:
        if st.button("‹", use_container_width=True, disabled=st.session_state.current_index <= 1):
            st.session_state.current_index -= 1
            st.rerun()
    with nav_mid:
        selected_index = st.number_input(
            "表示",
            min_value=1,
            max_value=total,
            value=st.session_state.current_index,
            step=1,
            label_visibility="collapsed",
        )
        if selected_index != st.session_state.current_index:
            st.session_state.current_index = int(selected_index)
            st.rerun()
        st.caption(f"{st.session_state.current_index} / {total} 件")
    with nav_right:
        if st.button("›", use_container_width=True, disabled=st.session_state.current_index >= total):
            st.session_state.current_index += 1
            st.rerun()

    record = df.iloc[st.session_state.current_index - 1]
    sheet_row = st.session_state.current_index + 1
    is_favorite = normalize_bool(record.get("favorite"))

    with nav_fav:
        fav_label = "★ お気に入り" if is_favorite else "☆ お気に入り"
        if st.button(fav_label, use_container_width=True):
            update_cell(sheet_row, "favorite", not is_favorite)
            cached_read_sheet.clear()
            st.rerun()

    render_card(record)

    st.markdown('<section class="note-panel">', unsafe_allow_html=True)
    note_key = f"note_{st.session_state.current_index}"
    note_value = st.text_area(
        "user_note",
        value=str(record.get("user_note", "")),
        height=150,
        key=note_key,
    )
    if st.button("更新", type="primary"):
        update_cell(sheet_row, "user_note", note_value)
        cached_read_sheet.clear()
        st.success("保存しました")
        st.rerun()
    st.markdown("</section>", unsafe_allow_html=True)

    csv = clean_dataframe(df).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSVダウンロード",
        data=csv,
        file_name="program_list.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
