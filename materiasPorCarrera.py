#IMPORTANTE: SE NECESITA TENER INSTALADO WEBDRIVER Y EL NAVEGADOR GOOGLE CHROME
#ABRE UN NAVEGADOR EXTERNO Y EL PROCESO SE DEMORA UNOS 3 O 5 MINUTOS APROX
#Librerias
from selenium import webdriver #Busca la info a tiempo real (especie de bot)
from selenium.webdriver.support.ui import Select #Sirve para utilizar los elementos de tipo Select
from selenium.webdriver.support.ui import WebDriverWait #Sirve para crear condiciones de espera
from selenium.webdriver.support import expected_conditions as EC #Sirve para esperar elementos en concreto
from selenium.webdriver.common.by import By #Sirve para buscar bajo distintos nobre y/o elementos HTML o CSS
import time
import json #Guardar contenido


#A RELLENAR (tomar el periodo lectivo correspondiente (LA PAGINA SE ACTUALIZA POR CUATRIMESTRE))
periodo = "1er. Cuatrimestre 2025"

#Se crea diccionario vacio donde se guardaran las materias segun cada carrera
materias_por_carrera = {}

# Configuro el navegador a usar (recomendable Chrome)
driver = webdriver.Chrome()
#La URL a utilizar
driver.get("https://inscripciones.exactas.uba.ar/autogestion/horarios_cursadas") #No necesita login


time.sleep(5)#Esperamos unos 5 segundos a que la pagina se cargue (NO SIRVE EL WEBDRIVERWAIT, idk)

try:
    #PRIMER FILTRO (RESPONSABILIDAD ACADEMICA)
    #esperamos 10 segundos (como maximo) para ver si aparece nuestro ID
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "formulario_filtro-ra"))
    )
    ra_filtro_element = driver.find_element(By.ID, "formulario_filtro-ra") #Obtenemos el ID de la resposabilidad academica
    ra_filtro = Select(ra_filtro_element) #Seleccionamos su filtro
    ra_filtro.select_by_visible_text("Carreras de Grado") #Vamos a la opción de Carreras de Grado
    
    time.sleep(5) #esperamos 5 segundos a que se refresque la pagina (tambien produce error si se saca la linea)
    
    #SEGUNDO FILTRO (FILTRO POR CARRERA)
    propuesta_filtro_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "formulario_filtro-carrera"))
    )
    propuesta_filtro = Select(propuesta_filtro_element)
    propuestas_carreras = propuesta_filtro.options #Obtenemos todas las opciones del filtro (o sea todas las carreras)
    
    propuestas_texto = [carrera.text for carrera in propuestas_carreras] #Obtenemos el texto asociado a cada elemnto del filtro
    
    #Iteramos por cada carrera
    for carrera in propuestas_texto:
        if carrera != "-- Seleccione --": #La 1era opción del filtro no aporta nada
            
            #Como se actualiza la pagina en cada busqueda y cambian los ID, por las dudas
            propuesta_filtro = Select(driver.find_element(By.ID, "formulario_filtro-carrera"))
            propuesta_filtro.select_by_visible_text(carrera)
            
            #TERCER FILTRO (PERIODO LECTIVO)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "formulario_filtro-periodo"))
            )
            periodoLectivo_filtro_element = driver.find_element(By.ID, "formulario_filtro-periodo")
            peridoLectivo_filtro = Select(periodoLectivo_filtro_element)
            peridoLectivo_filtro.select_by_visible_text(periodo) #variable del inicio a rellenar
            
            #Vamos a clickear el boton buscar bajo el ID boton_buscar
            boton_buscar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "boton_buscar"))
            )
            boton_buscar.click()
            
            #Esperamos que se refresque la pagina (a veces podruce error si no esperamos lo suficiente)
            time.sleep(10)
            
            #Comprobación a que aparezca el elemento
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.accordion-toggle.materia"))
            )
            
            #Buscamos todos los elementos bajo la clase accordion-toggle.materia
            materias_elements = driver.find_elements(By.CSS_SELECTOR, 'a.accordion-toggle.materia')
            
            #Obtenemos el texto asociado a cada una de las materias
            materias = [materia.text.strip() for materia in materias_elements]
            
            #La guardamos en el diccionario
            materias_por_carrera[carrera] = materias
            
        
except Exception as e:
    print(f"Se ha producido un error: {e}")
finally:
    driver.quit()

#Guardamos la info 
with open('materias_por_carrera.json', 'w', encoding='utf-8') as file:
    json.dump(materias_por_carrera, file, ensure_ascii=False, indent=4)
