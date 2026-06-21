import pandas as pd
from pathlib import Path
import time


BASE_DIR = Path(__file__).resolve().parent.parent
CARPETA_CRUDOS = BASE_DIR / "1_datos" / "crudos"
CARPETA_PROCESADOS = BASE_DIR / "1_datos" / "procesados"

def unificar_archivos():
    print("=== INICIANDO UNIFICACIÓN DE DATOS ===")
    tiempo_inicio = time.time()
    
    # Creamos la carpeta de destino si no existe
    CARPETA_PROCESADOS.mkdir(parents=True, exist_ok=True)
    
    # Buscamos todos los archivos CSV en la carpeta de crudos
    archivos = list(CARPETA_CRUDOS.glob("*.csv"))
    
    if not archivos:
        print(f"Error: No se encontraron archivos en {CARPETA_CRUDOS}")
        return

    print(f"-> Detectados {len(archivos)} archivos. Consolidando...")
    
    # Lista para almacenar los DataFrames
    lista_df = []
    
    for f in archivos:
        # Leemos cada archivo manteniendo las columnas originales (incluyendo timestamp)
        temp_df = pd.read_csv(f)
        lista_df.append(temp_df)
        
    # Concatenación de los 3.3 millones de registros
    df_final = pd.concat(lista_df, ignore_index=True)
    
    # Guardado de la base maestra ()
    archivo_salida = CARPETA_PROCESADOS / "base_climatica_maestra.csv"
    df_final.to_csv(archivo_salida, index=False)
    
    duracion = time.time() - tiempo_inicio
    print(f"=== UNIFICACIÓN FINALIZADA EN {duracion:.2f} SEGUNDOS ===")
    print(f"Archivo generado: {archivo_salida}")
    print(f"Total de registros consolidados: {len(df_final)}")

if __name__ == "__main__":
    unificar_archivos()