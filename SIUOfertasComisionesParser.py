import re
from bs4 import BeautifulSoup
import json

# Parsea el codigo fuente de Ofertas comisiones y crea el siguiente json por periodos lectivos, indexeado por el id del periodo
# [id] : id del periodo lectivo
# [nombre] : nombre del periodo lectivo
# [nombre] : nombre del periodo lectivo
# [actividades] : Diccionario con la cantidad de actividades del periodo y la informacion de cada una
#    [cantidad] : Cantidad de actividades que forman parte de este periodo lectivo
#    [actividades] : Diccionario con la informacion de cada actividad indexeado por el id de la actividad
#       [id] : id de la actividad
#       [nombre] : nombre de la actividad
#       [comisiones] : Diccionario con la informacion de cada comision de la actividad, indexeado por su nombre
#           [nombre] : nombre de la comision
#           [turno] : turno de la comision
#           [instancia] : tipo de comision
#           [ubicacion] : ubicacion de la comision
#           [observacion] : observacion OPCIONAL de la comision
#           [subcomisiones] : Diccionario con la informacion de cada subcomision, indexeado por su nombre
#               [nombre] : nombre de la subcomision
#               [cupo] : cupo de la subcomision (int)
#               [docentes] : Diccionario de listas de docentes de la subcomision, indexeado por cargo
#               [dias] : Diccionario de cada dia de la subcomision, indexeado por el nombre del dia
#                   [dia] : dia de la materia (Lunes, Martes, ...)
#                   [tipo] : tipo de clase ese dia (Teorico, Laboratorio, ...)
#                   [horario] : horario en donde se da la actividad este dia [desde, hasta]
#                   [aula] : numero de aula donde se da la actividad

# Abrimos el archivo donde esta el Source Code de la pagina
pageFile = open("pagina_info_comisiones.html", "r")
pageSource = pageFile.read()
pageFile.close()
# Regex que encuentra todo texto entre <div class="js-recuadro_periodo recuadro" ...> (incluido) y <div id="js-reporte-vacio" ... </div></div> (no incluido)
# En la pagina, cada periodo esta dentro de su propio <div> con la clase: "js-recuadro_periodo recuadro",
# entre periodo y periodo siempre hay un <div> de reporte vacio, asi que podemos utilizar toda su definicion como finalizador
# usamos la opcion lazy de (.*?) para matchear un solo periodo y no todo dentro del inicio del primero y el finalizador del ultimo periodo

# Tenemos que formatear usando literales \\, ya que toda las informacion estar escrita en un script de una linea que escribe su contenido directamente a la pagina.
regexQueryDivPeriodo = r"(<div class=\\\"js-recuadro_periodo recuadro\\\"(.*?)>)(.*?)(?=(<div id=\\\"js-reporte-vacio\\\")(.*?)<\\/div>)"

# Conseguimos un iterador con cada match en el codigo fuente(cada <div> de periodo )
matches = re.finditer(regexQueryDivPeriodo, pageSource)

# Inicializamos un diccionario donde guardar la informacion de cada Periodo Lectivo indexeado por su id
periodosLectivosDic = {}

