import pandas as pd
import numpy as np
import pathlib
import time
import sys
from pathlib import Path

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
ARCHIVO_ENTRADA = BASE_DIR / "1_datos" / "procesados" / "base_climatica_maestra.csv"
ARCHIVO_SALIDA = BASE_DIR / "1_datos" / "procesados" / "base_climatica_limpia.csv"

# Se importa el mapeo oficial para vincular ciudades con regiones de CAMMESA
sys.path.append(str(BASE_DIR))
try:
    from configuracion_maestra import mapeo_coordenadas as MAPEO_REGIONES
except ImportError:
    print("Error: No se encontró configuracion_maestra.py en la raíz del proyecto.")
    sys.exit(1)

def limpiar_y_formatear():
    print("\n INICIANDO LIMPIEZA, REGIONALIZACIÓN Y FORMATO ")
    tiempo_inicio = time.time()
    
    if not ARCHIVO_ENTRADA.exists():
        print(f"Error: No existe el archivo maestro en {ARCHIVO_ENTRADA}")
        return

    # Carga de la base consolidada (3.3M de registros)
    df = pd.read_csv(ARCHIVO_ENTRADA)

    #  FORMATEO DE FECHAS Y HORAS
    # Corrección del formato NASA (YYYYMMDDHH) 
    df['fecha_hora'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H', errors='coerce')
    df = df.sort_values(['ciudad_id', 'fecha_hora'])
    
    # Desglose temporal para análisis de estacionalidad y ciclos solar
    df['fecha'] = df['fecha_hora'].dt.date
    df['hora'] = df['fecha_hora'].dt.hour

    #  TRATAMIENTO DE OUTLIERS FÍSICOS
    # Identificación y remoción de códigos de error de la NASA (-999)
    columnas_clima = ['ALLSKY_SFC_SW_DWN', 'T2M', 'WS10M', 'CLOUD_AMT', 'RH2M']
    for col in columnas_clima:
        df.loc[df[col] < -50, col] = np.nan 

    #  CORRECCIÓN DE RADIACIÓN NOCTURNA
    # Forzamos a 0 la radiación en horas sin sol (20hs a 06hs) para evitar 
    # que la interpolación genere energía artificial durante la noche
    condicion_noche = (df['hora'] >= 20) | (df['hora'] <= 6)
    df.loc[condicion_noche, 'ALLSKY_SFC_SW_DWN'] = 0

    #  INTERPOLACIÓN LINEAL POR CIUDAD
    # Garantiza una serie temporal continua (0.0% de baches) para el modelo SARIMAX
    df[columnas_clima] = df.groupby('ciudad_id')[columnas_clima].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both').ffill().bfill()
    )

    #  ASEGURAR COHERENCIA FÍSICA
    # Evitamos valores negativos en variables que por naturaleza son >= 0
    for col in ['ALLSKY_SFC_SW_DWN', 'WS10M', 'RH2M']:
        df[col] = df[col].clip(lower=0)

    #  REGIONALIZACIÓN (Lógica CAMMESA)
    # Vinculamos cada nodo con su región operativa (GBA, CUYO, NOA, etc.)
    df['ciudad_id'] = df['ciudad_id'].str.lower().str.strip()
    df['region'] = df['ciudad_id'].map(MAPEO_REGIONES)

    #  RENOMBRADO DE COLUMNAS (Estándar del Dashboard y SARIMAX)
    df = df.rename(columns={
        'ALLSKY_SFC_SW_DWN': 'radiacion_solar(ALLSKY)',
        'T2M': 'temperatura_media(T2M)',
        'WS10M': 'velocidad_viento(WS10M)',
        'CLOUD_AMT': 'nubosidad_promedio(CLOUD_AMT)',
        'RH2M': 'humedad_relativa(RH2M)'
    })

    #  REORDENAMIENTO ESTRUCTURAL
    orden = ['ciudad_id', 'region', 'fecha', 'hora', 'radiacion_solar(ALLSKY)', 
             'temperatura_media(T2M)', 'velocidad_viento(WS10M)', 
             'nubosidad_promedio(CLOUD_AMT)', 'humedad_relativa(RH2M)']
    
    df_final = df[orden]

    #  GUARDADO Y AUDITORÍA FINAL
    df_final.to_csv(ARCHIVO_SALIDA, index=False)
    
    duracion = time.time() - tiempo_inicio
    nulos_finales = df_final.isnull().sum().sum()
    meses_detectados = pd.to_datetime(df_final['fecha']).dt.month.nunique()

    
    print(f"Estado Final -> Nulos: {nulos_finales} | Meses detectados: {meses_detectados}/12")
    print(f"Archivo guardado exitosamente en: {ARCHIVO_SALIDA}")

if __name__ == "__main__":
    limpiar_y_formatear()
    






































































