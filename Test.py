import unittest
import os
import pandas as pd
from app import EnvioCorreo

class TestVerificacionArchivos(unittest.TestCase):
    def setUp(self):
        """Configura los valores esperados."""
        self.carpeta = "descargas"
        self.archivo_esperado = "anexo_referencias_mas_vendidas_18_03_2021.xlsx"

    def test_carpeta_y_archivo_existente(self):
        """Verifica si la carpeta 'descargas' y el archivo esperado existen."""
        # Verificar que la carpeta existe
        self.assertTrue(os.path.exists(self.carpeta), f"La carpeta '{self.carpeta}' no existe.")

        # Verificar que el archivo existe dentro de la carpeta
        ruta_archivo = os.path.join(self.carpeta, self.archivo_esperado)
        self.assertTrue(os.path.exists(ruta_archivo), f"El archivo '{self.archivo_esperado}' no se encuentra en la carpeta '{self.carpeta}'.")


class TestProcesadorDatos_GenerarArchivos(unittest.TestCase):
    def setUp(self):
        """Configura los nombres de los archivos generados y las condiciones esperadas."""
        # Archivos ahora están en el directorio principal del proyecto
        self.archivo_csv = "productos_mas_vendidos.csv"
        self.archivo_excel = "resumen_productos.xlsx"

    def test_archivos_generados_existen(self):
        """Verifica que los archivos generados existan."""
        self.assertTrue(os.path.exists(self.archivo_csv), f"El archivo CSV '{self.archivo_csv}' no se encontró.")
        self.assertTrue(os.path.exists(self.archivo_excel), f"El archivo Excel '{self.archivo_excel}' no se encontró.")

    def test_dimensiones_csv(self):
        """Verifica que el archivo CSV tenga dimensiones 10x4."""
        df_csv = pd.read_csv(self.archivo_csv)
        self.assertEqual(df_csv.shape, (10, 4), "El archivo CSV no tiene las dimensiones 10x4.")

    def test_hojas_excel(self):
        """Verifica que el archivo Excel tenga las hojas esperadas."""
        with pd.ExcelFile(self.archivo_excel) as excel:
            hojas = excel.sheet_names
            self.assertIn("Resumen Cantidades", hojas, "No se encontró la hoja 'Resumen Cantidades' en el archivo Excel.")
            self.assertIn("Resumen Precios", hojas, "No se encontró la hoja 'Resumen Precios' en el archivo Excel.")


import unittest
from unittest.mock import patch
import os
import tempfile
from app import EnvioCorreo  # Asegúrate de importar correctamente tu clase EnvioCorreo


class TestEnvioCorreo(unittest.TestCase):
    @patch("smtplib.SMTP")
    def test_envio_correo(self, mock_smtp):
        """Verifica que se envíe el correo con los parámetros correctos y los archivos adjuntos."""
        remitente = "alejoemunoz2002@gmail.com"
        contraseña = "ybqe sizu vfgk aryv"
        destinatario = "almunozo@unal.edu.co"
        asunto = "Resumen en Excel y CSV"
        cuerpo = "Hola, adjunto los archivos Excel y CSV con los resúmenes solicitados."

        # Crear un directorio temporal para los archivos simulados
        with tempfile.TemporaryDirectory() as temp_dir:
            archivos_adjuntos = [
                os.path.join(temp_dir, "resumen_productos.xlsx"),
                os.path.join(temp_dir, "productos_mas_vendidos.csv"),
            ]

            # Crear archivos simulados
            for archivo in archivos_adjuntos:
                with open(archivo, "w") as f:
                    f.write("Contenido de prueba")

            # Llamar a la función de envío
            EnvioCorreo.enviar_correo(remitente, contraseña, destinatario, asunto, cuerpo, archivos_adjuntos)

            # Comprobar que se creó la conexión SMTP
            mock_smtp.assert_called_with("smtp.gmail.com", 587)
            instancia_smtp = mock_smtp.return_value

            # Comprobar que se inició la sesión SMTP
            instancia_smtp.starttls.assert_called_once()
            instancia_smtp.login.assert_called_once_with(remitente, contraseña)

            # Comprobar que el correo fue enviado
            instancia_smtp.sendmail.assert_called_once()
            args, kwargs = instancia_smtp.sendmail.call_args
            self.assertEqual(args[0], remitente)
            self.assertEqual(args[1], destinatario)
            self.assertIn(asunto, args[2])  # Verifica que el asunto está en el mensaje

            # Comprobar que los archivos adjuntos están en el mensaje
            for archivo in archivos_adjuntos:
                self.assertIn(os.path.basename(archivo), args[2])


        

if __name__ == "__main__":
    unittest.main()
