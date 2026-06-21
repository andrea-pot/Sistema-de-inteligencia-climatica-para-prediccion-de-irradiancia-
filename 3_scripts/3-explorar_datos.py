import pandas as pd
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent 
ARCHIVO_MAESTRO = BASE_DIR / "1_datos" / "procesados" / "base_climatica_maestra.csv"

def explorar_datos():
    print(f"Cargando archivo desde: {ARCHIVO_MAESTRO}\n")
    
    try:
        # Carga de la base de datos en memoria
        df = pd.read_csv(ARCHIVO_MAESTRO)
        
        #  VISTA PREVIA
        # Mostramos todas las columnas para asegurar que ciudad_id, latitud y longitud estén presentes
        print(" LAS PRIMERAS 5 FILAS ")
        pd.set_option('display.max_columns', None) 
        print(df.head())

        # INFORMACIÓN TÉCNICA
        # Verificamos los tipos de datos (Dtypes) y la cantidad de registros (aprox. 3.3M)
        print("\n INFORMACIÓN DE LAS COLUMNAS ")
        print(df.info())

        # RESUMEN ESTADÍSTICO
        #buscar  números negativos extremos o valores nulos antes de la limpieza
        print("\n RESUMEN ESTADÍSTICO GENERAL ")
        print(df.describe())
        
        # VERIFICACIÓN DE NODOS
        # Listamos las ciudades para confirmar que los 24 nodos estratégicos están presentes
        if 'ciudad_id' in df.columns:
            print("\nNODOS DETECTADOS EN EL DATASET")
            print(df['ciudad_id'].unique())
            print(f"Total de ciudades: {df['ciudad_id'].nunique()}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en {ARCHIVO_MAESTRO}.")
        print("Por favor, asegúrate de haber ejecutado primero el Script 2-unificar_datos.py.")
    except Exception as e:
        print(f"Error inesperado durante la exploración: {e}")

if __name__ == "__main__":
    explorar_datos()

