import streamlit as st
import json, logging, os
from utils import render_sidebar, load_css
from api_client import upload_archive

st.set_page_config(layout="wide", page_title="Архивы")

ARCHIVES_FILE = './archives.json'

if not os.path.exists(ARCHIVES_FILE) or os.path.getsize(ARCHIVES_FILE) == 0:
    with open(ARCHIVES_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

with open(ARCHIVES_FILE, 'r', encoding='utf-8') as f:
    st.session_state.archives = json.load(f)

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()


def save_archives():
    with open('./archives.json', 'w') as f:
        archives = st.session_state.archives
        json.dump(list(filter(lambda x: x['status'] != "Ошибка индексации", archives)), f, indent=2, ensure_ascii=False)


def get_last_archive():
    archives = st.session_state.archives
    if len(archives):
        return archives[-1]


def delete_archive(archive_id):
    st.session_state.archives = [a for a in st.session_state.archives if a["id"] != archive_id]
    save_archives()
    st.rerun()


def render_archive_card(archive, show_delete=True):
    colors = {
        "Индексируется": "#F4B41A",  # Желтый
        "Проиндексирован": "#00E676",  # Зеленый
        "Ошибка индексации": "#FF1744"  # Красный
    }
    color = colors.get(archive["status"], "#FFFFFF")

    delete_btn_key = f"delete_btn_{archive['id']}"

    return f"""
    <div style="background-color: #1A1A1A; border: 1px solid {color}; border-radius: 12px; padding: 16px; color: #FFFFFF; font-family: sans-serif; margin-bottom: 5px; box-sizing: border-box; height: 185px;">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
            <div style="background-color: {color}; width: 50px; height: 50px; border-radius: 12px; display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6H12L10 4H4C2.9 4 2.01 4.9 2.01 6L2 18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V8C22 6.9 21.1 6 20 6ZM20 18H4V8H20V18Z" fill="#1A1A1A"/>
                </svg>
            </div>
            <div style="overflow: hidden;">
                <div style="font-size: 16pt; font-weight: 500; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{archive['name']}</div>
                <div style="font-size: 12pt; color: #888;">{archive['status']}</div>
            </div>
        </div>
        <div style="display: flex; border-top: 1px solid #333; border-bottom: 1px solid #333; padding: 12px 0; margin-bottom: 15px;">
            <div style="flex: 1; text-align: center; border-right: 1px solid #333;">
                <div style="font-size: 16pt; font-weight: 500;">{archive.get('files_count', 0)}</div>
                <div style="font-size: 12pt; color: #888;">Файла</div>
            </div>
            <div style="flex: 1; text-align: center;">
                <div style="font-size: 16pt; font-weight: 500;">{archive.get('chunks_count', 0)}</div>
                <div style="font-size: 12pt; color: #888;">Чанка</div>
            </div>
        </div>
    </div>
    """


load_css()
render_sidebar()

st.markdown('<div class="archive-title" style="font-size: 32pt; margin-bottom: 20px;">Архивы</div>',
            unsafe_allow_html=True)

col_left, col_right = st.columns([3, 1], gap="large")

with col_left:
    top_col1, top_col2 = st.columns([2, 1], gap="medium")

    with top_col1:
        st.markdown('''
            <div class="upload-container">
                <div class="custom-card upload-visual-card">
                    <svg width="42" height="47" viewBox="0 0 42 47" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M21.9686 4.42686C21.72 4.15491 21.3686 4 21 4C20.6315 4 20.2801 4.15491 20.0314 4.42686L13.0313 12.0831C12.5422 12.6181 12.5794 13.4483 13.1144 13.9374C13.6494 14.4265 14.4795 14.3894 14.9687 13.8544L19.6875 8.69315V28.0625C19.6875 28.7873 20.2752 29.375 21 29.375C21.7249 29.375 22.3125 28.7873 22.3125 28.0625V8.69315L27.0314 13.8544C27.5205 14.3894 28.3507 14.4265 28.8857 13.9374C29.4207 13.4483 29.4578 12.6181 28.9686 12.0831L21.9686 4.42686Z" fill="#FFF" />
                      <path d="M6.5625 30.6875C6.5625 29.9626 5.97489 29.375 5.25 29.375C4.52513 29.375 3.9375 29.9626 3.9375 30.6875V30.7836C3.93747 33.1769 3.93743 35.1059 4.14141 36.6231C4.3532 38.1983 4.80625 39.5245 5.85961 40.5778C6.91297 41.6313 8.23925 42.0844 9.81444 42.2961C11.3316 42.5 13.2607 42.5 15.654 42.5H26.3461C28.7394 42.5 30.6684 42.5 32.1856 42.2961C33.7608 42.0844 35.087 41.6313 36.1405 40.5778C37.1938 39.5245 37.6469 38.1983 37.8586 36.6231C38.0625 35.1059 38.0625 33.1769 38.0625 30.7836V30.6875C38.0625 29.9626 37.4748 29.375 36.75 29.375C36.0252 29.375 35.4375 29.9626 35.4375 30.6875C35.4375 33.1994 35.4347 34.9514 35.2571 36.2733C35.0844 37.5575 34.7687 38.2373 34.2842 38.7217C33.7998 39.2061 33.12 39.5218 31.8358 39.6946C30.5139 39.8722 28.762 39.875 26.25 39.875H15.75C13.238 39.875 11.4861 39.8722 10.1642 39.6946C8.88011 39.5218 8.2001 39.2061 7.71577 38.7217C7.23144 38.2373 6.91565 37.5575 6.74301 36.2733C6.56528 34.9514 6.5625 33.1994 6.5625 30.6875Z" fill="#FFF" />
                    </svg>
                    <h3 style="margin: 10px 0;">Перетащите архив сюда</h3>
                    <p style="color: #DDDDDD; font-size: 14pt;">или нажмите для выбора файла</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Загрузка архива",
            type=["zip"],
            key="archive_uploader",
            label_visibility="collapsed",
            accept_multiple_files=True
        )

        if uploaded_files:
            for file in uploaded_files:
                if file.name not in st.session_state.processed_files:
                    st.session_state.processed_files.add(file.name)

                    new_archive = {
                        "id": len(st.session_state.archives) + 1,
                        "name": file.name.split('.')[0],
                        "status": "Индексируется",
                        "files_count": 0,
                        "chunks_count": 0
                    }
                    st.session_state.archives.append(new_archive)
                    current_index = len(st.session_state.archives) - 1

                    try:
                        files_payload = {
                            "file": (file.name, file.getvalue(), "application/zip")
                        }

                        response = upload_archive(files_payload)
                        st.session_state.archives[current_index]["status"] = response["status"]
                        st.session_state.archives[current_index]["files_count"] = response["files_count"]
                        st.session_state.archives[current_index]["chunks_count"] = response["chunks_count"]

                        save_archives()

                        st.rerun()

                    except Exception as e:
                        st.session_state.archives[current_index]["status"] = "Ошибка индексации"
                        logging.error(f"Ошибка индексации: {e}")

    with top_col2:
        if len(st.session_state.archives) > 0:
            latest_archive = get_last_archive()
            st.markdown(render_archive_card(latest_archive), unsafe_allow_html=True)

            if st.button("Удалить", key=f"delete_btn_latest_{latest_archive['id']}", use_container_width=True):
                delete_archive(latest_archive['id'])
        else:
            st.markdown('''
                <div class="custom-card" style="height: 230px; display: flex; align-items: center; justify-content: center;">
                    <div style="text-align: center; color: #555;">
                        <p style="font-size: 14pt; color: #888">Недавний архив</p>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

    st.markdown(
        '<div class="archive-title" style="font-size: 24pt; margin-top: 30px; margin-bottom: 10px;">Ваши архивы</div>',
        unsafe_allow_html=True)

    if len(st.session_state.archives) > 0:
        for i in range(0, len(st.session_state.archives), 3):
            cols = st.columns(3, gap="medium")
            row_archives = st.session_state.archives[i:i + 3]

            for idx, archive in enumerate(row_archives):
                with cols[idx]:
                    st.markdown(render_archive_card(archive), unsafe_allow_html=True)

                    if st.button("Удалить", key=f"latest_delete_btn_{archive['id']}", use_container_width=True):
                        delete_archive(archive['id'])
    else:
        st.markdown("<p style='color: #888; font-size: 14pt;'>Вы еще не загрузили ни одного архива</p>",
                    unsafe_allow_html=True)

with col_right:
    st.markdown('''
        <div class="custom-card tall-card">
            <h4 style="color: #E0E0E0; margin-bottom: 20pt;">Детали архива</h4>
            <p style="color: #888; font-size: 14pt;">
                Здесь будет отображаться подробная информация по выбранному архиву
            </p>
        </div>
    ''', unsafe_allow_html=True)