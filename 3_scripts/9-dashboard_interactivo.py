import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
import pathlib
from fpdf import FPDF
import streamlit.components.v1 as components

# CONFIGURACION Y RUTAS PORTABLES 
st.set_page_config(page_title="Dashboard Solar - TFI", layout="wide")

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

try:
    from configuracion_maestra import HUELLAS_CAMMESA, mapeo_coordenadas
except ImportError:
    st.error(" No se pudo encontrar 'configuracion_maestra.py'. Verifique las rutas.")
    HUELLAS_CAMMESA = {}
    mapeo_coordenadas = {}

CSV_SIMULACION = BASE_DIR / "4_salidas" / "4.5_simulacion_energia" / "simulacion_paneles.csv"
RUTA_MAPA_HTML = BASE_DIR / "4_salidas" / "riesgo_anual" / "mapa_riesgo_interactivo.html"

CATALOGO_PANELES = {
    "Estandar: Policristalino 330W": {"area": 1.94, "eficiencia": 0.170, "potencia": 330},
    "Intermedio: Monocristalino PERC 450W": {"area": 2.20, "eficiencia": 0.205, "potencia": 450},
    "Premium: Monocristalino Half-Cell 550W": {"area": 2.58, "eficiencia": 0.213, "potencia": 550}
}

@st.cache_data
def cargar_datos():
    if not CSV_SIMULACION.exists():
        st.error(f"No se encontró {CSV_SIMULACION}")
        return pd.DataFrame()
    return pd.read_csv(CSV_SIMULACION)

def generar_informe_pdf(ciudad, consumo, modelo, inclinacion, bateria_ah, voltaje, dias, pan_est, pan_bal, pan_man, mes_critico):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Informe Tecnico: Dimensionamiento Solar Off-Grid", ln=True, align='C')
    pdf.ln(5)
    
    # Parámetros del Sistema
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="1. Parametros Base del Sistema", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, txt=f"- Ubicacion: {ciudad.upper()}", ln=True)
    pdf.cell(0, 8, txt=f"- Consumo Base: {consumo} kWh/mes (Curva estacional ajustada por CAMMESA)", ln=True)
    pdf.cell(0, 8, txt=f"- Panel Seleccionado: {modelo}", ln=True)
    pdf.cell(0, 8, txt=f"- Inclinacion del Arreglo: {inclinacion} grados", ln=True)
    pdf.cell(0, 8, txt=f"- Banco de Baterias: {bateria_ah} Ah a {voltaje}V (Autonomia: {dias} dias)", ln=True)
    pdf.ln(5)
    
    # Comparativa de Estrategias
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="2. Comparativa de Estrategias de Dimensionamiento", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, txt=f"A. Criterio Estricto (Peor Escenario): {pan_est} paneles.", ln=True)
    pdf.cell(0, 8, txt="   Garantiza cobertura total en invierno, pero genera alto costo y excedente en verano.", ln=True)
    pdf.cell(0, 8, txt=f"B. Criterio Balanceado (Promedio): {pan_bal} paneles.", ln=True)
    pdf.cell(0, 8, txt="   Optimiza la relacion costo/beneficio asumiendo un riesgo controlado de deficit.", ln=True)
    pdf.cell(0, 8, txt=f"C. Criterio Manual (Usuario): {pan_man} paneles.", ln=True)
    pdf.ln(5)
    
    # Conclusión
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 8, txt=f"Nota Analitica: El mes con mayor estres sobre el sistema detectado es el mes {mes_critico}. La seleccion final de paneles debe considerar la tolerancia a cortes de suministro durante este periodo critico.")
    
    return pdf.output(dest='S').encode('latin-1')

df = cargar_datos()
if df.empty:
    st.stop()

ciudades_disponibles = sorted(df['Ciudad'].unique())
dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
ganancia_relativa_30_grados = [0.12, 0.10, 0.05, 0.00, -0.05, -0.08, -0.05, 0.00, 0.05, 0.10, 0.12, 0.15]
nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

# INTERFAZ DE USUARIO 
st.title("SISTEMA DE INTELIGENCIA CLIMATICA")

# Aviso de Advertencia con diseño solicitado
st.markdown("""
<div style="background-color: #ff4b4b; padding: 15px; border-radius: 5px; color: white; margin-bottom: 20px; text-align: center;">
    <strong> AVISO IMPORTANTE: Esta es una herramienta para uso orientativo. Los resultados son estimaciones técnicas basadas en modelos predictivos; para instalaciones reales, siempre debe consultar a un profesional certificado.</strong>
</div>
""", unsafe_allow_html=True)

st.subheader("Simulador Integral de Dimensionamiento Fotovoltaico (Off-Grid)")
st.markdown("---")

