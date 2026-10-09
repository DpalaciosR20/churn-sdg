from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]      # la carpeta que contiene a churn/
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
RUTA_MODELO = MODELS_DIR / "modelo.pkl"
AUC_MINIMO = 0.65

SEMILLA = 42
TEST_SIZE = 0.2
NUM_COLS = [
    "rev_Mean",         # Mean monthly revenue (charge amount)
    "mou_Mean",         # Mean number of monthly minutes of use
    "ovrrev_Mean",      # Mean overage revenue
    "comp_dat_Mean",    # Mean number of completed data calls
    "custcare_Mean",    # Mean number of customer care calls
    "phones",           # Number of handsets issued
    "months",           # Total number of months in service
    "eqpdays",          # Number of days (age) of current mobile phone
    "change_mou",       # Percentage change in monthly minutes of use vs previous three month average
    "change_rev",       # Percentage change in monthly revenue vs previous three month average
    "drop_vce_Mean",    # Mean number of dropped (failed) voice calls
    "drop_dat_Mean",    # Mean number of dropped (failed) data calls
    "drop_blk_Mean",    # Mean number of dropped or blocked calls
    "blck_vce_Mean",    # Mean number of blocked (failed) voice calls
    "blck_dat_Mean",    # Mean number of blocked (failed) data calls
    "unan_dat_Mean",    # Mean number of unanswered data calls
    "totmrc_Mean",      # Mean total monthly recurring charge
    "uniqsubs",         # Number of unique subscribers in the household
    "roam_Mean",        # Mean number of roaming calls
    "datovr_Mean",      # Mean revenue of data overage
    "da_Mean",          # Mean number of directory assisted calls
    "recv_sms_Mean",    # Mean number of received sms
    "callfwdv_Mean",    # Mean number of call forwarding calls
    "callwait_Mean",    # Mean number of call waiting calls
    "threeway_Mean",    # Mean number of three way calls
    "hnd_price",        # Current handset price
]
CAT_COLS = [
    "refurb_new",   # Handset: refurbished or new
    "infobase",     # InfoBase match
    "dualband",     # Dualband
    "asl_flag",     # Account spending limit
    "hnd_webcap",   # Handset web capability
]
HIPERPARAMETROS = {
    "learning_rate": 0.05,   # cuánto aporta cada árbol.
    "n_estimators": 300,      # el número de árboles.
    "num_leaves": 15,        # el máximo de hojas (grupos finales) por árbol. limita cuántos grupos crea el árbol.
    "max_depth": 5,          # el máximo de preguntas encadenadas desde la raíz hasta una hoja. limita qué tan específica puede ser una regla.
    "min_child_samples": 50, # ninguna hoja puede tener menos de 50 clientes. no sacar conclusiones de grupos chicos.
    "colsample_bytree": 0.8, # Usa solo el 80% de las columnas por árbol
    "reg_alpha": 0.1,        # puede llevar los valores pequeños exactamente a cero, y hace que los cortes con poca ganancia dejen de valer la pena.
    "reg_lambda": 0.5,       # encoge los valores de todas las hojas hacia cero, y encoge más a las que tienen poca evidencia
    "random_state": SEMILLA,
    "verbose": -1
}