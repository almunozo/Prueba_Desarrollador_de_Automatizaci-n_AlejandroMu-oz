import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class DescargadorArchivos:
    """Clase para manejar descargas de archivos."""

    def __init__(self, url, output_dir="descargas"):
        self.url = url
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def descargar_archivo(self, patron, nombre_salida):
        """Descargar archivo de la página principal según un patrón en el enlace."""
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception(f"Error al acceder al sitio web: {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")
        enlace_descarga = None
        for enlace in soup.find_all("a", href=True):
            if patron in enlace["href"]:
                enlace_descarga = enlace["href"]
                break

        if not enlace_descarga:
            raise Exception("No se encontró el enlace con el patrón especificado.")

        # Construir URL completa si es relativa
        if not enlace_descarga.startswith("http"):
            enlace_descarga = f"https://www.dane.gov.co{enlace_descarga}"

        archivo_descarga = requests.get(enlace_descarga)
        ruta_salida = os.path.join(self.output_dir, nombre_salida)

        with open(ruta_salida, "wb") as archivo:
            archivo.write(archivo_descarga.content)

        return ruta_salida


class ProcesadorDatos:
    """Clase para procesar y analizar datos."""

    def __init__(self, archivo_excel, hoja):
        self.archivo_excel = archivo_excel
        self.hoja = hoja

    def procesar_datos(self):
        """Procesa los datos del archivo Excel y genera el análisis."""
        df = pd.read_excel(self.archivo_excel, sheet_name=self.hoja, header=None)
        df = df.iloc[7:].reset_index(drop=True)
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

        df["Precio total"] = df["Cantidades vendidas "] * df["Precio Reportado "]
        columnas_relevantes = ["Nombre producto", "Marca", "Cantidades vendidas ", "Precio Reportado ", "Precio total"]
        df_agrupado = df[columnas_relevantes].dropna()

        # Análisis
        productos_mas_vendidos = df_agrupado.sort_values(by="Cantidades vendidas ", ascending=False).head(10)
        total_productos_vendidos = df["Cantidades vendidas "].sum()
        total_10_mas_vendidos = productos_mas_vendidos["Cantidades vendidas "].sum()
        porcentaje_10_mas_vendidos = (total_10_mas_vendidos / total_productos_vendidos) * 100
        total_precio_todos = df["Precio total"].sum()
        total_precio_10_mas_vendidos = productos_mas_vendidos["Precio total"].sum()
        porcentaje_precio_10_mas_vendidos = (total_precio_10_mas_vendidos / total_precio_todos) * 100

        # Generar resumen
        productos_mas_vendidos = productos_mas_vendidos.drop(columns=["Cantidades vendidas "])
        return {
            "productos_mas_vendidos": productos_mas_vendidos,
            "resumen_cantidades": pd.DataFrame({
                "Descripción": [
                    "Total de productos vendidos",
                    "Total de los 10 productos más vendidos",
                    "Porcentaje de los 10 productos más vendidos"
                ],
                "Valor": [
                    total_productos_vendidos,
                    total_10_mas_vendidos,
                    f"{porcentaje_10_mas_vendidos:.2f}%"
                ]
            }),
            "resumen_precios": pd.DataFrame({
                "Descripción": [
                    "Total del precio de todos los productos vendidos",
                    "Total del precio de los 10 productos más vendidos",
                    "Porcentaje del precio de los 10 productos más vendidos respecto al total"
                ],
                "Valor": [
                    f"${total_precio_todos:,.2f}",
                    f"${total_precio_10_mas_vendidos:,.2f}",
                    f"{porcentaje_precio_10_mas_vendidos:.2f}%"
                ]
            })
        }


class GeneradorArchivos:
    """Clase para manejar la generación de archivos de salida."""

    @staticmethod
    def generar_archivos(resultados):
        """Generar archivos CSV y Excel con los resultados procesados."""
        resultados["productos_mas_vendidos"].to_csv("productos_mas_vendidos.csv", index=False)

        with pd.ExcelWriter("resumen_productos.xlsx", engine="openpyxl") as writer:
            resultados["resumen_cantidades"].to_excel(writer, sheet_name="Resumen Cantidades", index=False)
            resultados["resumen_precios"].to_excel(writer, sheet_name="Resumen Precios", index=False)


class EnvioCorreo:
    """Clase para enviar correos con archivos adjuntos."""

    @staticmethod
    def enviar_correo(remitente, contraseña, destinatario, asunto, cuerpo, archivos_adjuntos):
        try:
            mensaje = MIMEMultipart()
            mensaje["From"] = remitente
            mensaje["To"] = destinatario
            mensaje["Subject"] = asunto
            mensaje.attach(MIMEText(cuerpo, "plain"))

            for archivo in archivos_adjuntos:
                with open(archivo, "rb") as adjunto:
                    parte = MIMEBase("application", "octet-stream")
                    parte.set_payload(adjunto.read())
                encoders.encode_base64(parte)
                parte.add_header("Content-Disposition", f"attachment; filename={os.path.basename(archivo)}")
                mensaje.attach(parte)

            servidor = smtplib.SMTP("smtp.gmail.com", 587)
            servidor.starttls()
            servidor.login(remitente, contraseña)
            servidor.sendmail(remitente, destinatario, mensaje.as_string())
            servidor.quit()

            print(f"Correo enviado a {destinatario}")
        except Exception as e:
            print(f"Error al enviar correo: {e}")


# Uso de las clases
if __name__ == "__main__":
    url = "https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/precios-de-venta-al-publico-de-articulos-de-primera-necesidad-pvpapn"
    descargador = DescargadorArchivos(url)
    archivo_descargado = descargador.descargar_archivo(
        "/files/investigaciones/boletines/pvpapn/pvpapn-2021-03-18-anexo-referencias-mas-vendidas.xlsx",
        "anexo_referencias_mas_vendidas_18_03_2021.xlsx"
    )

    procesador = ProcesadorDatos(archivo_descargado, "Cantidades 1203-1603")
    resultados = procesador.procesar_datos()

    GeneradorArchivos.generar_archivos(resultados)

    EnvioCorreo.enviar_correo(
        "alejoemunoz2002@gmail.com",
        "ybqe sizu vfgk aryv",  # Contraseña de aplicación
        "almunozo@unal.edu.co",
        "Resumen en Excel y CSV",
        "Hola, adjunto los archivos Excel y CSV con los resúmenes solicitados.",
        ["resumen_productos.xlsx", "productos_mas_vendidos.csv"]
    )