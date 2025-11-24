import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import odeint

st.set_page_config(page_title="Laboratorio MAS", layout="wide", page_icon="⚛️")

def plot_time_series(t, y_data, names, title, y_label):
    fig = go.Figure()
    for y, name in zip(y_data, names):
        fig.add_trace(go.Scatter(x=t, y=y, mode='lines', name=name))
    fig.update_layout(
        title=title, xaxis_title="Tiempo (s)", yaxis_title=y_label,
        hovermode="x unified", height=400, template="plotly_white"
    )
    return fig

st.sidebar.title("Menú de Simulación")
opcion = st.sidebar.radio(
    "Selecciona un módulo:",
    ("Inicio", "Masa-Resorte", "Péndulo Simple", "Análisis T vs (m, k)", "MAS Amortiguado")
)

if opcion == "Inicio":
    st.title("Movimiento Armónico Simple (MAS)")
    st.markdown("""
    Bienvenido a la aplicación interactiva para el estudio del MAS.
    Esta herramienta permite visualizar fenómenos físicos fundamentales:
    
    * **Masa-Resorte:** Dinámica de fuerzas elásticas.
    * **Péndulo:** Comparación de modelos lineales y reales.
    * **Energía:** Conservación y transformación.
    * **Amortiguamiento:** Efecto de la fricción en la oscilación.
    """)
    
    st.info("Selecciona una opción en el menú de la izquierda para comenzar.")
    
    st.subheader("Ecuación Fundamental")
    st.latex(r"x(t) = A \cos(\omega t + \phi)")
    st.write("Donde $A$ es la amplitud, $\omega$ la frecuencia angular y $\phi$ la fase inicial.")

elif opcion == "Masa-Resorte":
    st.header("Sistema Masa-Resorte")
    
    tipo_sistema = st.radio(
        "Seleccione la Orientación del Sistema:",
        ("Horizontal", "Vertical"),
        horizontal=True
    )
    
    st.divider()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Parámetros")
        m = st.slider("Masa (m) [kg]", 0.1, 10.0, 1.0, 0.1)
        k = st.slider("Constante elástica (k) [N/m]", 1.0, 100.0, 10.0, 1.0)
        A = st.slider("Amplitud (A) [m]", 0.1, 5.0, 1.0, 0.1)
        duration = st.slider("Tiempo simulación [s]", 5, 30, 10)
    
    w = np.sqrt(k / m)
    T = 2 * np.pi / w
    t = np.linspace(0, duration, 500)
    
    x = A * np.cos(w * t)
    v = -A * w * np.sin(w * t)
    a = -A * (w**2) * np.cos(w * t)
    
    E_p = 0.5 * k * x**2
    E_k = 0.5 * m * v**2
    E_m = E_p + E_k

    with col2:
        if tipo_sistema == "Vertical":
            g = 9.81
            delta_eq = (m * g) / k
            st.warning(f"**Modo Vertical:** La gravedad estira el resorte inicial.")
            st.metric("Desplazamiento de equilibrio (mg/k)", f"{delta_eq:.3f} m")
            desc_extra = " (Vertical - Afectado por gravedad)"
        else:
            st.success(f"**Modo Horizontal:** Sin fricción, movimiento sobre superficie.")
            st.metric("Desplazamiento de equilibrio", "0.000 m")
            desc_extra = " (Horizontal)"

        st.metric(label="Periodo (T)", value=f"{T:.2f} s")
        st.metric(label="Frecuencia Angular (ω)", value=f"{w:.2f} rad/s")
        st.metric(label="Energía Mecánica (E)", value=f"{0.5 * k * A**2:.2f} J")
        tab1, tab2 = st.tabs(["Cinemática", "Energía"])
        
        with tab1:
            st.plotly_chart(plot_time_series(
                t, [x, v, a], 
                ["Posición (m)", "Velocidad (m/s)", "Aceleración (m/s²)"], 
                f"Cinemática{desc_extra}", "Magnitud"
            ), use_container_width=True)
            
        with tab2:
            st.plotly_chart(plot_time_series(
                t, [E_p, E_k, E_m], 
                ["Potencial Elástica", "Cinética", "Mecánica Total"], 
                f"Energía{desc_extra}", "Joules (J)"
            ), use_container_width=True)