#  PANEL LATERAL (CONTROLES)
# Se evalúa la ciudad primero para poder recomendar la autonomía en baterías
st.sidebar.header("1. Parametros de Captacion")
ciudad_seleccionada = st.sidebar.selectbox("Nodo Geografico", ciudades_disponibles)
modelo_seleccionado = st.sidebar.selectbox("Catalogo de Paneles", list(CATALOGO_PANELES.keys()))

pr = st.sidebar.slider("Performance Ratio (PR %)", min_value=50, max_value=100, value=75, step=1) / 100.0
angulo_inclinacion = st.sidebar.slider("Angulo de Inclinacion (Grados)", min_value=0, max_value=45, value=30, step=1)

area = CATALOGO_PANELES[modelo_seleccionado]["area"]
eficiencia = CATALOGO_PANELES[modelo_seleccionado]["eficiencia"]
potencia_panel_w = CATALOGO_PANELES[modelo_seleccionado]["potencia"]

st.sidebar.header("2. Parametros de Demanda")
consumo_mensual = st.sidebar.number_input("Consumo Vivienda (kWh/mes)", min_value=50, max_value=2000, value=300, step=10)

st.sidebar.header("3. Almacenamiento (Baterias)")
# Lógica de sugerencia de días por zona geográfica
region = mapeo_coordenadas.get(ciudad_seleccionada.lower(), 'CENTRO').upper()
sugerencia_dias = {"SUR": 4, "PATAGONIA": 4, "CENTRO": 3, "CUYO": 3, "NOA": 2, "NEA": 2}.get(region, 3)

dias_autonomia = st.sidebar.slider(
    f"Dias de Autonomia (Sugerido {region}: {sugerencia_dias})", 
    min_value=1, max_value=5, value=sugerencia_dias, step=1
)
voltaje_sistema = st.sidebar.selectbox("Voltaje del Banco (V)", [12, 24, 48], index=2)
profundidad_descarga = 0.6 

st.sidebar.header("4. Estrategia de Dimensionamiento")
criterio_dimensionamiento = st.sidebar.radio(
    "Criterio de Cálculo",
    ["Estricto (Peor Mes)", "Balanceado (Promedio)", "Manual"],
    help="Estricto: Dimensiona para el peor escenario. Balanceado: Promedio. Manual: Ingreso libre."
)

#  LOGICA DE CAMMESA 
huella = HUELLAS_CAMMESA.get(region, [1.0]*12) # Fallback seguro
consumo_ajustado = [consumo_mensual * h for h in huella]
consumo_anual_real = sum(consumo_ajustado)
consumo_diario_max = max(consumo_ajustado) / 30.0

#  4. LOGICA DE CALCULO MATEMATICO 
df_ciudad = df[df['Ciudad'] == ciudad_seleccionada].copy()
energia_calculada_un_panel = []

for i, row in df_ciudad.iterrows():
    hsp_diario = row['HSP_Diario_Predicho']
    mes_idx = int(row['Mes_Prediccion']) - 1
    dias = dias_por_mes[mes_idx]
    
    factor_ganancia = 1.0 + (angulo_inclinacion / 30.0) * ganancia_relativa_30_grados[mes_idx]
    hsp_inclinado = hsp_diario * factor_ganancia
    
    energia_mes = area * eficiencia * hsp_inclinado * pr * dias
    energia_calculada_un_panel.append(energia_mes)

# CÁLCULO DE LOS 3 ESCENARIOS PARA EL REPORTE
ratios_cobertura = [consumo_ajustado[i] / energia_calculada_un_panel[i] for i in range(12)]
ratio_peor_mes = max(ratios_cobertura)
ratio_promedio = sum(ratios_cobertura) / 12

paneles_estricto = math.ceil(ratio_peor_mes)
paneles_balanceado = math.ceil((ratio_peor_mes + ratio_promedio) / 2.0)
paneles_manual = st.sidebar.number_input("Ingrese Cantidad de Paneles (Modo Manual)", min_value=1, max_value=200, value=paneles_estricto, step=1)

if criterio_dimensionamiento == "Estricto (Peor Mes)":
    paneles_necesarios = paneles_estricto
    texto_criterio = "Calculado sobre el peor mes"
elif criterio_dimensionamiento == "Balanceado (Promedio)":
    paneles_necesarios = paneles_balanceado
    texto_criterio = "Cálculo balanceado (promedio)"
else:
    paneles_necesarios = paneles_manual
    texto_criterio = "Selección manual del usuario"

generacion_sistema_mensual = [e * paneles_necesarios for e in energia_calculada_un_panel]
generacion_total_sistema = sum(generacion_sistema_mensual)
area_techo_necesaria = paneles_necesarios * area * 1.5

energia_baterias_kwh = (consumo_diario_max * dias_autonomia) / profundidad_descarga
capacidad_baterias_ah = int((energia_baterias_kwh * 1000) / voltaje_sistema)

