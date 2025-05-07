import streamlit as st
import pandas as pd
import datetime
import os
import ast

# Inicializar archivos
REGISTRO_PATH = 'registro_salud.csv'
FARMACOS_PATH = 'farmacos.csv'

# Cargar o inicializar registros
if os.path.exists(REGISTRO_PATH):
    df = pd.read_csv(REGISTRO_PATH)
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
else:
    df = pd.DataFrame(columns=[
        'fecha', 'fatiga', 'estado_animo', 'migrañas', 'dolor_articular', 'inflamacion_intestinal',
        'dolor abdominal', 'diarrea', 'estrenimiento', 'gases', 'síntomas alergia menores',
        'otros_sintomas', 'farmacos_tomados', 'hora_acostarse', 'hora_levantarse',
        'horas_sueno', 'calidad_sueno', 'sueno_incidentes', 'comidas', 'eventos_factores', 'notas'
    ])

if os.path.exists(FARMACOS_PATH):
    farmacos_df = pd.read_csv(FARMACOS_PATH)
    farmacos_df['inicio'] = pd.to_datetime(farmacos_df['inicio'], errors='coerce')
    farmacos_df['fin'] = pd.to_datetime(farmacos_df['fin'], errors='coerce')
else:
    farmacos_df = pd.DataFrame(columns=['nombre', 'tipo', 'inicio', 'fin'])

st.title("Registro diario de salud")

st.sidebar.subheader("📋 Fármacos activos")
with st.sidebar.expander("➕ Registrar nuevo fármaco"):
    nombre_farmaco = st.text_input("Nombre del fármaco")
    tipo_farmaco = st.selectbox("Tipo", ["Permanente", "Temporal"])
    inicio_farmaco = st.date_input("Fecha de inicio", datetime.date.today())
    fin_farmaco = None
    if tipo_farmaco == "Temporal":
        fin_farmaco = st.date_input("Fecha de finalización", datetime.date.today())
    if st.button("Guardar fármaco"):
        nueva_fila = pd.DataFrame([{
            'nombre': nombre_farmaco,
            'tipo': tipo_farmaco,
            'inicio': pd.to_datetime(inicio_farmaco),
            'fin': pd.to_datetime(fin_farmaco) if tipo_farmaco == "Temporal" else pd.NaT
        }])
        farmacos_df = pd.concat([farmacos_df, nueva_fila], ignore_index=True)
        farmacos_df.to_csv(FARMACOS_PATH, index=False)
        st.success("Fármaco registrado correctamente.")

# Filtrar fármacos activos hoy
hoy = pd.Timestamp(datetime.date.today())
farmacos_hoy = farmacos_df[(farmacos_df['inicio'] <= hoy) &
                           ((farmacos_df['tipo'] == 'Permanente') | (farmacos_df['fin'] >= hoy))]

# Entradas del día
st.subheader("📝 Registro del día")
fecha = st.date_input("Fecha", hoy.date())
fatiga = st.slider("Nivel de fatiga", 0, 10, 5)
estado_animo = st.slider("Estado de ánimo", 0, 10, 5)
migranas = st.slider("Migrañas", 0, 10, 0)
dolor_articular = st.slider("Dolor articular", 0, 10, 0)
inflamacion = st.slider("Inflamación intestinal", 0, 10, 0)
dolor_abdominal = st.slider("Dolor abdominal", 0, 10, 0)
diarrea = st.slider("Diarrea", 0, 10, 0)
estrenimiento = st.slider("Estrenimiento", 0, 10, 0)
gases = st.slider("Gases", 0, 10, 0)
sintomas_alergia_menores = st.slider("Síntomas alergia menores", 0, 10, 0)
otros_sintomas = st.text_input("Otros síntomas")

farmacos_tomados = st.multiselect("¿Qué fármacos tomaste hoy?", farmacos_hoy['nombre'].tolist())

hora_acostarse = st.time_input("Hora de acostarse")
hora_levantarse = st.time_input("Hora de levantarse")

sueno_incidentes = st.multiselect("¿Qué incidencias ocurrieron durante el sueño?", [
    "Me costó dormirme", "Me desperté una vez", "Me desperté varias veces",
    "Tuve pesadillas", "Tuve angustia", "Tuve ansiedad",
    "Terminó el sueño antes de tiempo", "Otros"
])
calidad_sueno = st.slider("Calidad del sueño (0-10)", 0, 10, 5)