elif opcion == "Péndulo Simple":
    st.header("Péndulo Simple: Lineal vs No Lineal")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        L = st.slider("Longitud (L) [m]", 0.1, 5.0, 1.0, 0.1)
        g = st.number_input("Gravedad (g) [m/s²]", value=9.81)
        theta0_deg = st.slider("Ángulo inicial (grados)", 1, 179, 10)
        theta0 = np.radians(theta0_deg)
        
    t = np.linspace(0, 10, 500)
    w0 = np.sqrt(g / L)
    
    theta_linear = theta0 * np.cos(w0 * t)
    
    def pendulum_ode(y, t, g, L):
        theta, omega = y
        dydt = [omega, -(g/L) * np.sin(theta)]
        return dydt

    y0 = [theta0, 0.0]
    sol = odeint(pendulum_ode, y0, t, args=(g, L))
    theta_nonlinear = sol[:, 0]
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=np.degrees(theta_linear), name='Modelo Lineal (Simple)', line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=t, y=np.degrees(theta_nonlinear), name='Modelo No Lineal (Exacto)'))
        
        fig.update_layout(title="Ángulo del Péndulo vs Tiempo", xaxis_title="Tiempo (s)", yaxis_title="Ángulo (grados)")
        st.plotly_chart(fig, use_container_width=True)

elif opcion == "Análisis T vs (m, k)":
    st.header("Análisis del Periodo (T)")
    st.latex(r"T = 2\pi \sqrt{\frac{m}{k}}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Efecto de la Masa")
        k_fixed = st.slider("Fijar Constante k [N/m]", 1.0, 50.0, 10.0)
        m_range = np.linspace(0.1, 10, 100)
        T_m = 2 * np.pi * np.sqrt(m_range / k_fixed)
        
        fig_m = go.Figure()
        fig_m.add_trace(go.Scatter(x=m_range, y=T_m, mode='lines', line=dict(color='blue')))
        fig_m.update_layout(title=f"Periodo vs Masa (k={k_fixed})", xaxis_title="Masa (kg)", yaxis_title="Periodo (s)")
        st.plotly_chart(fig_m, use_container_width=True)
        
    with col2:
        st.subheader("Efecto de la Constante k")
        m_fixed = st.slider("Fijar Masa m [kg]", 0.1, 10.0, 1.0)
        k_range = np.linspace(1.0, 50, 100)
        T_k = 2 * np.pi * np.sqrt(m_fixed / k_range)
        
        fig_k = go.Figure()
        fig_k.add_trace(go.Scatter(x=k_range, y=T_k, mode='lines', line=dict(color='red')))
        fig_k.update_layout(title=f"Periodo vs Constante k (m={m_fixed})", xaxis_title="Constante k (N/m)", yaxis_title="Periodo (s)")
        st.plotly_chart(fig_k, use_container_width=True)

elif opcion == "MAS Amortiguado":
    st.header("Oscilador Armónico Amortiguado")
    st.markdown("Añadimos un término de fricción proporcional a la velocidad: $F_{friccion} = -b v$")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        m = st.number_input("Masa (m)", value=1.0)
        k = st.number_input("Constante (k)", value=10.0)
        b = st.slider("Coeficiente amortiguamiento (b)", 0.0, 5.0, 0.5, 0.1)
        A = 1.0
        
    def damped_ode(y, t, m, k, b):
        x, v = y
        dydt = [v, -(b/m)*v - (k/m)*x]
        return dydt
    
    t = np.linspace(0, 20, 1000)
    y0 = [A, 0.0]
    sol = odeint(damped_ode, y0, t, args=(m, k, b))
    x_damped = sol[:, 0]
    
    envelope = A * np.exp(-(b / (2*m)) * t)
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=x_damped, name='Posición x(t)', line=dict(width=2)))
        if b > 0 and b**2 < 4*m*k: 
            fig.add_trace(go.Scatter(x=t, y=envelope, name='Envolvente (+)', line=dict(dash='dot', color='gray')))
            fig.add_trace(go.Scatter(x=t, y=-envelope, name='Envolvente (-)', line=dict(dash='dot', color='gray')))
            
        fig.update_layout(title="Movimiento Amortiguado", xaxis_title="Tiempo (s)", yaxis_title="Posición (m)")
        st.plotly_chart(fig, use_container_width=True)