#  ESTRUCTURA DE PESTAÑAS (TABS)
tab1, tab2 = st.tabs([" Dimensionamiento Físico y Eléctrico", "Mapa Interactivo de Riesgos"])

with tab1:
    #  VISUALIZACION DE METRICAS (KPIs) 
    st.markdown("### Resultados del Sistema")

    st.markdown(f"#### Arreglo Fotovoltaico ({modelo_seleccionado})")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Paneles Necesarios", f"{paneles_necesarios} unid.", texto_criterio)
    col2.metric("Potencia Nominal del Panel", f"{potencia_panel_w} W", f"Area: {area} m2 | Efic: {eficiencia*100}%", delta_color="off")
    col3.metric("Potencia Total Instalada", f"{(paneles_necesarios * potencia_panel_w / 1000):.2f} kWp", "Potencia Pico del Sistema")
    col4.metric("Area Minima de Instalacion", f"{area_techo_necesaria:.1f} m2", "Incluye pasillos de sombra")

    st.markdown("#### Banco de Baterias (Almacenamiento)")
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Capacidad Total de Energia", f"{energia_baterias_kwh:.1f} kWh", f"Para {dias_autonomia} dias sin sol")
    col6.metric("Capacidad en Amperios", f"{capacidad_baterias_ah} Ah", f"Sistema a {voltaje_sistema}V")
    col7.metric("Demanda Anual Real", f"{consumo_anual_real:.0f} kWh/año", "Ajustado por CAMMESA", delta_color="inverse")
    col8.metric("Generacion del Sistema", f"{generacion_total_sistema:.1f} kWh/año", f"Excedente: {generacion_total_sistema - consumo_anual_real:.1f} kWh")

    st.markdown("---")

    #  GRAFICO INTERACTIVO 
    fig, ax = plt.subplots(figsize=(12, 6))

    barras = ax.bar(nombres_meses, generacion_sistema_mensual, color='#3498db', edgecolor='black', label="Generación Proyectada", alpha=0.7)

    ax.plot(nombres_meses, consumo_ajustado, color='#e74c3c', linewidth=3, marker='o', linestyle='-', label="Demanda Real (CAMMESA)")
    ax.plot(nombres_meses, [consumo_mensual]*12, color='black', linewidth=1.5, linestyle=':', label="Demanda Teórica Plana")

    brecha = np.array(generacion_sistema_mensual) - np.array(consumo_ajustado)
    indice_peor_mes = int(np.argmin(brecha))

    for i, barra in enumerate(barras):
        if brecha[i] < 0:
            barra.set_color('#c0392b')
            barra.set_edgecolor('black')
        elif i == indice_peor_mes:
            barra.set_color('#f39c12')
            barra.set_edgecolor('black')

    max_y = max(max(generacion_sistema_mensual), max(consumo_ajustado)) * 1.3
    ax.set_ylim(0, max_y)

    for barra in barras:
        yval = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2, yval + (max_y * 0.02), f'{yval:.0f}', ha='center', fontsize=9, fontweight='bold')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, frameon=False)
    ax.set_title(f'Balance Energético ({paneles_necesarios} Paneles a {angulo_inclinacion}°) - {ciudad_seleccionada.upper()}', fontsize=14, fontweight='bold', pad=40)
    ax.set_ylabel('Energía (kWh/mes)', fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.4)

    st.pyplot(fig)

    #  MODULO DE REPORTES 
    st.markdown("---")
    st.markdown("### Exportación de Resultados")

    pdf_bytes = generar_informe_pdf(
        ciudad=ciudad_seleccionada,
        consumo=consumo_mensual,
        modelo=modelo_seleccionado,
        inclinacion=angulo_inclinacion,
        bateria_ah=capacidad_baterias_ah,
        voltaje=voltaje_sistema,
        dias=dias_autonomia,
        pan_est=paneles_estricto,
        pan_bal=paneles_balanceado,
        pan_man=paneles_manual,
        mes_critico=indice_peor_mes + 1
    )

    st.download_button(
        label="Descargar Informe Técnico (PDF)",
        data=pdf_bytes,
        file_name=f"Dimensionamiento_{ciudad_seleccionada}.pdf",
        mime="application/pdf"
    )

with tab2:
    st.markdown("### Explorador Espacial: Mapa Federal de Riesgos")
    if RUTA_MAPA_HTML.exists():
        with open(RUTA_MAPA_HTML, 'r', encoding='utf-8') as f:
            html_data = f.read()
        # Renderiza el mapa usando el componente HTML de Streamlit
        components.html(html_data, height=650, scrolling=True)
    else:
        st.info(" No se encontró el mapa interactivo. Asegúrese de haber ejecutado previamente el script generador de mapas.")


