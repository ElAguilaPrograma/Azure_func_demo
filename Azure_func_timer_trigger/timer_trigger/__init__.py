import datetime
import logging
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    logging.info(f"Trigger iniciado")
    logging.info(f"Ejecutando tarea programada... {hora_actual}")
    
    if mytimer.past_due:
        logging.warning("El trigger se ha retrasado.")