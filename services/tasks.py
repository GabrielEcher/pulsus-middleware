import os
from sqlalchemy import text
from database.oracle_connection import Session
from models.devices import Devices
from aiohttp import ClientSession, ClientError
from typing import List
from dotenv import load_dotenv
from middleware.logger import logger
from time import sleep

load_dotenv()
API_KEY = os.getenv("API_KEY")

# FUNÇÃO PARA CONSULTAR COLETORES NA API DO PULSUS


async def request_devices_data() -> List[dict]:
    try:
        async with ClientSession() as session:
            async with session.get("https://api.pulsus.mobi/v1/devices", headers={
                "ApiToken": API_KEY
            }) as response:

                if response.status != 200:
                    logger.error(
                        f"Erro ao consultar a API do Pulsus. Status: {response.status}")
                    return []

                try:
                    data = await response.json()
                except Exception as e:
                    logger.error(
                        f"Erro ao decodificar JSON da resposta da API: {e}")
                    return []

                coletores: List[Devices] = []
                for item in data:
                    try:
                        coletor = Devices(**item)
                        coletores.append(coletor)
                    except Exception as e:
                        logger.error(
                            f"Erro ao processar coletor: {e} | Dados: {item}")

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
                            )
                        })
                    except Exception as e:
                        logger.error(
                            f"Erro ao montar dados do coletor: {e} | Coletor: {coletor}")

                logger.info("Consulta à API do Pulsus realizada com sucesso.")
                return resultado

    except ClientError as e:
        logger.error(f"Erro de conexão com a API do Pulsus: {e}")
    except Exception as e:
        logger.error(
            f"Erro inesperado ao consultar dados da API do Pulsus: {e}")

    return []

# FUNÇÃO PARA ATUALIZAR OS DADOS DOS COLETORES NO BANCO DE DADOS


async def update_devices_data() -> None:
    try:
        devices_data = await request_devices_data()
        if not devices_data:
            logger.warning(
                "Nenhum dado recebido da API. Abandonando atualização no banco.")
            return

        with Session() as session:
            try:
                logger.info(
                    "Iniciando a atualização dos dados dos coletores...")
                logger.info("Excluindo dados antigos...")
                session.execute(text("DELETE FROM COLETORES_PULSUS"))
                session.commit()
                sleep(3)
                logger.info("Dados antigos excluídos com sucesso!")

                for device in devices_data:
                    try:
                        session.execute(text("""
                        INSERT INTO COLETORES_PULSUS (
                            ID_PULSUS,
                            ID_COLETOR,
                            IP,
                            ESTADO
                        ) VALUES (
                            :id_pulsus,
                            :id_coletor,
                            :ip,
                            :estado
                        )
                        """), {
                            "id_pulsus": device["id"],
                            "id_coletor": device["user_first_name"],
                            "ip": device["ip_address"],
                            "estado": device["state"]
                        })
                        session.commit()
                    except Exception as e:
                        logger.error(
                            f"Erro ao inserir coletor no banco: {e} | Dados: {device}")
                        session.rollback()

                logger.info("Dados atualizados com sucesso!")

            except Exception as e:
                logger.error(
                    f"Erro durante a transação com o banco de dados: {e}")
                session.rollback()

    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar dados dos coletores: {e}")
