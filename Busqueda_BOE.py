#importacion
import sys
from datetime import date,timedelta #Operaciones con fechas
import numpy as np
import pandas as pd
import urllib #Acceso a paginas Url
from xml.etree import ElementTree as ET #para busqueda en arboles tipo a XML
import re #para busqueda patrones regulares

#Funcion para carga fichero y retorno datos en arbol
def carga(url): #Apertura y lectura fichero
    fichero=urllib.request.urlopen(url)
    data=fichero.read()
    fichero.close()
    #Transformacion datos en un arbol de elementos para busqueda de patron    
    arb=ET.fromstring(data)
    return arb

#Funcion comprobacion string
def cad(ch):
    if isinstance(ch,str)==True:
        return ch
    else: return None
    

# Funcion recursiva de busqueda de padre
def padre(n,hijo):
    while (n>0):
        n=n-1
        try:      ## Gestion de excepciones por si faltan epigrafes. Secciones 4 y 5 . Ver documentacion BOE XML
            hijo=parent_map[hijo]
        except KeyError:
            return hijo
        return padre(n,hijo)
    return hijo

#Funcion extraccion  y carga datos
def extrac(pa):
    ca=np.empty((1,11),dtype=object) #El array donde se guarda los datos
    ca[0,0]=cad(pa[6][0].findtext('fecha')) #Meta / Fecha publicacion (elemento)
    ca[0,6]=cad( ''.join(pa[1].attrib.values())) # Item id (atributo)
    ca[0,7]=cad( titulo.text) # Item / Titulo (elemento)
    ca[0,8]=cad( pa[1].findtext('urlPdf')) # Item / UrlPdf (elemento)
    ca[0,9]=cad( pa[1].findtext('urlHtm')) # Item / UrlHtm (elemento)
    ca[0,10]=cad( pa[1].findtext('urlXml')) # Item / UrlXml (elemento)
    if pa[5]==pa[6]:
        ca[0,1]=cad( ''.join(pa[4][0].attrib.values()))  # Diario / Sumario_nbo (elemento)
        ca[0,2]=cad( pa[4][0].findtext('urlPdf')) # Sumario_nbo / urlPdf  (elemento)
        ca[0,3]=cad( ''.join(pa[3].attrib.values())) # Seccion / nombre ( atributo)
        ca[0,4]=cad( ''.join(pa[2].attrib.values())) # Departamento / nombre ( atributo)
        ca[0,5]=  None # Epigrafe / nombre ( atributo  .. si lo tuviera)
    else :
        ca[0,1]=cad( ''.join(pa[5][0].attrib.values()))  # Diario / Sumario_nbo (elemento)
        ca[0,2]=cad( pa[5][0].findtext('urlPdf')) # Sumario_nbo / urlPdf  (elemento)
        ca[0,3]=cad( ''.join(pa[4].attrib.values())) # Seccion / nombre ( atributo)
        ca[0,4]=cad( ''.join(pa[3].attrib.values())) # Departamento / nombre ( atributo)
        ca[0,5]=cad( ''.join(pa[2].attrib.values())) # Epigrafe / nombre ( atributo  .. si lo tuviera)
    cdf=pd.DataFrame(data=ca,columns=('fecha','sumario','sumarioPdf','seccion','departamento','epigrafe','item','titulo','tituloPdf','tituloHtm','tituloXml'))
    return cdf
        
#Obtencion argumentos
termino=str(sys.argv[1]  )
    
#Otener la fecha actual y la primera. Queda pendiente la manera de hacerlo interactivo
formato="%Y%m%d"
origen=date(1950,9,1)
destino=date.today()

#Rango de dias
dif=destino-origen #numero de dias
difer=dif.days

url=np.empty(difer,dtype=object) #el array donde almacenar las urls
#Concatenamos y ponemos en el array
for fila in range(0,url.size):
    dia=origen+timedelta(days=fila)
    diaUrl=dia.strftime(formato)
    url[fila]="http://boe.es/diario_boe/xml.php?id=BOE-S-"+diaUrl


#Preparacion dataframe
dat=pd.DataFrame(columns=('fecha','sumario','sumarioPdf','seccion','departamento','epigrafe','item','titulo','tituloPdf','tituloHtm','tituloXml'))
dat=dat.fillna(0)
#Lectura del archivo XML desde la URl       
for i in range(0,difer):
    arb=carga(url[i])
#Busqueda de patron en titulo (solo de aquellos que sean 'string')   
    for titulo in arb.findall('.//titulo'):
        if isinstance(titulo.text,str)==False : continue   #No existe titulo como string. Continuar
        EsRe=re.search(termino,titulo.text) #Este es el patron
        if EsRe!=None :
            parent_map = dict((c, p) for p in arb.getiterator() for c in p)  #diccionario donde se almacenan los padres de cada nodo
            pa=np.empty(7,dtype=object)   #array para guardar padres
            pa[0]=titulo
            for i in range(1,7):   #llamada a funcion recursiva para encontrar todos los padres. El rango indica la profundidad del arbol. Hasta 6 hijos
                pa[i]=padre(i,titulo)
            dat=dat.append(extrac(pa))
            

            
txtSalida='BOE'+termino+'.txt'
dat.to_csv(txtSalida,encoding='utf-8')