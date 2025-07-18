import io
import pandas as pd
import tempfile
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from pandas.api.types import is_datetime64_any_dtype


def generate_xlsx(data: dict):
    # 1. Criação do DataFrame
    df = pd.DataFrame(data)

    # 2. Converter colunas específicas para datetime
    # Adicione aqui os nomes reais das colunas de data/hora
    datetime_columns = ["login_time", "last_contact_at"]  # ajuste conforme seu caso
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # 3. Criação do objeto BytesIO
    output = io.BytesIO()

    # 4. Criação da pasta de trabalho do Excel
    wb = Workbook()

    # 5. Seleção da planilha ativa
    ws = wb.active

    # 6. Escrever os cabeçalhos das colunas na primeira linha
    for col_num, column_title in enumerate(df.columns, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = column_title.upper()

    # 7. Adicionar os dados linha por linha
    for row in dataframe_to_rows(df, index=False, header=False):
        ws.append(row)

    # 8. Determinar formatos numéricos com base nos tipos de dados
    number_formats = {}
    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            number_formats[col] = "dd/mm/yyyy hh:mm"
        elif df[col].dtype == "int64":
            number_formats[col] = "0"
        elif df[col].dtype == "float64":
            number_formats[col] = "0.00"
        else:
            number_formats[col] = "general"

    # 9. Aplicar os formatos nas colunas
    for idx, (col_cells, fmt) in enumerate(zip(ws.columns, number_formats.values())):
        for cell in list(col_cells)[1:]:  # Ignorar cabeçalho
            cell.number_format = fmt

    # 10. Salvar a pasta de trabalho no objeto BytesIO
    wb.save(output)

    # 11. Criar um arquivo temporário e gravar o conteúdo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp:
        temp.write(output.getvalue())
        temp_file_path = temp.name

    return temp_file_path
