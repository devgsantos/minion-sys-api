import psycopg2
import dotenv
import json
import os
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config')
ENV_PATH = os.path.join(CONFIG_PATH, '.env')

dotenv.load_dotenv(ENV_PATH)


def execute_query(query, params=None):
    con = psycopg2.connect(
        host=os.environ.get("db_host"),
        port=os.environ.get("db_port"),
        database=os.environ.get("db_name"),
        user=os.environ.get("db_user"),
        password=os.environ.get("db_password")
    )

    try:
        cur = con.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        if "INSERT" in query or "UPDATE" in query or "DELETE" in query:
            con.commit()
            return_rows = cur.fetchone()

            if not return_rows:
                return {
                    "status": False,
                    "message": f"Não foi encontrado nenhum dado com os filtros fornecidos."
                }  # Inserção falhou

            if len(return_rows) > 0:
                columns = [desc[0] for desc in cur.description]
                updated_dict = dict(zip(columns, return_rows))
                updated_json = json.dumps(updated_dict, indent=4, default=default_serialize)
                parsed_data = json.loads(updated_json)
            if cur.rowcount > 0:
                return {
                    "status": True,
                    "message": f"Encontrado {cur.rowcount} resultado.",
                    "data": parsed_data
                }  # Inserção bem-sucedida
            else:
                return {
                    "status": False,
                    "message": f"Encontrado {cur.rowcount} resultado."
                }  # Inserção falhou
        else:
            result_set = cur.fetchall()
            if len(result_set) > 0:
                # Mapear as colunas em um dicionário
                columns = [desc[0] for desc in cur.description]
                results = []
                for rec in result_set:
                    result_dict = dict(zip(columns, rec))
                    results.append(result_dict)

                # Converter para JSON com tratamento para objetos datetime
                json_results = json.dumps(results, indent=4, default=default_serialize)
                parsed_data = json.loads(json_results)
                return {
                        "status": True,
                        "message": f"Encontrado {len(result_set)} resultado.",
                        "data": parsed_data
                    }
            else:
                return {
                    "status": False,
                    "message": "Dados não encontrados.",
                    "data": []
                }
    except psycopg2.Error as error:
        print("Error:", error)
        return {
            "status": False,
            "message": error,
        }
    # finally:
    #     if con:
    #         con.close()

def default_serialize(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError("Type not serializable")

