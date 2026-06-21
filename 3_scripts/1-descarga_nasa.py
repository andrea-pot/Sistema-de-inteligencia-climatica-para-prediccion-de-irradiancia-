import time
from pathlib import Path
import requests
import pandas as pd

# CONFIGURACION DE RUTAS ABSOLUTAS
BASE_DIR = Path(__file__).resolve().parent.parent 
OUTPUT_DIR = BASE_DIR / "1_datos" / "crudos"

BASE_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
YEARS = range(2010, 2026)
REQUEST_DELAY_SECONDS = 1.5

COORDS = [
    {"name": "Jujuy", "id": "jujuy", "lat": -24.20, "lon": -65.30},
    {"name": "Salta", "id": "salta", "lat": -24.80, "lon": -65.40},
    {"name": "San Antonio de los Cobres", "id": "san_antonio_cobres", "lat": -24.22, "lon": -66.32},
    {"name": "Formosa", "id": "formosa", "lat": -26.20, "lon": -58.20},
    {"name": "Chaco", "id": "chaco", "lat": -27.50, "lon": -59.00},
    {"name": "Santiago del Estero", "id": "santiago_del_estero", "lat": -27.80, "lon": -64.30},
    {"name": "Posadas", "id": "posadas", "lat": -27.37, "lon": -55.90},
    {"name": "La Quiaca", "id": "la_quiaca", "lat": -22.10, "lon": -65.60},
    {"name": "San Juan", "id": "san_juan", "lat": -31.50, "lon": -68.50},
    {"name": "Mendoza", "id": "mendoza", "lat": -32.90, "lon": -68.80},
    {"name": "La Rioja", "id": "la_rioja", "lat": -29.41, "lon": -66.85},
    {"name": "Malargue", "id": "malargue", "lat": -35.47, "lon": -69.58},
    {"name": "Cordoba", "id": "cordoba", "lat": -31.40, "lon": -64.20},
    {"name": "Santa Fe", "id": "santa_fe", "lat": -31.60, "lon": -60.70},
    {"name": "Rosario", "id": "rosario", "lat": -32.95, "lon": -60.66},
    {"name": "AMBA", "id": "amba", "lat": -34.60, "lon": -58.40},
    {"name": "Mar del Plata", "id": "mar_del_plata", "lat": -38.00, "lon": -57.55},
    {"name": "Buenos Aires Sur", "id": "buenos_aires_sur", "lat": -38.00, "lon": -61.50},
    {"name": "La Pampa", "id": "la_pampa", "lat": -36.62, "lon": -64.29},
    {"name": "Neuquen", "id": "neuquen", "lat": -38.95, "lon": -68.06},
    {"name": "Bariloche", "id": "bariloche", "lat": -41.13, "lon": -71.31},
    {"name": "Rio Gallegos", "id": "rio_gallegos", "lat": -51.62, "lon": -69.22},
    {"name": "Comodoro Rivadavia", "id": "comodoro_rivadavia", "lat": -45.87, "lon": -67.48},
    {"name": "Ushuaia", "id": "ushuaia", "lat": -54.80, "lon": -68.30}
]

def descargar_y_convertir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for coord in COORDS:
        for year in YEARS:
            params = {
                "parameters": "ALLSKY_SFC_SW_DWN,T2M,WS10M,CLOUD_AMT,RH2M",
                "community": "RE", "format": "JSON", "latitude": coord["lat"],
                "longitude": coord["lon"], "start": f"{year}0101", "end": f"{year}1231"
            }
            try:
                response = requests.get(BASE_URL, params=params, timeout=30)
                if response.status_code == 200:
                    datos_json = response.json()
                    parametros = datos_json["properties"]["parameter"]
                    df = pd.DataFrame(parametros)
                    # Nombres clave para los siguientes scripts:
                    df['ciudad_id'] = coord['id']
                    df['latitud'] = coord['lat']
                    df['longitud'] = coord['lon']
                    nombre_archivo = OUTPUT_DIR / f"{coord['id']}_{year}.csv"
                    df.to_csv(nombre_archivo, index_label="timestamp")
                    print(f"Exito: {nombre_archivo}")
                time.sleep(REQUEST_DELAY_SECONDS)
            except Exception as e:
                print(f"Error en {coord['id']} {year}: {e}")

if __name__ == "__main__":
    descargar_y_convertir()














































