import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

try:
    import cartopy.crs as ccrs
    from cartopy import feature as cfeature
except ImportError as e:
    ccrs = None
    cfeature = None
    CARTOPY_IMPORT_ERROR = e

from pykrige.ok import OrdinaryKriging

#  CONFIGURACIÓN DE RUTAS ABSOLUTAS
BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVO_LIMPIO = BASE_DIR / "1_datos" / "procesados" / "base_climatica_limpia.csv"
OUTPUT_PATH = BASE_DIR / "4_salidas" / "mapas_mensuales"

#  DICCIONARIO DE COORDENADAS
COORDS = {
    "jujuy": {"lat": -24.20, "lon": -65.30}, "salta": {"lat": -24.80, "lon": -65.40},
    "san_antonio_cobres": {"lat": -24.22, "lon": -66.32}, "formosa": {"lat": -26.20, "lon": -58.20},
    "chaco": {"lat": -27.50, "lon": -59.00}, "santiago_del_estero": {"lat": -27.80, "lon": -64.30},
    "posadas": {"lat": -27.37, "lon": -55.90}, "la_quiaca": {"lat": -22.10, "lon": -65.60},
    "san_juan": {"lat": -31.50, "lon": -68.50}, "mendoza": {"lat": -32.90, "lon": -68.80},
    "la_rioja": {"lat": -29.41, "lon": -66.85}, "malargue": {"lat": -35.47, "lon": -69.58},
    "cordoba": {"lat": -31.40, "lon": -64.20}, "santa_fe": {"lat": -31.60, "lon": -60.70},
    "rosario": {"lat": -32.95, "lon": -60.66}, "amba": {"lat": -34.60, "lon": -58.40},
    "mar_del_plata": {"lat": -38.00, "lon": -57.55}, "buenos_aires_sur": {"lat": -38.00, "lon": -61.50},
    "la_pampa": {"lat": -36.62, "lon": -64.29}, "neuquen": {"lat": -38.95, "lon": -68.06},
    "bariloche": {"lat": -41.13, "lon": -71.31}, "rio_gallegos": {"lat": -51.62, "lon": -69.22},
    "comodoro_rivadavia": {"lat": -45.87, "lon": -67.48}, "ushuaia": {"lat": -54.80, "lon": -68.30}
}

NOMBRES_MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def generar_atlas_final():
    print("=== INICIANDO GENERACIÓN DE MAPAS (KRIGING ORDINARIO) ===")
    
    if not ARCHIVO_LIMPIO.exists():
        print(f"Error: No se encontró la base limpia en {ARCHIVO_LIMPIO}")
        return

    # Carga de la base de datos 
    df = pd.read_csv(ARCHIVO_LIMPIO)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.month
    
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Definición de la malla de alta resolución para Argentina
    grid_lon = np.linspace(-74, -53, 150)
    grid_lat = np.linspace(-55, -22, 150)

    for m_num, m_name in NOMBRES_MESES.items():
        print(f"-> Procesando {m_name}...")
        
        # CÁLCULO TÉCNICO: (Media horaria * 24h) / 1000 = kWh/m2-día [3]
        df_mes = df[df['mes'] == m_num].groupby('ciudad_id')['radiacion_solar(ALLSKY)'].mean().reset_index()
        df_mes['valor_final'] = (df_mes['radiacion_solar(ALLSKY)'] * 24) / 1000
        
        lons, lats, valores = [], [], []
        for _, row in df_mes.iterrows():
            cid = str(row['ciudad_id']).lower().strip()
            if cid in COORDS:
                lons.append(COORDS[cid]['lon'])
                lats.append(COORDS[cid]['lat'])
                valores.append(row['valor_final'])
        
        if len(valores) < 3:
            continue

        try:
            # Interpolación geoestadística
            OK = OrdinaryKriging(lons, lats, valores, variogram_model='linear', verbose=False)
            z, _ = OK.execute('grid', grid_lon, grid_lat)
            
            # Configuración visual del mapa
            fig = plt.figure(figsize=(10, 12))
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.set_extent([-75, -50, -56, -21])
            ax.add_feature(cfeature.COASTLINE, linewidth=1)
            ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.7)
            ax.add_feature(cfeature.LAND, facecolor='whitesmoke')
            
            lon_grid, lat_grid = np.meshgrid(grid_lon, grid_lat)
            
            # Escala de 0.5 kWh/m2-día
            niveles = np.arange(0, 9.5, 0.5) 
            
            #  Contorno con relleno (Colores)
            mapa_relleno = ax.contourf(lon_grid, lat_grid, z, levels=niveles, cmap='YlOrRd', alpha=0.8)
            
            #  Isolíneas de alta visibilidad (Negro sólido)
            lineas = ax.contour(
                lon_grid, lat_grid, z, 
                levels=niveles, 
                colors='black', 
                linewidths=1.2, 
                alpha=1.0
            )
            
            #  Etiquetas de valor (Negrita y legibles)
            etiquetas = plt.clabel(
                lineas, 
                inline=True, 
                fontsize=10, 
                fmt='%1.1f', 
                colors='black',
                use_clabeltext=True
            )
            
            # Forzar negrita en cada etiqueta de texto
            for l in etiquetas:
                l.set_fontweight('bold')
            
            # Barra de color con pasos de 0.5
            plt.colorbar(mapa_relleno, label='kWh/m2-día', shrink=0.7, ticks=niveles)
            plt.title(f"Atlas Digital de Irradiación - {m_name}\nEscala: pasos de 0.5 kWh/m2-día", fontsize=14, fontweight='bold')
            
            # Guardado en 300 DPI 
            nombre_archivo = f"mapa_kriging_{m_num:02d}_{m_name.lower()}.png"
            plt.savefig(OUTPUT_PATH / nombre_archivo, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"    Mapa guardado: {nombre_archivo}")
            
        except Exception as e:
            print(f"    Error en {m_name}: {e}")

if __name__ == "__main__":
    generar_atlas_final()
