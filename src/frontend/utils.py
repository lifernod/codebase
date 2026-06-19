import streamlit as st


def load_css(file_name="style.css"):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_sidebar():
    chat_svg = '<svg width="20" height="16" viewBox="0 0 20 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 16C1.45 16 0.979167 15.8042 0.5875 15.4125C0.195833 15.0208 0 14.55 0 14V2C0 1.45 0.195833 0.979167 0.5875 0.5875C0.979167 0.195833 1.45 0 2 0H18C18.55 0 19.0208 0.195833 19.4125 0.5875C19.8042 0.979167 20 1.45 20 2V14C20 14.55 19.8042 15.0208 19.4125 15.4125C19.0208 15.8042 18.55 16 18 16H2ZM2 14H18V4H2V14ZM5.5 13L4.1 11.6L6.675 9L4.075 6.4L5.5 5L9.5 9L5.5 13ZM10 13V11H16V13H10Z" fill="#F5F5F5"/></svg>'
    metrics_svg = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 14H6V9H4V14ZM12 14H14V4H12V14ZM8 14H10V11H8V14ZM8 9H10V7H8V9ZM2 18C1.45 18 0.979167 17.8042 0.5875 17.4125C0.195833 17.0208 0 16.55 0 16V2C0 1.45 0.195833 0.979167 0.5875 0.5875C0.195833 0.979167 1.45 0 2 0H16C16.55 0 17.0208 0.195833 17.4125 0.5875C17.8042 0.979167 18 1.45 18 2V16C18 16.55 17.8042 17.0208 17.4125 17.4125C17.0208 17.8042 16.55 18 16 18H2ZM2 16H16V2H2V16ZM2 2V16V2Z" fill="#F5F5F5"/></svg>'
    archives_svg = '<svg width="20" height="16" viewBox="0 0 20 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14 8V6H16V8H14ZM14 10H12V8H14V10ZM14 12V10H16V12H14ZM9.175 4L7.175 2H2V14H12V12H14V14H18V4H14V6H12V4H9.175ZM2 16C1.45 16 0.979167 15.8042 0.5875 15.4125C0.195833 15.0208 0 14.55 0 14V2C0 1.45 0.195833 0.979167 0.5875 0.5875C0.195833 0.195833 1.45 0 2 0H8L10 2H18C18.55 2 19.0208 2.19583 19.4125 2.5875C19.8042 2.97917 20 3.45 20 4V14C20 14.55 19.8042 15.0208 19.4125 15.4125C19.0208 15.8042 18.55 16 18 16H2ZM2 14V4V2V14Z" fill="#F5F5F5"/></svg>'

    with st.sidebar:
        st.markdown('<div class="custom-sidebar-menu">', unsafe_allow_html=True)

        def nav_btn(label, icon, page):
            st.markdown(f'<div class="menu-item-wrapper">{icon}<span>{label}</span></div>', unsafe_allow_html=True)
            if st.button(" ", key=f"btn_{label}"):
                st.switch_page(page)

        nav_btn("Чат", chat_svg, "pages/chat.py")
        nav_btn("Метрики", metrics_svg, "pages/metrics.py")
        nav_btn("Архивы", archives_svg, "pages/archives.py")

        st.markdown('</div>', unsafe_allow_html=True)