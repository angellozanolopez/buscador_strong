"""
Este código es un buscador bíblico para la versión Reina Valera 60, que permite encontrar palabras o números en los versículos 
almacenados en una base de datos SQLite (`diccionario_strong.db`). La búsqueda se realiza en los campos `contenido`, `texto_sin_tildes` 
y `texto`, asegurando coincidencias precisas.

El sistema diferencia entre búsquedas exactas (usando comillas) y aproximadas, y es compatible con términos en español, hebreo y griego (o sus equivalentes numericos). 
Además, genera enlaces dinámicos a versículos en la web utilizando diccionarios de diminutivos de libros bíblicos. La interfaz está 
construida con Streamlit, proporcionando una experiencia interactiva y eficiente para los usuarios.
"""

import os
import re
import unicodedata
import streamlit as st
import sqlite3
# BLOQUE 1 -------------------------------------------------------------------------------------------------------------------------------
# Ruta base donde están los archivos de la Biblia
BASE_PATH = r"C:\PYTHON\buscador_strong\Reina Valera del 60"

# Variables de diseño
TAMANIO_TITULO = "30px"
TAMANIO_RESULTADOS = "20px"
RADIO_BORDE = "0px"

# Diccionarios con los diminutivos
DIRECCION_AT = "https://www.logosklogos.com/interlinear/AT/"
DIRECCION_NT = "https://www.logosklogos.com/interlinear/NT/"

DIMINUTIVOS_AT = {
    "genesis": "Gn", "exodo": "Ex", "levitico": "Lv", "numeros": "Nm", "deuteronomio": "Dt",
    "josue": "Jos", "jueces": "Jue", "rut": "Rt", "1a samuel": "1S", "2a samuel": "2S",
    "1a reyes": "1R", "2a reyes": "2R", "1a cronicas": "1Cr", "2a cronicas": "2Cr",
    "esdras": "Esd", "nehemias": "Neh", "ester": "Est", "job": "Job", "salmos": "Sal",
    "proverbios": "Pr", "eclesiastes": "Ec", "cantares": "Cnt", "isaias": "Is",
    "jeremias": "Jer", "lamentaciones": "Lm", "ezequiel": "Ez", "daniel": "Dn",
    "oseas": "Os", "joel": "Jl", "amos": "Am", "abdias": "Abd", "jonas": "Jon",
    "miqueas": "Mi", "nahum": "Nah", "habacuc": "Hab", "sofonias": "Sof", "hageo": "Ha",
    "zacarias": "Zac", "malaquias": "Mal"
}

