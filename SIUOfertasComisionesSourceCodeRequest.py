import requests
from bs4 import BeautifulSoup

# TODO VER COMO HACER PARA CAMBIAR DE CARRERA
# AHORA EMPIEZA COMO LA CARRERA DEFAULT, PERO DEBERIAMOS USAL "OTRAS MATERIAS"

# TODO VER COMO HACER PARA CAMBIAR A MODO DOCENTE, DEBERIA SER DE LA MISMA FORMA QUE LO ANTERIOR

#Paginas de Login y de info_comisiones

login_url = "https://inscripciones.exactas.uba.ar:443/autogestion/acceso?auth=form"
info_url = "https://inscripciones.exactas.uba.ar/autogestion/oferta_comisiones/"


#Info necesario segun el inspeccionar
payload = {
    "usuario": "USUARIO",
    "password": "PASSWORD"
}


# Al crear la sesion, manetengo las  cookies
session = requests.Session()


# Realizo una solicitud para entrar a la pagina, iniciando sesion
login_response = session.post(login_url, data=payload)


# Verifico Si la pagina esta online
if login_response.status_code == 200:
    print("Inicio la sesion y página ON")
    
    #Busco la pagina donde buscar la info de las comisiones
    info_response = session.get(info_url)
    
    #Parseo
    soup = BeautifulSoup(info_response.content, 'html.parser')
    
    content = soup.prettify()
    
    with open("pagina_info_comisiones.html", "w", encoding="utf-8") as file:
            file.write(content)
    
    print("Contenido de la página guardado en 'pagina_info_comisiones.txt'")
    
    #Caso contrario pido que me devuelva el error
else:
    print(f"No inicio sesion. {login_response.status_code}")