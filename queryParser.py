import re
from bs4 import BeautifulSoup
import json

# Abrimos el archivo donde esta el Source Code de la pagina
pageFile = open("page.html", "r")
pageSource = pageFile.read()

# Regex que encuentra todo texto entre <div class="js-recuadro_periodo recuadro" ...> (incluido) y <div id="js-reporte-vacio" ... </div></div> (no incluido)
# En la pagina, cada periodo esta dentro de su propio <div> con la clase: "js-recuadro_periodo recuadro", 
# entre periodo y periodo siempre hay un <div> de reporte vacio, asi que podemos utilizar toda su definicion como finalizador
# usamos la opcion lazy de (.*?) para matchear un solo periodo y no todo dentro del inicio del primero y el finalizador del ultimo periodo

#Tenemos que formatear usando literales \\, ya que toda las informacion estar escrita en un script de una linea que escribe su contenido directamente a la pagina.
regexQueryDivPeriodo = r"(<div class=\\\"js-recuadro_periodo recuadro\\\"(.*?)>)(.*?)(?=(<div id=\\\"js-reporte-vacio\\\")(.*?)<\\/div>)"

#Conseguimos un iterador con cada match en el codigo fuente(cada <div> de periodo )
matches = re.finditer(regexQueryDivPeriodo, pageSource)

#Inicializamos un diccionario donde guardar la informacion de cada Periodo Lectivo indexeado por su id
periodosLectivosDic = {}

