import streamlit as st


def connection():
    conn = st.connection("postgresql", type="sql", dialect="postgresql",
                         host="localhost",
                         port="5432",
                         database="migration",
                         username="postgres",
                         password="123456789")
    return conn


def connection2():
    conn = st.connection("postgresql", type="sql", dialect="postgresql",
                         host="localhost",
                         port="5432",
                         database="migration2",
                         username="postgres",
                         password="123456789")
    return conn