DIMINUTIVOS_NT = {
    "mateo": "Mt", "marcos": "Mr", "lucas": "Lc", "juan": "Jn", "hechos": "Hch",
    "romanos": "Ro", "1a corintios": "1Co", "2a corintios": "2Co", "galatas": "Ga",
    "efesios": "Ef", "filipenses": "Fil", "colosenses": "Col", "1a tesalonicenses": "1Ts",
    "2a tesalonicenses": "2Ts", "1a timoteo": "1Tm", "2a timoteo": "2Tm", "tito": "Tit",
    "filemon": "Flm", "hebreos": "He", "santiago": "Stg", "1a pedro": "1P",
    "2a pedro": "2P", "1a juan": "1Jn", "2a juan": "2Jn", "3a juan": "3Jn",
    "judas": "Jud", "apocalipsis": "Ap"
}
# BLOQUE 2 -------------------------------------------------------------------------------------------------------------------------------
# Función para eliminar tildes
def quitar_tildes(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
# BLOQUE 3 -------------------------------------------------------------------------------------------------------------------------------
# Iniciar variable de sesión para resultados
if "resultados" not in st.session_state:
    st.session_state.resultados = []
# BLOQUE 4 -------------------------------------------------------------------------------------------------------------------------------
def buscar_texto_en_bd(texto):
    resultados = []

    busqueda_exacta = texto.startswith('"') and texto.endswith('"')

    # No modificar el texto si contiene caracteres hebreos
    if re.search(r'[\u0590-\u05FF]', texto):  # Detecta caracteres hebreos
        texto_limpio = texto.strip('"')  # No tocar si es hebreo
    else:
        texto_limpio = quitar_tildes(texto.strip('"').lower())  # Solo eliminar tildes si es texto latino

    # Conectar con SQLite
    conn = sqlite3.connect("diccionario_strong.db")

    # Habilitar soporte para expresiones regulares en SQLite
    conn.create_function("REGEXP", 2, lambda expr, item: re.search(expr, item) is not None)

    cursor = conn.cursor()

    # Ajustar consulta según el tipo de búsqueda
    if busqueda_exacta:
        consulta = f"""
        SELECT cita, texto FROM diccionario
        WHERE contenido REGEXP '\\b{texto_limpio}\\b'
           OR texto_sin_tildes REGEXP '\\b{texto_limpio}\\b'
           OR texto REGEXP '\\b{texto_limpio}\\b'
        """
    else:
        consulta = f"""
        SELECT cita, texto FROM diccionario
        WHERE contenido LIKE '%{texto_limpio}%'
           OR texto_sin_tildes LIKE '%{texto_limpio}%'
           OR texto LIKE '%{texto_limpio}%'
        """

    # Ejecutar consulta
    cursor.execute(consulta)
    filas = cursor.fetchall()
    conn.close()

    # Procesar resultados
    for cita, versiculo in filas:
        partes = cita.split()
        libro = " ".join(partes[:-1]).lower()
        capitulo_versiculo = partes[-1].split(",")

        es_antiguo_testamento = libro in DIMINUTIVOS_AT
        diccionario = DIMINUTIVOS_AT if es_antiguo_testamento else DIMINUTIVOS_NT
        base_url = DIRECCION_AT if es_antiguo_testamento else DIRECCION_NT

        if libro in diccionario and len(capitulo_versiculo) == 2:
            diminutivo = diccionario[libro]
            capitulo, versiculo_num = capitulo_versiculo
            url_final = f"{base_url}{diminutivo}/{capitulo}/{versiculo_num}"

            resultados.append((cita, versiculo, url_final))  

    return resultados

# BLOQUE 5 -------------------------------------------------------------------------------------------------------------------------------
# Interfaz con Streamlit
st.markdown(
    f"""
    <h1 style='font-size:{TAMANIO_TITULO}; margin-top: -50px;'>🔍 Buscador Bíblico - Reina Valera 60</h1>
    <h2 style='font-size:20px; margin-top: -20px;'>📖 Buscador Strong Inverso - Version 12.1</h2>
    <h2 style='font-size:14px; margin-top: -20px;'>(c) Creado por Angel Lozano Lopez - lozanolopez@gmail.com</h2>
    <h2 style='font-size:14px; margin-top: -20px;'>Creditos: https://www.logosklogos.com/</h2>
    """,
    unsafe_allow_html=True
)
# BLOQUE 6 -------------------------------------------------------------------------------------------------------------------------------
# 📜 Sección de Instrucciones en el menú lateral con margen ajustado
with st.sidebar:
    st.markdown(
        """
        <style>
            div[data-testid="stExpander"] {
                margin-top: -30px;  /* Reduce el margen superior */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.expander("📜 INSTRUCCIONES"):
        st.write(
            """
            Este buscador te permite encontrar términos dentro de la Biblia **Reina Valera 60**, ya sea en **español, hebreo o griego**.  
            También puedes buscar por el **equivalente numérico** de las palabras hebreas y griegas.  

            **¿Cómo utilizarlo?**  
            1️⃣ Escribe la palabra o el número que deseas buscar en el cuadro de texto y pulsa ENTER.  
            2️⃣ Se mostrarán todas las citas bíblicas enumeradas donde aparece el término buscado.  
            3️⃣ **Haga clic en el versículo para verlo en la web con detalle.**              
            """
        )

# BLOQUE 7 -------------------------------------------------------------------------------------------------------------------------------
# Restaurar el ancho completo del cuadro de búsqueda
st.markdown(
    """
    <style>
        div[data-testid="stTextInput"] {
            width: 100%;  /* La caja ocupa el 100% del ancho disponible */
        }
    </style>
    """,
    unsafe_allow_html=True
)
# BLOQUE 8 -------------------------------------------------------------------------------------------------------------------------------
# Cuadro de búsqueda
texto_busqueda = st.text_input("Introduce la palabra o número a buscar:")
# BLOQUE 9 -------------------------------------------------------------------------------------------------------------------------------
# Botón para borrar resultados
if st.button("Borrar resultados"):
    st.session_state.resultados = []
    texto_busqueda = ""
# BLOQUE 10 -------------------------------------------------------------------------------------------------------------------------------
if texto_busqueda:
    st.session_state.resultados = buscar_texto_en_bd(texto_busqueda)  # Ahora busca en la base de datos

    if st.session_state.resultados:
        st.write(f"### RESULTADOS ({len(st.session_state.resultados)}):")
        for indice, (nombre_archivo, versiculo, url_final) in enumerate(st.session_state.resultados, start=1):
            st.markdown(
                f"""
                <div style="
                    border: 1px solid white;
                    padding: 10px;
                    border-radius: {RADIO_BORDE};
                    margin-bottom: 10px;
                    font-size: {TAMANIO_RESULTADOS};
                ">
                    <b><a href="{url_final}" target="_blank">{indice}. {nombre_archivo}</a></b>: {versiculo}
                </div>
                """, unsafe_allow_html=True
            )
    else:
        st.write("### ❌ 0 resultados encontrados.")
# -------------------------------------------------------------------------------------------------------------------------------