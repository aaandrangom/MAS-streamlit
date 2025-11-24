import streamlit as st

st.title("¡Hola Mundo! 🚀")

st.write("Si puedes leer esto en internet, significa que **el despliegue fue un éxito**.")

nombre = st.text_input("Escribe tu nombre aquí:")

if st.button("¡Presióname!"):
    if nombre:
        st.success(f"¡Bienvenido al mundo del desarrollo web, {nombre}!")
        st.balloons()
    else:
        st.warning("Por favor, escribe tu nombre primero.")