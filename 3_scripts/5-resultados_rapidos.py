import pandas as pd
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVO_LIMPIO = BASE_DIR / "1_datos" / "procesados" / "base_climatica_limpia.csv"
CARPETA_SALIDAS = BASE_DIR / "4_salidas" / "ANALISIS_EDA"

def obtener_records_climaticos():
    """
    Analiza la base de datos para identificar los extremos historicos de 15 años.
    Estos valores validan los limites operativos de los paneles y estructuras.
    """
    print("-> Leyendo la base limpia para detectar records historicos...")
    
    # Verificacion de existencia del archivo
    if not ARCHIVO_LIMPIO.exists():
        print(f"Error: No se encontro el archivo en {ARCHIVO_LIMPIO}")
        print("Asegurate de haber ejecutado primero el Script 4-limpiar_datos.py")
        return

    # Carga de datos procesados (3.3 millones de registros)
    df = pd.read_csv(ARCHIVO_LIMPIO)
    
    # Nombres de columnas estandarizados 
    COL_TEMP = 'temperatura_media(T2M)'
    COL_VIENTO = 'velocidad_viento(WS10M)'
    COL_CIUDAD = 'ciudad_id'
    COL_FECHA = 'fecha'

    print("\n=== [ RESULTADOS DE EXTREMOS CLIMATICOS ] ===")

    #  Busqueda de Maximo Calor (Critico para perdidas por coeficiente termico)
    idx_calor = df[COL_TEMP].idxmax()
    reg_calor = df.loc[idx_calor]
    print(f"-> MAXIMO CALOR: {reg_calor[COL_TEMP]} C en {reg_calor[COL_CIUDAD].upper()} el {reg_calor[COL_FECHA]}")

    
    
    idx_frio = df[COL_TEMP].idxmin()
    reg_frio = df.loc[idx_frio]
    print(f"-> MAXIMO FRIO: {reg_frio[COL_TEMP]} C en {reg_frio[COL_CIUDAD].upper()} el {reg_frio[COL_FECHA]}")

   
   
    idx_viento = df[COL_VIENTO].idxmax()
    reg_viento = df.loc[idx_viento]
    print(f"-> MAXIMO VIENTO: {reg_viento[COL_VIENTO]} m/s en {reg_viento[COL_CIUDAD].upper()} el {reg_viento[COL_FECHA]}")

    #  GUARDADO DE REPORTE EN CARPETA DE SALIDAS
    # Creamos la subcarpeta ANALISIS_EDA si no existe para mantener el orden
    CARPETA_SALIDAS.mkdir(parents=True, exist_ok=True)
    reporte_path = CARPETA_SALIDAS / "records_climaticos_argentina.txt"
    
    with open(reporte_path, "w") as f:
        f.write("=== REPORTE DE RECORDS CLIMATICOS (NASA POWER 2010-2025) ===\n")
        f.write(f"MAX CALOR: {reg_calor[COL_TEMP]} C | Ciudad: {reg_calor[COL_CIUDAD]} | Fecha: {reg_calor[COL_FECHA]}\n")
        f.write(f"MAX FRIO: {reg_frio[COL_TEMP]} C | Ciudad: {reg_frio[COL_CIUDAD]} | Fecha: {reg_frio[COL_FECHA]}\n")
        f.write(f"MAX VIENTO: {reg_viento[COL_VIENTO]} m/s | Ciudad: {reg_viento[COL_CIUDAD]} | Fecha: {reg_viento[COL_FECHA]}\n")
        f.write("\nNota: Datos utilizados para el dimensionamiento robusto del sistema fotovoltaico.")
    
    print(f"\nReporte de auditoria guardado exitosamente en: {reporte_path}")

if __name__ == "__main__":
    obtener_records_climaticos()






