# Cálculo de horas de sueño
t1 = datetime.datetime.combine(datetime.date.today(), hora_acostarse)
t2 = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), hora_levantarse)
horas_sueno = round((t2 - t1).total_seconds() / 3600, 2)

st.markdown("### 🍽️ Registro de comidas")
comidas_dict = {}
comidas_momentos = ["Desayuno", "Intermedio-mañana", "Comida", "Intermedio-tarde", "Cena"]

for momento in comidas_momentos:
    with st.expander(momento):
        alimentos = [st.text_input(f"{momento} - Alimento {i+1}", key=f"{momento}_{i}") for i in range(5)]
        comidas_dict[momento] = [a for a in alimentos if a.strip() != ""]

comidas_str = str(comidas_dict)

st.markdown("### 📌 Otros registros")
eventos = st.multiselect("Eventos o factores externos", [
    "Estrés laboral", "Estudios", "Viajes", "Fiestas/Celebraciones", "Cambio de clima", "Otros"
])
notas = st.text_area("Notas adicionales")

if st.button("Guardar registro"):
    nueva_fila = pd.DataFrame([{
        'fecha': pd.to_datetime(fecha), 'fatiga': fatiga, 'estado_animo': estado_animo, 'migrañas': migranas,
        'dolor_articular': dolor_articular, 'inflamacion_intestinal': inflamacion,
        'dolor abdominal': dolor_abdominal, 'diarrea': diarrea, 'estrenimiento': estrenimiento,
        'gases': gases, 'síntomas alergia menores': sintomas_alergia_menores,
        'otros_sintomas': otros_sintomas,
        'farmacos_tomados': ", ".join(farmacos_tomados),
        'hora_acostarse': hora_acostarse, 'hora_levantarse': hora_levantarse,
        'horas_sueno': horas_sueno, 'calidad_sueno': calidad_sueno,
        'sueno_incidentes': ", ".join(sueno_incidentes),
        'comidas': comidas_str, 'eventos_factores': ", ".join(eventos), 'notas': notas
    }])
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(REGISTRO_PATH, index=False)
    st.success("Registro guardado correctamente.")

st.subheader("📈 Visualización de datos")
grupos = {
    "Síntomas": ['fatiga', 'estado_animo', 'migrañas', 'dolor_articular', 'inflamacion_intestinal',
                'dolor abdominal', 'diarrea', 'estrenimiento', 'gases', 'síntomas alergia menores'],
    "Sueño (calidad y duración)": ['calidad_sueno', 'horas_sueno']
}

grupo_seleccionado = st.radio("Selecciona un grupo de variables", list(grupos.keys()))
variable = st.selectbox("Selecciona una variable a visualizar", grupos[grupo_seleccionado])

if not df.empty:
    df_ordenado = df.sort_values('fecha')
    st.line_chart(df_ordenado.set_index('fecha')[variable])
else:
    st.info("Aún no hay registros guardados.")

# 🔍 Módulo de preguntas abiertas
st.subheader("🧠 Pregunta algo sobre tus datos")
pregunta = st.text_input("¿Qué quieres saber?")

if pregunta and not df.empty:
    import difflib
    import numpy as np

    df['comidas'] = df['comidas'].fillna("{}").apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    def buscar_patron_en_comidas(palabra):
        contiene = df['comidas'].apply(lambda comidas: any(
            palabra.lower() in alimento.lower()
            for momento in comidas.values() for alimento in momento
        ))
        return contiene

    if "queso" in pregunta.lower() and "sueñ" in pregunta.lower():
        queso = buscar_patron_en_comidas("queso")
        sin_queso = ~queso
        if queso.sum() > 0 and sin_queso.sum() > 0:
            promedio_con = df.loc[queso, 'calidad_sueno'].mean()
            promedio_sin = df.loc[sin_queso, 'calidad_sueno'].mean()
            st.markdown(f"**Respuesta:** La calidad media del sueño con queso es {promedio_con:.2f}, y sin queso es {promedio_sin:.2f}.")
        else:
            st.info("No hay suficientes datos con y sin queso para comparar.")
    else:
        st.info("Por ahora solo puedo responder preguntas como: '¿Comer queso afecta al sueño?' Pronto añadiré más inteligencia.")