#Populamos el diccionario de Periodos Lectivos
for match in matches:
    
    # Formateamos el div encontrado remplazando los literales por su valor real
    # \\t -> \t | \\n -> \n | \\/ -> /
    # Tenemos el problema de los caracteres de escape como "\\u00ed" -> "\u00ed" -> í
    # TODO: hacer una funcion que remplaze los valores de los caracteres de escape (facil)
    formatedPageSourceCode = match.group().replace("\\t","\t").replace("\\n","\t").replace("\\\"","\"").replace("\\/","/")
    
    #Parseamos el codigo por BeautifulSoup 
    soup = BeautifulSoup(formatedPageSourceCode, "html.parser")
    
    periodoDic = {}
    # Inicializamos un diccionario que representara al periodo:
    # [id] : id del periodo lectivo
    # [nombre] : nombre del periodo lectivo
    # [nombre] : nombre del periodo lectivo
    # [actividades] : diccionario con la cantidad de actividades del periodo y la informacion de cada una
    
    # Parseamos el div principal, donde se encuentra toda la informacion del periodo
    periodo = soup.find("div", class_="js-recuadro_periodo recuadro")
    
    # Guardamos el id del periodo, el cual esta como atributo personalizado
    periodoDic["id"] = periodo["periodo"]
    
    # Buscamos el nombre del periodo
    periodoNombre = periodo.find("h3")
    periodoNombreText = periodoNombre.text
    #El texto esta formateado como: "Período lectivo: NOMBRE"
    #Manipulamos el string para solo quedarnos con "NOMBRE"
    periodoNombreText = periodoNombreText[periodoNombreText.rfind(":") + 1 : ].strip()
    # Guardamos el nombre del periodo
    periodoDic["nombre"] = periodoNombreText
    
    #Inicializamos el diccionario para guardar la informacion de las actividades que suceden en el periodo lectivo
    # [cantidad] : Cantidad de actividades que forman parte de este periodo lectivo
    # [actividades] : Diccionario con la informacion de cada actividad indexeado por el id de la actividad
    actividadesDic = {}
    
    # Cada actividad es contenida en un <div> con la clase "js-recuadro_actividad"
    # Encontramos cada uno de estos <div> dentro del periodo, consiguiendo una lista de cada actividad
    actividades = periodo.find_all("div",class_="js-recuadro_actividad")
    
    # Guardamos la cantidad de actividades e inicializamos el diccionario de actividades
    actividadesDic["cantidad"] = len(actividades)
    actividadesDic["actividades"] = {}
    
    # Recorremos cada <div> actividad y populamos el diccionario de actividades
    for actividad in actividades:
        
        #Inicializamos un diccionario para representar cada actividad
        # [id] : id de la actividad
        # [nombre] : nombre de la actividad
        # [comisiones] : Diccionario con la informacion de cada comision de la actividad, indexeado por su nombre
        actividadDic = {}
        
        #Conseguimos Nombre de la actividad por un atributo personalizado del <div> de actividad
        #el atributo esta formateado como: "NOMBRE (ID)"
        nombreActividad = actividad["actividad"]
        
        #Manipulamos el string para aislar ID
        idActividad = nombreActividad[nombreActividad.rfind("(") + 1 : -1]
        
        #Guardamos el id y nombre de la actividad
        actividadDic["id"] = idActividad 
        actividadDic["nombre"] = nombreActividad
        
        #Inicializamos el diccionario que representar cada comision de la actividad
        actividadDic["comisiones"] = {}

        # Cada comision esta contenida en su propia <table> con la clases "table table-bordered table-condensed comision"
        # Encontramos cada tabla de comision y las parseamos
        tablasInformacionComisiones = actividad.find_all("table", class_="table table-bordered table-condensed comision")
        for tablaComision in tablasInformacionComisiones:
            #Inicializamos el diccionario que representara a las comisiones
            # [nombre] : nombre de la comision
            # [turno] : turno de la comision
            # [instancia] : tipo de comision
            # [ubicacion] : ubicacion de la comision
            # [observacion] : observacion OPCIONAL de la comision
            # [subcomisiones] : Diccionario con la informacion de cada subcomision, indexeado por su nombre
            comisionDir = {}
            
            #Inicializamos el diccionario que representara cada subcomision de la comision
            comisionDir["subcomisiones"] = {}
            
            # La informacion de las subcomisiones no estan contenidas en si misma como lo estaban el resto de objetos
            # Cada Tabla de informacion esta formateada de la siguiente forma:
            # <tr>
            
            ultimaSubComision = ""
            comisionEncontrada = False
            
            for filasComisionesInfo in tablaComision.find_all("tr"):
                    
                    if filasComisionesInfo["class"] == ["comision"]:
                        
                        if(not(comisionEncontrada)):
                            columnasInformacionComision = list(filasComisionesInfo.children)
                            
                            columnaNombreComision = columnasInformacionComision[0]
                            columnaTurnoComision = columnasInformacionComision[1]
                            columnaInfoComision = columnasInformacionComision[2]                            

                            nombreComision = columnaNombreComision.find("h5").text
                            nombreComision = nombreComision[nombreComision.find("n:") + 2 : ].strip()
                            comisionDir["nombre"] = nombreComision
                    
                            turnoComision = columnaTurnoComision.find("span").text
                            turnoComision = turnoComision[turnoComision.find(":") + 2 : ].strip()
                            comisionDir["turno"] = turnoComision

                            comisionInstancia, comisionUbicacion = columnaInfoComision.find_all("span")
                                
                            comisionInstanciaText = comisionInstancia.text
                            comisionInstanciaText = comisionInstanciaText[comisionInstanciaText.find(":") + 2 : ].strip()
                            comisionDir["instancia"] = comisionInstanciaText

                            comisionUbicacionText = comisionUbicacion.text
                            comisionUbicacionText = comisionUbicacionText[comisionUbicacionText.find(":") + 2 : ].strip()
                            comisionDir["ubicacion"] = comisionUbicacionText
                            
                            comisionDir["observacion"] = ""
                            
                            comisionEncontrada = True
                            
                        else:
                            
                            ObservacionComision = filasComisionesInfo.find("td")
                            ObservacionComisionText = ObservacionComision.text
                            ObservacionComisionText = ObservacionComisionText[ObservacionComisionText.find(":") + 2 : ].strip()
                            comisionDir["observacion"] = ObservacionComisionText
                                    
                    if filasComisionesInfo["class"] == ["horarios", "encabezados"]:
                        continue

                    if filasComisionesInfo["class"] == ["subcomision"]:
                       
                        columnasInformacionSubComisiones = list(filasComisionesInfo.children)
             
                        columnaNombreSubComision = columnasInformacionSubComisiones[0]
                        columnaCupoSubComision = columnasInformacionSubComisiones[1]
                        columnaDocentesSubComision = columnasInformacionSubComisiones[2]

                        subComisionDir = {}

                        nombreSubComisionText = columnaNombreSubComision.text
                        nombreSubComisionText = nombreSubComisionText[nombreSubComisionText.rfind(":") + 2 : ].strip()
                        subComisionDir["nombre"] = nombreSubComisionText

                        columnaCupoSubComisionText = columnaCupoSubComision.text
                        columnaCupoSubComisionText = int(columnaCupoSubComisionText[columnaCupoSubComisionText.rfind("/") + 2 : ].strip())
                        subComisionDir["cupo"] = columnaCupoSubComisionText

                        columnaDocentesSubComisionText = columnaDocentesSubComision.text
                        docentesSubComisionText = columnaDocentesSubComisionText[columnaDocentesSubComisionText.find(":") + 2 : ].strip()
                        
                        docentesSubComision = docentesSubComisionText.split(", ")
                        docentesSubComisionDir={}
                        for docente in docentesSubComision:
                            indexInicioCargo = docente.rfind("(")
                            nombre = docente[:indexInicioCargo].strip()
                            cargo = docente[indexInicioCargo + 1:-1].strip()
                            if cargo in docentesSubComisionDir:
                                docentesSubComisionDir[cargo].append(nombre)
                            else:
                                docentesSubComisionDir[cargo] = [nombre]
                            
                        subComisionDir["docentes"] = docentesSubComisionDir

                        subComisionDir["dias"] = {}

                        ultimaSubComision = subComisionDir["nombre"]

                        comisionDir["subcomisiones"][subComisionDir["nombre"]] = subComisionDir

                    if "js-dia" in filasComisionesInfo["class"]:
                        
                        columnasInformacionDias = list(filasComisionesInfo.children)
             
                        columnaTipoClase = columnasInformacionDias[0]
                        columnaDia = columnasInformacionDias[1]
                        columnaHorario = columnasInformacionDias[2]
                        columnaAula = columnasInformacionDias[3]

                        diaDir = {}

                        tipoClaseText = columnaTipoClase.text.strip()
                        diaText = columnaDia.text.strip()
                        horarioText = columnaHorario.text
                        horario = [horarioText[ : horarioText.find("a")].strip(), horarioText[horarioText.find("a") + 1 : ].strip()]
                        AulaText = columnaAula.text.strip()

                        diaDir["dia"] = diaText
                        diaDir["tipo"] = tipoClaseText
                        diaDir["horario"] = horario
                        diaDir["aula"] = AulaText

                        comisionDir["subcomisiones"][ultimaSubComision]["dias"][diaText] = diaDir
                
            actividadDic["comisiones"][comisionDir["nombre"]] = comisionDir
            
        actividadesDic["actividades"][actividadDic["id"]] = actividadDic
        
    periodoDic["actividadesInformacion"] = actividadesDic

    periodosLectivosDic[periodoDic["id"]] = periodoDic
    
    # print()
    # print(periodoDic["id"])
    # print(periodoDic)
    # print()

ejemploDiccionario = open("ejemploDiccionario.json", "w")

json.dump(periodosLectivosDic, ejemploDiccionario)

ejemploDiccionario.close()






