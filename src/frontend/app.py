import streamlit as st
import requests
import time

# Настройка страницы
st.set_page_config(page_title="Backend Status", layout="centered")

# Функция проверки здоровья бэкенда
def check_health():
    url = "http://backend:8000/api/ping"
    try:
        # Устанавливаем таймаут 2 секунды, чтобы интерфейс не зависал
        response = requests.get(url, timeout=2)
        return response.status_code
    except requests.exceptions.RequestException:
        return None

# Блок отображения статуса
status_code = check_health()

if status_code == 200:
    st.success(f"### Backend {status_code}")
elif status_code is not None:
    st.error(f"### Backend {status_code}")
else:
    st.error("### Backend Offline (Нет ответа)")

# Автоматическое обновление страницы каждые 2 секунды
time.sleep(2)
st.rerun()
