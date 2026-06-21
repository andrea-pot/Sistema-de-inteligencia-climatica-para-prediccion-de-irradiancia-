import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from pathlib import Path
import warnings

# Ignorar advertencias matemáticas de la consola
warnings.filterwarnings("ignore")

#  CONFIGURACIÓN DE RUTAS
BASE_DIR = Path(__file__).resolve().parent.parent 

# Definición de rutas relativas a la raíz del proyecto
ARCHIVO_LIMPIO = BASE_DIR / "1_datos" / "procesados" / "base_climatica_limpia.csv"
OUTPUT_PREDICCIONES = BASE_DIR / "4_salidas" / "4.4_predicciones"

# Creación automática de la carpeta de salida si no existe
OUTPUT_PREDICCIONES.mkdir(parents=True, exist_ok=True)



# DICCIONARIO DE CIUDADES (24 coor)
CIUDADES = [
    "jujuy", "salta", "san_antonio_cobres", "formosa", "chaco", "santiago_del_estero",
    "posadas", "la_quiaca", "san_juan", "mendoza", "la_rioja", "malargue",
    "cordoba", "santa_fe", "rosario", "amba", "mar_del_plata", "buenos_aires_sur",
    "la_pampa", "neuquen", "bariloche", "rio_gallegos", "comodoro_rivadavia", "ushuaia"
]

MESES_PREDICCION = 12

def entrenar_red_nacional():
   
    print("[SISTEMA] INICIANDO ENTRENAMIENTO NACIONAL ")
  
    
    # Cargar base de datos
    df = pd.read_csv(ARCHIVO_LIMPIO)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['ciudad_id'] = df['ciudad_id'].astype(str).str.strip().str.lower()

    resultados_nacionales = []

    # Iterar sobre cada ciudad
    for i, ciudad in enumerate(CIUDADES, start=1):
        print(f"\n>>> [{i}/24] Procesando coordenadas: {ciudad.upper()}...")
        df_ciudad = df[df['ciudad_id'] == ciudad].copy()
        
        if df_ciudad.empty:
            print(f" [!] Sin datos para {ciudad}. Omitiendo nodo.")
            continue
            
        #  Transformación a Promedio Mensual (Clave para RAM y velocidad)
        df_ciudad['radiacion_kwh'] = df_ciudad['radiacion_solar(ALLSKY)'] / 1000
        df_ciudad.set_index('fecha', inplace=True)
        serie = df_ciudad['radiacion_kwh'].resample('MS').mean().dropna()

        # Partición Train / Test
        train = serie.iloc[:-MESES_PREDICCION]
        test = serie.iloc[-MESES_PREDICCION:]

        # Entrenamiento del Modelo SARIMAX
        modelo = SARIMAX(train, 
                         order=(1, 1, 1), 
                         seasonal_order=(1, 1, 1, 12),
                         enforce_stationarity=False, 
                         enforce_invertibility=False)
        
        resultado = modelo.fit(disp=False) 
        
        #  Predicciones y cálculo de error
        predicciones = resultado.get_forecast(steps=MESES_PREDICCION)
        pred_media = predicciones.predicted_mean
        pred_intervalos = predicciones.conf_int(alpha=0.05)

        mape = mean_absolute_percentage_error(test, pred_media) * 100
        rmse = np.sqrt(mean_squared_error(test, pred_media))
        
        print(f" [OK] Modelo ajustado. MAPE: {mape:.2f}% | RMSE: {rmse:.2f}")

        # Acumular resultados para el CSV final
        resultados_nacionales.append({
            'Ciudad': ciudad.upper(),
            'MAPE_%': round(mape, 2),
            'RMSE_kWh': round(rmse, 2)
        })

        #  Generación del Gráfico Individual
        plt.figure(figsize=(10, 5))
        
        # Mostrar datos desde 2017 para mejor visualización
        train_reciente = train[train.index >= '2017-01-01']
        
        plt.plot(train_reciente.index, train_reciente, label='Histórico (Train)', color='steelblue', linewidth=2)
        plt.plot(test.index, test, label='Realidad (Test)', color='green', linewidth=2)
        plt.plot(pred_media.index, pred_media, label='Predicción SARIMAX', color='red', linestyle='--', linewidth=2)
        
        plt.fill_between(pred_intervalos.index, 
                         pred_intervalos.iloc[:, 0], pred_intervalos.iloc[:, 1], 
                         color='red', alpha=0.15, label='Margen de Confianza (95%)')

        plt.title(f'Pronóstico Radiación Solar SARIMAX - {ciudad.upper()}\nError MAPE: {mape:.2f}%', fontweight='bold')
        plt.ylabel('Irradiación (kWh/m²/día)')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='lower left')

        # Guardar gráfico PNG
        ruta_grafico = OUTPUT_PREDICCIONES / f"pronostico_{ciudad}.png"
        plt.savefig(ruta_grafico, dpi=200, bbox_inches='tight')
        plt.close()

    #  EXPORTACIÓN DEL REPORTE NACIONAL (CSV)
    print(" [SISTEMA] EXPORTANDO REPORTE NACIONAL DE ERRORES")
    
    df_reporte = pd.DataFrame(resultados_nacionales)
    
    # Calcular promedios nacionales
    if not df_reporte.empty:
        mape_nacional = df_reporte['MAPE_%'].mean()
        rmse_nacional = df_reporte['RMSE_kWh'].mean()
        
        # Insertar fila de promedios al final del DataFrame
        df_reporte.loc['Promedio Nacional'] = ['PROMEDIO NACIONAL', round(mape_nacional, 2), round(rmse_nacional, 2)]
        
        # Exportar a CSV
        ruta_csv = OUTPUT_PREDICCIONES / "reporte_errores_sarimax.csv"
        df_reporte.to_csv(ruta_csv, index=False)
        
        print(f" -> CSV guardado con éxito en: {ruta_csv}")
        print(f" -> MAPE PROMEDIO NACIONAL: {mape_nacional:.2f}%")
    else:
        print(" [!] No se generaron resultados para exportar.")

if __name__ == "__main__":
    entrenar_red_nacional()































































































































































