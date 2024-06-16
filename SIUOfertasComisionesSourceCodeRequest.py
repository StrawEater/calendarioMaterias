import requests
from bs4 import BeautifulSoup

# TODO VER COMO HACER PARA CAMBIAR DE CARRERA
# AHORA EMPIEZA COMO LA CARRERA DEFAULT, PERO DEBERIAMOS USAL "OTRAS MATERIAS"

# TODO VER COMO HACER PARA CAMBIAR A MODO DOCENTE, DEBERIA SER DE LA MISMA FORMA QUE LO ANTERIOR

#INFO A RELLENAR ANTES DE EJECUTAR EL CODIGO
usuario = "USUARIO"
password = "CONTRASEÑA"
id_carrera = "ID" #26 el de otras carreras


#Paginas de Login, de info_comisiones y de cambio de carrera
login_url = "https://inscripciones.exactas.uba.ar:443/autogestion/acceso?auth=form"
info_url = "https://inscripciones.exactas.uba.ar/autogestion/oferta_comisiones/"
cambio_carrera_url = f"https://inscripciones.exactas.uba.ar/autogestion/acceso/cambiar_carrera?id={id_carrera}&op=inicio_alumno"




# Verifica que se haya cambiado las info necesaria antes de seguir ejecutando el codigo 
if usuario == "USUARIO" or password == "CONTRASEÑA" or id_carrera == "ID":
    print("Error: Se debe cambiar el usuario, contraseña e ID para ingresar")
else:
    # Payload con la información de inicio de sesión
    payload = {
        "usuario": usuario,
        "password": password
    }

    # Al crear la sesion, mantengo las cookies
    session = requests.Session()

    # Realizo una solicitud para entrar a la pagina, iniciando sesion
    login_response = session.post(login_url, data=payload)
    
    # Verifico Si la pagina esta online
    if login_response.status_code == 200:
        print("Inicio de sesión exitoso y página accesible.")
        
        # Cambio de carrera al ID correspondiente y mantengo la info
        cambio_carrera_response = session.get(cambio_carrera_url)

        #Verifico si la pagina esta online
        if cambio_carrera_response.status_code == 200:
            print("Cambio de carrera exitoso.")
            
            # Accedo a la oferta de comisiones
            info_response = session.get(info_url)
            
            #Verifico si la pagina esta online
            if info_response.status_code == 200:
                # Parseo el contenido HTML
                soup = BeautifulSoup(info_response.content, 'html.parser')
                
                
                content = soup.prettify()

                # Guardo el contenido en un archivo de texto
                with open("pagina_info_comisiones.html", "w", encoding="utf-8") as file:
                    file.write(content)
            
                print("Contenido de la oferta de comisiones guardado en 'pagina_info_comisiones.html' ")
            else:
                print(f"Error al acceder a la oferta de comisiones. {info_response.status_code}")
        else:
            print(f"Error al cambiar de carrera. {cambio_carrera_response.status_code}")
    else:
        print(f"Error al iniciar sesión. {login_response.status_code}")
