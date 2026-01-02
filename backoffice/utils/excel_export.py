import io
import pandas as pd

def gerar_excel_retorno(lista_ignorados):
    """
    Gera um arquivo Excel com os registros ignorados retornados pela API.
    """
    df = pd.DataFrame(lista_ignorados)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="ignorados")
        writer.sheets["ignorados"].set_column(0, len(df.columns)-1, 25)

    output.seek(0)
    return output
