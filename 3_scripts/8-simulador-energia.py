import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")


from pathlib import Path
import os


# --- CONFIGURACIÓN DE RUTAS PORTABLES ---
# Esta lógica detecta automáticamente la carpeta raíz 'Sistema_inteligencia_climatica'
# sin importar en qué PC o disco esté guardado el proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent 

# Definición de rutas relativas a la raíz
ARCHIVO_LIMPIO = BASE_DIR / "1_datos" / "procesados" / "base_climatica_limpia.csv"
OUTPUT_SIMULACION = BASE_DIR / "4_salidas" / "4.5_simulacion_energia"

# Creación segura de la carpeta de salida (si no existe)
OUTPUT_SIMULACION.mkdir(parents=True, exist_ok=True)




# 2. PARÁMETROS TÉCNICOS DEL PANEL SOLAR
AREA_PANEL_M2 = 1.94
EFICIENCIA = 0.17 
PERFORMANCE_RATIO = 0.75 
DIAS_POR_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# Red nacional completa (24 coordenadas)
CIUDADES_MUESTRA = [
    "jujuy", "salta", "san_antonio_cobres", "formosa", "chaco", "santiago_del_estero",
    "posadas", "la_quiaca", "san_juan", "mendoza", "la_rioja", "malargue",
    "cordoba", "santa_fe", "rosario", "amba", "mar_del_plata", "buenos_aires_sur",
    "la_pampa", "neuquen", "bariloche", "rio_gallegos", "comodoro_rivadavia", "ushuaia"
]

MESES_PREDICCION = 12

def simular_generacion_nacional():
    print(" INICIANDO SIMULACIÓN NACIONAL (24 coordenadas)")
    
    
    df = pd.read_csv(ARCHIVO_LIMPIO)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['ciudad_id'] = df['ciudad_id'].astype(str).str.strip().str.lower()
    
    resultados_energia = []

    for ciudad in CIUDADES_MUESTRA:
        print(f"-> Procesando nodo: {ciudad.upper()}")
        
        df_ciudad = df[df['ciudad_id'] == ciudad].copy()
        if df_ciudad.empty:
            continue
            
        df_ciudad['radiacion_kwh'] = df_ciudad['radiacion_solar(ALLSKY)'] / 1000
        df_ciudad.set_index('fecha', inplace=True)
        serie = df_ciudad['radiacion_kwh'].resample('MS').mean().dropna()
        
        modelo = SARIMAX(serie, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12), enforce_stationarity=False, enforce_invertibility=False)
        resultado = modelo.fit(disp=False)
        
        predicciones = resultado.get_forecast(steps=MESES_PREDICCION).predicted_mean
        
        for mes_idx, (fecha, hsp_promedio_horario) in enumerate(predicciones.items()):
            dias = DIAS_POR_MES[mes_idx]
            hsp_diario = hsp_promedio_horario * 24 
            
            energia_mes_kwh = AREA_PANEL_M2 * EFICIENCIA * hsp_diario * PERFORMANCE_RATIO * dias
            
            resultados_energia.append({
                'Ciudad': ciudad.upper(),
                'Mes_Prediccion': mes_idx + 1,
                'HSP_Diario_Predicho': round(hsp_diario, 2),
                'Generacion_Mensual_kWh': round(energia_mes_kwh, 2)
            })

    # Exportar el CSV con las 24 coordenadas
    df_resultados = pd.DataFrame(resultados_energia)
    df_resultados.to_csv(OUTPUT_SIMULACION / "simulacion_paneles.csv", index=False)
    
    print("\n[OK] Simulación nacional completada. CSV actualizado.")

if __name__ == "__main__":
    simular_generacion_nacional()

