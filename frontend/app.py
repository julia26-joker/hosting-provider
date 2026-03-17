import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Хостинг-провайдер", layout="wide")

st.title("Аренда мощностей")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(" Создать новый инстанс")

    inst_type = st.radio("Тип", ["container", "vm"], format_func=lambda x: "Контейнер" if x == "container" else "Виртуальная машина")

    if inst_type == "container":
        os_options = ["ubuntu"]
    else:
        os_options = ["ubuntu", "alpine", "debian"]

    with st.form("create_form"):
        name = st.text_input("Имя инстанса", "my-instance")
        os = st.selectbox("ОС", os_options)
        cpu = st.slider("CPU (ядра)", 1, 4, 1)
        ram = st.slider("RAM (MB)", 256, 4096, 512, step=256)
        disk = st.slider("Диск (GB)", 5, 50, 10)
        ssh_key = st.text_area("SSH ключ (опционально)", "")

        submitted = st.form_submit_button("🚀 Запустить")

        if submitted:
            with st.spinner("Создаем..."):
                response = requests.post(
                    f"{API_URL}/api/create",
                    json={
                        "name": name,
                        "type": inst_type,
                        "os": os,
                        "cpu": cpu,
                        "ram": ram,
                        "disk": disk,
                        "ssh_key": ssh_key if ssh_key else None
                    }
                )
                if response.status_code == 200:
                    st.success(f"Создано! SSH порт: {response.json()['ssh_port']}")
                else:
                    st.error("Ошибка создания")

with col2:
    st.subheader("Мои инстансы")

    if st.button("Обновить список"):
        st.rerun()

    response = requests.get(f"{API_URL}/api/list")
    if response.status_code == 200:
        instances = response.json()
        if instances:
            header = st.columns([2, 1, 1, 1, 1, 1])
            for col, label in zip(header, ["Имя", "Тип", "ОС", "Статус", "SSH порт", "Действие"]):
                col.markdown(f"**{label}**")

            st.markdown("---")

            for inst in instances:
                row = st.columns([2, 1, 1, 1, 1, 1])
                row[0].write(inst['name'])
                row[1].write(inst['type'])
                row[2].write(inst['os'])
                row[3].write(inst['status'])
                row[4].write(inst['ssh_port'])

                if inst['status'] == 'running':
                    if row[5].button("⏹ Стоп", key=f"stop_{inst['id']}"):
                        res = requests.post(f"{API_URL}/api/stop/{inst['id']}")
                        if res.status_code == 200:
                            st.success(f"Инстанс {inst['name']} остановлен")
                            st.rerun()
                        else:
                            st.error("Ошибка остановки")
                else:
                    row[5].write("—")
        else:
            st.info("Нет активных инстансов")

st.markdown("---")
st.subheader(" Статус системы")

response = requests.get(f"{API_URL}/api/list")
instances = response.json() if response.status_code == 200 else []

active = sum(1 for i in instances if i['status'] == 'running')
total = len(instances)

col3, col4, col5 = st.columns(3)
with col3:
    st.metric("Активные инстансы", active)
with col4:
    st.metric("Всего создано", total)
with col5:
    st.metric("Свободно ресурсов", "N/A")