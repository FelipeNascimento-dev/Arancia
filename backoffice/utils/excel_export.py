import io
import pandas as pd

def gerar_excel_retorno(lista_duplicados):
    """
    Gera um arquivo Excel com os registros duplicados retornados pela API.
    """
    df = pd.DataFrame(lista_duplicados)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Duplicados")
        writer.sheets["Duplicados"].set_column(0, len(df.columns)-1, 25)

    output.seek(0)
    return output
