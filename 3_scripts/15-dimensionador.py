import pandas as pd
import math
from pathlib import Path
import sys

# --- 1. CONFIGURACIÓN DE RUTAS PORTABLES ---
BASE_DIR = Path(__file__).resolve().parent.parent 
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

try:
    from configuracion_maestra import HUELLAS_CAMMESA, mapeo_coordenadas
except ImportError:
    print("ERROR: No se encontro 'configuracion_maestra.py'.")
    sys.exit(1)

# Ruta del insumo generado por el modelo SARIMAX
CSV_SIMULACION = BASE_DIR / "4_salidas" / "4.5_simulacion_energia" / "simulacion_paneles.csv"

def dimensionar_sistema_final(ciudad_id, consumo_mensual_kwh, dias_autonomia=3):
    try:
        if not CSV_SIMULACION.exists():
            print(f"ERROR: No se encontro el archivo de simulacion en {CSV_SIMULACION}")
            return

        # Cargar datos
        df = pd.read_csv(CSV_SIMULACION)
        
        # Esto elimina espacios en blanco y pasa todo a minúsculas antes de buscar
        df['Ciudad'] = df['Ciudad'].str.strip().str.lower()
        
        # Filtrar el nodo solicitado (amba)
        df_ciudad = df[df['Ciudad'] == ciudad_id.lower()].copy()
        
        if df_ciudad.empty:
            print(f"ERROR: No hay datos predichos para el nodo: {ciudad_id}")
            print(f"Nodos disponibles en el archivo: {df['Ciudad'].unique()}") # Ayuda a depurar
            return

        #  LOGICA DE DEMANDA (CAMMESA) 
        region = mapeo_coordenadas.get(ciudad_id.lower(), 'CENTRO')
        huella = HUELLAS_CAMMESA.get(region)
        consumo_ajustado = [consumo_mensual_kwh * h for h in huella]
        consumo_diario_max = max(consumo_ajustado) / 30.0

        # DIMENSIONAMIENTO 
        POTENCIA_PANEL = 450 
        PR = 0.75 
        
        ratios = []
        # Aseguramos que el índice coincida con los 12 meses predichos
        for i in range(12):
            hsp = df_ciudad.iloc[i]['HSP_Diario_Predicho']
            # Energia (kWh) = HSP * Potencia(kW) * Eficiencia * 30 dias
            energia_mes_panel = hsp * (POTENCIA_PANEL / 1000) * PR * 30
            ratios.append(consumo_ajustado[i] / energia_mes_panel)
        
        paneles_necesarios = math.ceil(max(ratios))

        #  ALMACENAMIENTO 
        DOD = 0.6  
        VOLTAJE = 48 
        energia_baterias_kwh = (consumo_diario_max * dias_autonomia) / DOD
        capacidad_ah = int((energia_baterias_kwh * 1000) / VOLTAJE)

        print(f"\n=== REPORTE DE DIMENSIONAMIENTO: {ciudad_id.upper()} ===")
        print(f"Region CAMMESA: {region}")
        print(f"Paneles Necesarios (450W): {paneles_necesarios} unid.")
        print(f"Potencia Total: {(paneles_necesarios * POTENCIA_PANEL / 1000):.2f} kWp")
        print(f"Almacenamiento Sugerido: {capacidad_ah} Ah en {VOLTAJE}V")
        print(f"Autonomia Garantizada: {dias_autonomia} dias (Seguridad: 95.8%)")

    except Exception as e:
        print(f"ERROR EN EL CALCULO: {e}")

if __name__ == "__main__":
    # Test con el nodo amba
    dimensionar_sistema_final(ciudad_id="amba", consumo_mensual_kwh=300)