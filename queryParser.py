import re
from bs4 import BeautifulSoup

# Abrimos el archivo donde esta el Source Code de la pagina
pageFile = open("page.html", "r")
pageSource = pageFile.read()

# Regex que encuentra todo texto entre <div class="js-recuadro_periodo recuadro" ...> (incluido) y <div id="js-reporte-vacio" ... </div></div> (no incluido)
# En la pagina, cada periodo esta dentro de su propio <div> con la clase: "js-recuadro_periodo recuadro", 
# entre periodo y periodo siempre hay un <div> de reporte vacio, asi que podemos utilizar toda su definicion como finalizador
# usamos la opcion lazy de (.*?) para matchear un solo periodo y no todo dentro del inicio del primero y el finalizador del ultimo periodo

#Tenemos que formatear usando literales \\, ya que toda las informacion estar escrita en un script de una linea que escribe su contenido directamente a la pagina.
regexQueryDivPeriodo = r"(<div class=\\\"js-recuadro_periodo recuadro\\\"(.*?)>)(.*?)(?=(<div id=\\\"js-reporte-vacio\\\")(.*?)<\\/div>)"

#Conseguimos
matches = re.finditer(regexQueryDivPeriodo, pageSource)

periodosLectivosDic = {}

for match in matches:
    
    formatedPageSourceCode = match.group().replace("\\t","\t").replace("\\n","\t").replace("\\\"","\"").replace("\\/","/")
    soup = BeautifulSoup(formatedPageSourceCode, "html.parser")
        
    periodoDic = {}
    periodo = soup.find("div", class_="js-recuadro_periodo recuadro")
        
    periodoDic["id"] = periodo["periodo"]
        
    periodoNombre = periodo.find("h3")
    periodoNombreText = periodoNombre.text
    periodoNombreText = periodoNombreText[periodoNombreText.rfind(":") + 1 : ].strip()
    periodoDic["nombre"] = periodoNombreText
        
    actividadesDic = {}
    actividades = periodo.find_all("div",class_="js-recuadro_actividad")
        
    actividadesDic["cantidad"] = len(actividades)
    actividadesDic["actividades"] = {}
        
    for actividad in actividades:
            
        actividadDic = {}
            
        nombreActividad = actividad["actividad"]
        idActividad = nombreActividad[nombreActividad.rfind("(") + 1 : -1]
            
        actividadDic["id"] = idActividad 
        actividadDic["nombre"] = nombreActividad
        actividadDic["comisiones"] = {}

        tablasInformacionComisiones = actividad.find_all("table", class_="table table-bordered table-condensed comision")
        for tablaComision in tablasInformacionComisiones:
            
            filasComisiones = tablaComision.find_all("tr", class_="comision")
                
            filaInformacionComision = filasComisiones[0] 
                
            columnasInformacionComision = list(filaInformacionComision.children)
             
            columnaNombreComision = columnasInformacionComision[0]
            columnaTurnoComision = columnasInformacionComision[1]
            columnaInfoComision = columnasInformacionComision[2]

            comisionDir = {}

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

            if(len(filasComisiones) > 1):
                filaObservacionComision = filasComisiones[1]
                ObservacionComision = filaObservacionComision.find("td")
                ObservacionComisionText = ObservacionComision.text
                ObservacionComisionText = ObservacionComisionText[ObservacionComisionText.find(":") + 2 : ].strip()
                comisionDir["observacion"] = ObservacionComisionText
            else:
                comisionDir["observacion"] = ""

            comisionDir["subcomisiones"] = {}
            ultimaSubComision = ""
            for filasSubComisionesInfo in tablaComision.find_all("tr"):
                    
                    if filasSubComisionesInfo["class"] == ["comision"]:
                        continue

                    if filasSubComisionesInfo["class"] == ["horarios", "encabezados"]:
                        continue

                    if filasSubComisionesInfo["class"] == ["subcomision"]:
                       
                        columnasInformacionSubComisiones = list(filasSubComisionesInfo.children)
             
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

                    if "js-dia" in filasSubComisionesInfo["class"]:
                        
                        columnasInformacionDias = list(filasSubComisionesInfo.children)
             
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
        
    periodoDic["actividades"] = actividadesDic

    periodosLectivosDic[periodoDic["id"]] = periodoDic
    
    print()
    print(periodoDic["id"])
    print(periodoDic)
    print()
    







