import pandas as pd
import json
from pathlib import Path

#  CONFIGURACIÓN DE RUTAS PORTABLES 
# Detecta automáticamente la raíz 'Sistema_inteligencia_climatica' sin importar la PC
BASE_DIR = Path(__file__).resolve().parent.parent 
RUTA_CAMMESA = BASE_DIR / "1_datos" / "crudos" / "cammesa" / "demanda_cammesa.csv"

print(f"-> Procesando huella estacional de CAMMESA desde: {RUTA_CAMMESA}")

try:
    #  CARGA Y LIMPIEZA DE DATOS 
    
    df = pd.read_csv(RUTA_CAMMESA, skiprows=4, sep=';', encoding='latin-1', decimal=',')
    
    # Limpieza de nombres de columnas y conversión de fechas
    df.columns = df.columns.str.strip()
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)

    # Filtro del año 2023 para establecer la base 
    df_modelo = df[df['Fecha'].dt.year == 2023].copy()
    df_modelo['Mes_Num'] = df_modelo['Fecha'].dt.month

    # Definición de las 9 regiones operativas según CAMMESA 
    regiones = [
        'GRAN BS.AS.', 'BUENOS AIRES', 'CENTRO', 'LITORAL', 
        'CUYO', 'NOROESTE', 'NORESTE', 'COMAHUE', 'PATAGONICA'
    ]

    #  CÁLCULO DE LA HUELLA ESTACIONAL 
    # El sistema calcula el promedio mensual y normaliza por el mes de menor consumo 
    demanda_mensual = df_modelo.groupby('Mes_Num')[regiones].mean()
    
    # Cada coeficiente se obtiene dividiendo la demanda del mes por la demanda del mes mínimo en el año, lo que refleja la estacionalidad relativa
    huella_estacional = (demanda_mensual / demanda_mensual.min()).round(2)

    #  SALIDA DE RESULTADOS 
    # Este diccionario es el insumo para el ajuste dinámico de la demanda del usuario 
    print("\n PROCESO EXITOSO. ESTE DICCIONARIO VA AL SCRIPT 13 (HUELLAS_CAMMESA):")
    print(json.dumps(huella_estacional.to_dict('list'), indent=4))

except FileNotFoundError:
    print(f"ERROR: No se encontró el archivo en {RUTA_CAMMESA}.")
except Exception as e:
    print(f"ERROR INESPERADO: {e}")
