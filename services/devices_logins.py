import asyncio
from collections import defaultdict
import os
from sqlalchemy import text
from database.oracle_connection import Session
from models.devices import Devices
from aiohttp import ClientSession, ClientError
from typing import List
from dotenv import load_dotenv
from middleware.logger import logger
from datetime import datetime, timedelta
import pytz
from dateutil import parser

tz_brasil = pytz.timezone("America/Sao_Paulo")

load_dotenv()
API_KEY = os.getenv("API_KEY")

# FUNÇÃO PARA CONSULTAR COLETORES NA API DO PULSUS
async def request_devices_data() -> List[dict]:
    max_retries = 5
    url = "https://api.pulsus.mobi/v1/devices"

    for attempt in range(1, max_retries + 1):
        try:
            async with ClientSession() as session:
                async with session.get(url, headers={"ApiToken": API_KEY}) as response:

                    if response.status == 200:
                        try:
                            data = await response.json()
                        except Exception as e:
                            logger.error(f"Erro ao decodificar JSON da resposta da API: {e}")
                            return []

                        coletores: List[Devices] = []
                        for item in data:
                            try:
                                coletor = Devices(**item)
                                coletores.append(coletor)
                            except Exception as e:
                                logger.error(f"Erro ao processar coletor: {e} | Dados: {item}")

                        resultado = []
                        for coletor in coletores:
                            try:
                                resultado.append({
                                    "id": coletor.id,
                                    "ip_address": coletor.ip_address,
                                    "user_first_name": coletor.user.first_name.split(' ')[0],
                                    "state": (
                                        ' '.join(coletor.user.first_name.split()[1:]) or
                                        str(coletor.user.last_name or '')
                                    ),
                                    "is_charging": coletor.is_charging,
                                    "battery_level": coletor.battery_level,
                                    "model": coletor.model,
                                    "manufacturer": coletor.manufacturer,
                                    "last_contact_at": coletor.last_contact_at
                                })
                            except Exception as e:
                                logger.error(f"Erro ao montar dados do coletor: {e} | Coletor: {coletor}")

                        logger.info("Consulta à API do Pulsus realizada com sucesso.")
                        return resultado

                    else:
                        logger.warning(f"Tentativa {attempt}: Status {response.status} ao consultar a API do Pulsus.")
        except ClientError as e:
            logger.warning(f"Tentativa {attempt}: Erro de conexão com a API do Pulsus: {e}")
        except Exception as e:
            logger.warning(f"Tentativa {attempt}: Erro inesperado: {e}")

        # Espera exponencial (1s, 2s, 4s, 8s, 16s)
        await asyncio.sleep(2 ** (attempt - 1))

    logger.error("Falha ao consultar a API do Pulsus após múltiplas tentativas.")
    return []

def parse_result(rows):
    return [dict(row._mapping) for row in rows]
def get_devices_logins():
    try:
        with Session() as session:
            # ALTERADO PARA CONSULTAR DA TABELA DE LOGS DE SESSÃO
            query = text("""
                SELECT 
                USUARIO,
                MODULO,
                OPERACAO,
                DATAHORA,
                ID_PULSUS,
                ID_COLETOR_PULSUS,
                IP
                FROM C_LOG_SESSAO_PULSUS
            """)
            return parse_result(session.execute(query))
    except Exception as e:
        logger.error(f"Erro ao consultar logins dos coletores: {e}")
        return []
    
    


async def get_merged_devices_info() -> List[dict]:
    logins = get_devices_logins()
    devices = await request_devices_data()

    logins_by_id = defaultdict(list)
    for login in logins:
        # ID DO COLETOR É O ID DO INVENTÁRIO
        id_coletor = login.get("id_coletor_pulsus")
        if id_coletor:
            logins_by_id[str(id_coletor)].append(login)

    merged_data = []
    for device in devices:
        # USER_FIRST_NAME É O ID DO COLETOR
        id_coletor = device.get("user_first_name")
        logins_do_coletor = logins_by_id.get(id_coletor, [])
    
        ultimo_login = max(logins_do_coletor, key=lambda x: x["datahora"]) if logins_do_coletor else None

        last_contact_at_raw = device.get("last_contact_at")
        last_contact_at = None
        status = "offline"

        if last_contact_at_raw:
            try:
                # Faz parsing com timezone
                dt_raw = parser.isoparse(last_contact_at_raw)
                # Converte para horário de Brasília
                dt_brasilia = dt_raw.astimezone(tz_brasil)
                last_contact_at = dt_brasilia.isoformat(timespec='seconds')

                agora = datetime.now(tz_brasil)

                if (agora - dt_brasilia) <= timedelta(minutes=30):
                    status = "online"
            except Exception as e:
                logger.warning(f"Erro ao processar last_contact_at: {e}")

        merged = {
            "id": device.get("id"),
            "ip_address": device.get("ip_address"),
            "device_id": id_coletor,
            "state": device.get("state"),
            "is_charging": device.get("is_charging"),
            "battery_level": device.get("battery_level"),
            "model": device.get("model"),
            "manufacturer": device.get("manufacturer"),
            "last_contact_at": last_contact_at,
            "status": status,
            "user": ultimo_login.get("usuario") if ultimo_login else None,
            "login_time": ultimo_login.get("datahora") if ultimo_login else None,
            "source": ultimo_login.get("modulo") if ultimo_login else None,
            "operation": ultimo_login.get("operacao") if ultimo_login else None,
        }

        merged_data.append(merged)

    return merged_data



