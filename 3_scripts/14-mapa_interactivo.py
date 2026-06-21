import pandas as pd
import folium
from folium.plugins import HeatMap
from pathlib import Path
import sys



BASE_DIR = Path(__file__).resolve().parent.parent 

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

try:
    from configuracion_maestra import mapeo_coordenadas
except ImportError:
    print("ERROR: No se encontro 'configuracion_maestra.py' en la raiz.")
    sys.exit(1)

# Rutas de entrada y salida basadas en la estructura del proyecto
CSV_RIESGO = BASE_DIR / "4_salidas" / "matriz_riesgo_energetico.csv"
OUT_DIR = BASE_DIR / "4_salidas" / "riesgo_anual"
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

def generar_mapa_interactivo():
    print(f"-> Iniciando generacion de mapa de riesgo.")
    try:
        # Carga de la matriz de riesgo generada en la auditoría
        df = pd.read_csv(CSV_RIESGO)
        mapa = folium.Map(location=[-38.41, -63.61], zoom_start=4)
        heat_data = []

        for item in COORDS:
            match = df[df['nodo_id'] == item['id'].upper()]
            
            if not match.empty:
                oferta_min = float(match['oferta_critica_w'].iloc[0])
                autonomia = int(match['autonomia_sugerida_dias'].iloc[0])
                estado = str(match['estado_seguridad'].iloc[0])

                # Definir color según el riesgo (Rojo para riesgo alto en baches) 
                color_punto = 'red' if estado == "RIESGO_ALTO" else 'green'
                
                # Crear marcador interactivo
                folium.Marker(
                    location=[item['lat'], item['lon']],
                    popup=(f"<b>Nodo: {item['name']}</b><br>"
                           f"Oferta Min: {oferta_min:.1f} W<br>"
                           f"Autonomia Sugerida: {autonomia} dias<br>"
                           f"Estado: {estado}"),
                    icon=folium.Icon(color=color_punto, icon='bolt', prefix='fa')
                ).add_to(mapa)
                
                # Intensidad para el HeatMap (Inversamente proporcional a la oferta)
                intensidad = float(1 / (oferta_min + 1) * 1000)
                heat_data.append([item['lat'], item['lon'], intensidad])

        # Agregar capa de calor para visualizar la asimetría 
        HeatMap(heat_data, radius=25).add_to(mapa)
        
        ruta_salida = OUT_DIR / "mapa_riesgo_interactivo.html"
        mapa.save(ruta_salida)
        print(f"PROCESO EXITOSO. Mapa guardado en: {ruta_salida}")

    except Exception as e:
        print(f"ERROR INESPERADO: {e}")

if __name__ == "__main__":
    generar_mapa_interactivo()





































































































































