# Populamos el diccionario de Periodos Lectivos
for match in matches:

    # Formateamos el div encontrado remplazando los literales por su valor real
    # \\t -> \t | \\n -> \n | \\/ -> /
    # Tenemos el problema de los caracteres de escape como "\\u00ed" -> "\u00ed" -> í
    # Para esto usamos encode().decode('unicode-escape')
    formatedPageSourceCode = (
        match.group().replace("\\/", "/").encode().decode('unicode-escape')
        .replace("\\t", "\t")
        .replace("\\n", "\t")
        .replace('\\"', '"')
    )

    # Parseamos el codigo por BeautifulSoup
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
    # El texto esta formateado como: "Período lectivo: NOMBRE"
    # Manipulamos el string para solo quedarnos con "NOMBRE"
    periodoNombreText = periodoNombreText[periodoNombreText.rfind(":") + 1 :].strip()
    # Guardamos el nombre del periodo
    periodoDic["nombre"] = periodoNombreText

    # Inicializamos el diccionario para guardar la informacion de las actividades que suceden en el periodo lectivo
    # [cantidad] : Cantidad de actividades que forman parte de este periodo lectivo
    # [actividades] : Diccionario con la informacion de cada actividad indexeado por el id de la actividad
    actividadesDic = {}

    # Cada actividad es contenida en un <div> con la clase "js-recuadro_actividad"
    # Encontramos cada uno de estos <div> dentro del periodo, consiguiendo una lista de cada actividad
    actividades = periodo.find_all("div", class_="js-recuadro_actividad")

    # Guardamos la cantidad de actividades e inicializamos el diccionario de actividades
    actividadesDic["cantidad"] = len(actividades)
    actividadesDic["actividades"] = {}

    # Recorremos cada <div> actividad y populamos el diccionario de actividades
    for actividad in actividades:

        # Inicializamos un diccionario para representar cada actividad
        # [id] : id de la actividad
        # [nombre] : nombre de la actividad
        # [comisiones] : Diccionario con la informacion de cada comision de la actividad, indexeado por su nombre
        actividadDic = {}

        # Conseguimos Nombre de la actividad por un atributo personalizado del <div> de actividad
        # el atributo esta formateado como: "NOMBRE (ID)"
        nombreActividad = actividad["actividad"]

        # Manipulamos el string para aislar ID
        idActividad = nombreActividad[nombreActividad.rfind("(") + 1 : -1]

        # Guardamos el id y nombre de la actividad
        actividadDic["id"] = idActividad
        actividadDic["nombre"] = nombreActividad

        # Inicializamos el diccionario que representar cada comision de la actividad
        actividadDic["comisiones"] = {}

        # Cada comision esta contenida en su propia <table> con la clases "table table-bordered table-condensed comision"
        # Encontramos cada tabla de comision y las parseamos
        tablasInformacionComisiones = actividad.find_all(
            "table", class_="table table-bordered table-condensed comision"
        )
        for tablaComision in tablasInformacionComisiones:
            # Inicializamos el diccionario que representara a las comisiones
            # [nombre] : nombre de la comision
            # [turno] : turno de la comision
            # [instancia] : tipo de comision
            # [ubicacion] : ubicacion de la comision
            # [observacion] : observacion OPCIONAL de la comision
            # [subcomisiones] : Diccionario con la informacion de cada subcomision, indexeado por su nombre
            comisionDir = {}

            # Inicializamos el diccionario que representara cada subcomision de la comision
            comisionDir["subcomisiones"] = {}

            # La informacion de las subcomisiones no estan contenidas en si misma como lo estaban el resto de objetos
            # Cada Tabla de informacion esta formateada de la siguiente forma:

            # <tr class="comision">             INFORMACION GENERAL DE LA COMISION      <tr>
            # <tr class="comision">             OBSERVACION OPCIONAL DE LA COMISION     <tr>
            # <tr class="subcomision">          PRIMERA SUBCOMISION                     <tr>
            # <tr class="horarios encabezados"> PRIMER DIA DE LA SUBCOMISION            <tr>
            #                                               ...
            # <tr class="horarios encabezados"> ULTIOM DIA DE LA SUBCOMISION            <tr>
            # <tr class="subcomision">          SEGUNDA SUBCOMISION                     <tr>
            # <tr class="horarios encabezados"> PRIMER DIA DE LA SEGUND SUBCOMISION     <tr>
            #                                               ...

            # Guardamos la ultima subComision encontrada para guardar sus dias luego de encontrarla
            ultimaSubComision = ""

            # Verificamos si estamos leyendo la definicion de una comision o su observacion
            comisionEncontrada = False

            # Pasamos por cada fila y populamos a la comision
            for filasComisionesInfo in tablaComision.find_all("tr"):

                # La fila es la definicion de la comision o una observacion opcional
                if filasComisionesInfo["class"] == ["comision"]:

                    # Si aun no se encontro una comision, entonces debe ser su definicion
                    if not (comisionEncontrada):

                        # Separamos cada columna de inforacion
                        columnasInformacionComision = list(filasComisionesInfo.children)

                        # La primera columna tendra el nombre
                        columnaNombreComision = columnasInformacionComision[0]
                        # La segunda columna tendra el turno
                        columnaTurnoComision = columnasInformacionComision[1]
                        # La tercera columna tendra instancia(regularidad / libre) y ubicacion
                        columnaInfoComision = columnasInformacionComision[2]

                        # Conseguimos el nombre de la comision y lo guardamos
                        nombreComision = columnaNombreComision.find("h5").text
                        nombreComision = nombreComision[
                            nombreComision.find("n:") + 2 :
                        ].strip()
                        comisionDir["nombre"] = nombreComision

                        # Conseguimos el turno de la comision y lo guardamos
                        turnoComision = columnaTurnoComision.find("span").text
                        turnoComision = turnoComision[
                            turnoComision.find(":") + 2 :
                        ].strip()
                        comisionDir["turno"] = turnoComision

                        # Separamos instancias y ubicacion en un vector desde columnaInfoComision
                        comisionInformacionGeneral = columnaInfoComision.find_all(
                            "span"
                        )

                        # Ya que ambos pueden ser opcionales, los inicializamos con "" por defecto
                        comisionDir["instancia"] = ""
                        comisionDir["ubicacion"] = ""

                        # Si solo contienen un <span>, debe ser instancia
                        if len(comisionInformacionGeneral) == 1:
                            # Conseguimos la instancia de la comision y lo guardamos
                            comisionInstanciaText = comisionInformacionGeneral[0].text
                            comisionInstanciaText = comisionInstanciaText[
                                comisionInstanciaText.find(":") + 2 :
                            ].strip()
                            comisionDir["instancia"] = comisionInstanciaText

                        else:
                            # Si hay ubicacion, la conseguimos y la guardamos
                            comisionUbicacionText = comisionInformacionGeneral[1].text
                            comisionUbicacionText = comisionUbicacionText[
                                comisionUbicacionText.find(":") + 2 :
                            ].strip()
                            comisionDir["ubicacion"] = comisionUbicacionText

                        # Seteamos que ya se encontro una comision
                        comisionEncontrada = True

                    # Si ya encontramos una comision, entonces debe ser una observacion opcional
                    else:
                        # Conseguimos la observacion y la guardamos en la comision
                        ObservacionComision = filasComisionesInfo.find("td")
                        ObservacionComisionText = ObservacionComision.text
                        ObservacionComisionText = ObservacionComisionText[
                            ObservacionComisionText.find(":") + 2 :
                        ].strip()
                        comisionDir["observacion"] = ObservacionComisionText

                # Encontramos una definicion de subcomision
                if filasComisionesInfo["class"] == ["subcomision"]:

                    # Separamos las columnas con informacion de la subcomision
                    columnasInformacionSubComisiones = list(
                        filasComisionesInfo.children
                    )

                    # La primera contendra su nombre
                    columnaNombreSubComision = columnasInformacionSubComisiones[0]
                    # La segunda contendra su cupo
                    columnaCupoSubComision = columnasInformacionSubComisiones[1]
                    # La tercera contendra su docentes
                    columnaDocentesSubComision = columnasInformacionSubComisiones[2]

                    # Definimos el diccionario que representara a la subcomision
                    # [nombre] : nombre de la subcomision
                    # [cupo] : cupo de la subcomision (int)
                    # [docentes] : Diccionario de cada docente de la subcomision, indexeado por cargo
                    # [dias] : Diccionario de cada dia de la subcomision, indexeado por el nombre del dia
                    subComisionDir = {}

                    # Conseguimos el nombre de la subcomision y lo guardamos
                    nombreSubComisionText = columnaNombreSubComision.text
                    nombreSubComisionText = nombreSubComisionText[
                        nombreSubComisionText.rfind(":") + 2 :
                    ].strip()
                    subComisionDir["nombre"] = nombreSubComisionText

                    # Conseguimos el cupo de la subcomision y lo guardamos
                    columnaCupoSubComisionText = columnaCupoSubComision.text
                    columnaCupoSubComisionText = int(
                        columnaCupoSubComisionText[
                            columnaCupoSubComisionText.rfind("/") + 2 :
                        ].strip()
                    )
                    subComisionDir["cupo"] = columnaCupoSubComisionText

                    # Conseguimos los docentes de la subcomision
                    # Los docentes aparecen con el formato:
                    # Docente: NOMBRE DOCENTE 1 (CARGO), NOMBRE DOCENTE 2 (CARGO), NOMBRE DOCENTE 3 (CARGO), ...
                    columnaDocentesSubComisionText = columnaDocentesSubComision.text
                    docentesSubComisionText = columnaDocentesSubComisionText[
                        columnaDocentesSubComisionText.find(":") + 2 :
                    ].strip()

                    # Creamos una lista con la informacion de cada docente
                    docentesSubComision = docentesSubComisionText.split(", ")

                    # Inicializamos el diccionario que representara a los docentes de la subcomision
                    # [cargo] : lista de los docentes con este cargo que forman parte de la subcomision
                    docentesSubComisionDir = {}

                    # Recorremos por cada docente y lo agregamos al diccionario
                    for docente in docentesSubComision:

                        # Separamos el string de docente entre su nombre y su cargo
                        indexInicioCargo = docente.rfind("(")
                        nombre = docente[:indexInicioCargo].strip()
                        cargo = docente[indexInicioCargo + 1 : -1].strip()

                        # Si el cargo ya esta dentro del diccionario, agregamos al docente a la lista
                        if cargo in docentesSubComisionDir:
                            docentesSubComisionDir[cargo].append(nombre)
                        else:
                            # En caso contrario, agregamos el nuevo cargo como clave
                            docentesSubComisionDir[cargo] = [nombre]

                    # Guardamos el diccionario de los docentes de la subcomision
                    subComisionDir["docentes"] = docentesSubComisionDir

                    # Con la subcomision definida, el resto de las filas seran sus dias, o una nueva subcomision
                    # Inicializamos el diccionario que representara los dias de la subcomision
                    # [dia] : dia de la materia (Lunes, Martes, ...)
                    # [tipo] : tipo de clase ese dia (Teorico, Laboratorio, ...)
                    # [horario] : horario en donde se da la actividad este dia [desde, hasta]
                    # [aula] : numero de aula donde se da la actividad
                    subComisionDir["dias"] = {}

                    # Cambiamos la ultima subcomision encontrada
                    ultimaSubComision = subComisionDir["nombre"]

                    #Guardamos la subcomision definida en el diccionario de subcomisiones
                    comisionDir["subcomisiones"][subComisionDir["nombre"]] = subComisionDir

                # Encontramos un dia de la ultima subcomision
                if "js-dia" in filasComisionesInfo["class"]:
                    
                    # Separamos cada columna con informacion del dia
                    columnasInformacionDias = list(filasComisionesInfo.children)

                    # La primera contendra el tipo de clase / actividad
                    columnaTipoClase = columnasInformacionDias[0]
                    # La segunda contendra el dia descripto
                    columnaDia = columnasInformacionDias[1]
                    # La tercera contendra el horario de la actividad en este dia
                    columnaHorario = columnasInformacionDias[2]
                    # La cuarta contendra en que aula se hara
                    columnaAula = columnasInformacionDias[3]

                    # Definimos el diccionario que representara el dia de la subcomision
                    diaDir = {}

                    #conseguimos el tipo de clase
                    tipoClaseText = columnaTipoClase.text.strip()

                    #Si la subcomision no tiene dias definidos, salteamos este paso
                    if tipoClaseText == "Sin definir":
                        continue
                    
                    #conseguimos el dia y el horario
                    diaText = columnaDia.text.strip()
                    horarioText = columnaHorario.text
                    
                    #El horio tiene el formato "DESDE a HASTA"
                    # manipulamos el string original para tener un vector [DESDE, HASTA]
                    horario = [
                        horarioText[: horarioText.find("a")].strip(),
                        horarioText[horarioText.find("a") + 1 :].strip(),
                    ]
                    #Conseguimos el aula del dia
                    AulaText = columnaAula.text.strip()

                    #Guardamos las propiedades del dia
                    diaDir["dia"] = diaText
                    diaDir["tipo"] = tipoClaseText
                    diaDir["horario"] = horario
                    diaDir["aula"] = AulaText

                    #Agregamos el dia al diccionario de dias de la ultima subcomision encontrada
                    comisionDir["subcomisiones"][ultimaSubComision]["dias"][diaText] = diaDir
            
            #Agregamos la comision al diccionario de comisiones de actividades
            actividadDic["comisiones"][comisionDir["nombre"]] = comisionDir
        
        #Agregamos la actividad al diccionario de actividades de periodo
        actividadesDic["actividades"][actividadDic["id"]] = actividadDic
    
    # Guardamos el diccionario de informacion de actividades del periodo
    periodoDic["actividadesInformacion"] = actividadesDic

    # Agregamos el periodo al diccionario de periodos 
    periodosLectivosDic[periodoDic["id"]] = periodoDic

# Guardamos el diccionario de periodos en un archivo como un json
ejemploDiccionario = open("ejemploDiccionario.json", "w")
json.dump(periodosLectivosDic, ejemploDiccionario)
ejemploDiccionario.close()
