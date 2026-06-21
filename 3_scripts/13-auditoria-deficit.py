import pandas as pd
from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent.parent 
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

try:
    from configuracion_maestra import mapeo_coordenadas, HUELLAS_CAMMESA
except ImportError:
    print("ERROR: No se encontro 'configuracion_maestra.py'.")
    sys.exit(1)

ARCHIVO_MAESTRO = BASE_DIR / "1_datos" / "procesados" / "base_climatica_limpia.csv"
ARCHIVO_RESULTADO = BASE_DIR / "4_salidas" / "matriz_riesgo_energetico.csv"

#  DICCIONARIO DE AUTONOMÍA SUGERIDA 
# Estos valores representan los dias necesarios para cubrir baches criticos por zona
AUTONOMIA_POR_ZONA = {
    "ushuaia": 5, "rio_gallegos": 5, # Valores acotados para viabilidad economica
    "bariloche": 4, "comodoro_rivadavia": 4,
    "neuquen": 3, "la_pampa": 3, "buenos_aires_sur": 3, "amba": 3, 
    "rosario": 3, "santa_fe": 3, "mar_del_plata": 3, "santiago_del_estero": 3,
    "posadas": 2, "chaco": 2, "formosa": 2,
    "cordoba": 2, "mendoza": 2, "san_juan": 2,
    "malargue": 2, "la_rioja": 2,
    "jujuy": 1, "la_quiaca": 1, "san_antonio_cobres": 1, "salta": 1
}

def ejecutar_auditoria_con_autonomia():
    try:
        print(f"-> Iniciando Auditoria con Sugerencia de Autonomia.")
        df = pd.read_csv(ARCHIVO_MAESTRO)
        df['month'] = pd.to_datetime(df['fecha']).dt.month
        
        res = []
        for ciudad, datos in df.groupby('ciudad_id'):
            ciudad_key = ciudad.lower().strip()
            reg = mapeo_coordenadas.get(ciudad_key, 'CENTRO')
            
            # Calculo de oferta mensual promedio
            oferta = datos.groupby('month')['radiacion_solar(ALLSKY)'].mean()
            o_min = oferta.min()
            
            # Obtener autonomia sugerida del estudio de persistencia 
            # Si no esta en el diccionario, aplicamos el estandar de seguridad de 3 dias 
            dias_sugeridos = AUTONOMIA_POR_ZONA.get(ciudad_key, 3)
            
            res.append({
                'nodo_id': ciudad.upper(),
                'region_operativa': reg,
                'oferta_critica_w': round(o_min, 2),
                'autonomia_sugerida_dias': dias_sugeridos,
                'estado_seguridad': "SEGURO" if dias_sugeridos <= 3 else "RIESGO_ALTO"
            })

        # Guardado de la matriz expandida
        df_final = pd.DataFrame(res)
        df_final.to_csv(ARCHIVO_RESULTADO, index=False)
        
        print(f"\nMATRIZ GENERADA: Se incluyo columna de autonomia por zona.")
        print(f"-> Ubicacion: {ARCHIVO_RESULTADO}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    ejecutar_auditoria_con_autonomia()