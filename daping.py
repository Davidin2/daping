# Programado por David Hernandez david.hernandezc@gmail.com
# https://github.com/Davidin2/dapings


import subprocess
import pickle
import ipaddress
from random import randrange
from datetime import datetime
from datetime import date
import smtplib
import configparser

TESTEOS=0               #posicion en a lista en dic_rangos_contador
EXITOSOS=1              #posicion en a lista en dic_rangos_contador
EXITOSOS_SEGUIDOS=2     #posicion en a lista en dic_rangos_contador
FALLIDOS=3              #posicion en a lista en dic_rangos_contador
FALLIDOS_SEGUIDOS=4     #posicion en a lista en dic_rangos_contador
LOG_CADA=1              #Cada cuando escupimos log al fichero log.txt
BUSCA_IP_CADA=1         #Si un rango no tiene ips cada cuanto buscamos
GUARDA_DIC_CADA=1       #Cada cuando salvamos el diccionario de rangos ppal
MAIL_SI_FALLO=1         #Correo si falla un rango x veces seguidas
MAIL_SI_RECUPERA=1      #Correo cuando recupera un rango x veces seguidas
BUSCAIPS_SI_MENOS=10    #Busca IPs de nuevo si tiene menos de x
MAXIMAS_IP_POR_RANGO=50 #Cuantas IPs guarda de cada rango como máximo
MAXIMA_RED=21           #Si es más grande de X partimos la red en trozos como X
TRUNC_IPS=50            #Recorta las IPs a  (solo aplica si hay más de x al incio al cargar el diccionario). Nunca inferior a 6
ID=""
MAILS=["tu@email1","tu@email2"] #Direcciones de envío de mail

def envia_correo(asunto, mensaje):
    remitente = "david.hernandezc@gmail.com"
    destinatario = MAILS
    asunto="DAPING: " + ID + " "+ asunto
    print(asunto)
    email = """From: %s
To: %s
MIME-Version: 1.0
Content-type: text/html
Subject: %s
    
%s
""" % (remitente, destinatario, asunto, mensaje)
    try:
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(remitente, MAILS, email)
        print ("Correo enviado satisafactoriamente")
    except:
        print ("Error: el correo no ha sido enviado.")


def carga_rangos(fichero):
    try:
        with open(fichero, "r") as f:
            lista_rangos=[]
            print ("---------------Cargamos rangos de",fichero,"---------------")
            for linea in f:
                try:
                    ip = ipaddress.IPv4Network(linea[:-1]) # para quitar el retorno de carro
                    print(ip, "es una red correcta")
                    lista_rangos.append(linea[:-1]) 
                except ValueError:
                    print(linea, "es una red incorrecta y no se cargara")
            print ("---------------Rangos cargados---------------")
            print(lista_rangos)
            return lista_rangos
    except (OSError, IOError) as e:
        print ("---------------No hay rangos a cargar---------------")
        return list()   

def guarda_diccionario(dic,nombre_fichero):
    with open(nombre_fichero, "wb") as f:
        pickle.dump(dic, f)
    print("---------------Diccionario guardado---------------")
    #print (dic)

def carga_diccionario(nombre_fichero):
    global TRUNC_IPS
    try:
        with open(nombre_fichero, "rb") as f:
            dic_cargado=pickle.load(f)
            print ("---------------Diccionario cargado---------------")
            for rango in dic_cargado.keys(): #truncamos ips
                if TRUNC_IPS<6:
                    TRUNC_IPS=6 # como minimo debería ser 5 para no cargarnos el diccionario de contadores
                if len(dic_cargado[rango])>TRUNC_IPS:
                    dic_cargado[rango]=dic_cargado[rango][0:TRUNC_IPS]
            print(dic_cargado)
            return dic_cargado
    except (OSError, IOError) as e:
        print ("---------------No hay Diccionario a cargar---------------")
        return dict()

def busca_ips_en_rango(rango):

    print ("---------------Buscando IPs en rango", rango)
    network=ipaddress.ip_network(rango)
    mascara=network.prefixlen
    if mascara > MAXIMA_RED-1:
        result = subprocess.run(["fping", "-gaq", str(rango)], capture_output=True, text=True)
    else:  #Si el rango es <max_red seleccionamos uno de los max_red dentro de el
        lista_subredes=list(network.subnets(new_prefix=MAXIMA_RED)) #Spliteamos en max_red
        seleccionada=randrange(len(lista_subredes)) #Selecciona entre 0 y len-1
        print ("---------------Selecciono para ping la", seleccionada, "de",len(lista_subredes), str(lista_subredes[seleccionada]))
        result = subprocess.run(["fping", "-gaq", str(lista_subredes[seleccionada])], capture_output=True, text=True)
    lista_salida=result.stdout.splitlines() #result.stdout.splitlines es una lista de lineas con la salida del fping. Intentar limitar a 50 pings maximo, no tiene sentido tener mas.
    print("---------------Rango", rango, "procesado, ", len(lista_salida), "ips responden a ping")
    if len(lista_salida) > MAXIMAS_IP_POR_RANGO:
        lista_salida=lista_salida[0:MAXIMAS_IP_POR_RANGO]
    return (lista_salida)

def carga_config():
    global LOG_CADA
    global BUSCA_IP_CADA
    global GUARDA_DIC_CADA
    global MAIL_SI_FALLO
    global MAIL_SI_RECUPERA
    global BUSCAIPS_SI_MENOS
    global MAXIMAS_IP_POR_RANGO
    global MAXIMA_RED
    global TRUNC_IPS
    global ID
    global MAILS
   
    config = configparser.ConfigParser()
    try:
        with open ('daping.ini') as f:  #Falta gestionar si un id no existe en el fichero
            config.read_file(f)
            LOG_CADA=int(config['default']['LOG_CADA'])
            BUSCA_IP_CADA=int(config['default']['BUSCA_IP_CADA'])
            GUARDA_DIC_CADA=int(config['default']['GUARDA_DIC_CADA'])
            MAIL_SI_FALLO=int(config['default']['MAIL_SI_FALLO'])
            MAIL_SI_RECUPERA=int(config['default']['MAIL_SI_RECUPERA'])
            BUSCAIPS_SI_MENOS=int(config['default']['BUSCAIPS_SI_MENOS'])
            MAXIMAS_IP_POR_RANGO=int(config['default']['MAXIMAS_IP_POR_RANGO'])
            MAXIMA_RED=int(config['default']['MAXIMA_RED'])
            TRUNC_IPS=int(config['default']['TRUNC_IPS'])
            ID=config['default']['ID']
            MAILS=config['default']['MAILS']
            print("Configuración cargada")
            print (MAILS)
    except (OSError, IOError) as e:
        print ("No hay fichero configuración")

def print_config():
    config="\r\nConfiguración actual:\r\n"
    config=config + "LOG_CADA: " + str(LOG_CADA) + "\r\n"
    config=config + "BUSCA_IP_CADA: " + str(BUSCA_IP_CADA) + "\r\n"
    config=config + "GUARDA_DIC_CADA: " + str(GUARDA_DIC_CADA) + "\r\n"
    config=config + "MAIL_SI_FALLO: " + str(MAIL_SI_FALLO) + "\r\n"
    config=config + "MAIL_SI_RECUPERA: " + str(MAIL_SI_RECUPERA) + "\r\n"
    config=config + "BUSCAIPS_SI_MENOS: " + str(BUSCAIPS_SI_MENOS) + "\r\n"
    config=config + "MAXIMAS_IP_POR_RANGO: " + str(MAXIMAS_IP_POR_RANGO) + "\r\n"
    config=config + "MAXIMA_RED: " + str(MAXIMA_RED) + "\r\n"
    config=config + "TRUNC_IPS: " + str(TRUNC_IPS) + "\r\n"
    config=config + "ID: " + ID + "\r\n"
    config=config + "MAILS: " + MAILS + "\r\n"
    return (config)

def main():
    carga_config()
    fecha_inicio = date.today()
    dic_rangos_contador={}
    dic_rangos={} #Diccionario con rango (key) y lista de ips que responden (value)
    dic_rangos=carga_diccionario("dic_rangos.dat")
    dic_rangos_contador=carga_diccionario("dic_rangos_cont.dat")
    if dic_rangos_contador =={}: # si no hay fichero de contador lo inicializamos
        for rango in dic_rangos.keys():
            dic_rangos_contador[rango]=[0,0,0,0,0]  # testeos, exitosos, fallidos, ver constantes

    rangos=carga_rangos("nuevos_rangos.txt")
        #Buscar IPs en Rangos y rellenamos diccionario:
    for rango in rangos:      #En cada rango de la lista
        if rango not in dic_rangos: # Añadimos rango si no existe
            dic_rangos[rango]=busca_ips_en_rango(rango)  #Añadimos al diccionario las ips que responden       
            dic_rangos_contador[rango]=[0,0,0,0,0]
            print(rango, "cargado ")
        else:
            print(rango, "no cargado porque ya estaba")
        #Borramos rangos desde fichero
    rangos_a_borrar=carga_rangos("borrar_rangos.txt")
    for rango in rangos_a_borrar:      #En cada rango de la lista
        if rango in dic_rangos:
            #lo borramos
            del (dic_rangos[rango])
            del (dic_rangos_contador[rango])
            print(rango, "borrado ")
        else:
            print(rango, "No se puede borrar pq no está")
    #Pendiente imprimir al log el dic y count  
    print ("---------------Entramos en modo control---------------------")
    #print(dic_rangos)
    # Ver si las IPs de un diccionario de rangos siguen respondiendo. Si una IP no responde la elimina de la lista
    testeo=0
    
    while True:
        testeo+=1
        num_ips=0
        num_rangos=0
        num_ips_ping=0
        for rango in dic_rangos.keys():
            network=ipaddress.ip_network(rango)
            num_ips+=network.num_addresses  
            num_rangos+=1
            num_ips_ping+=len(dic_rangos[rango])
        logfile=open("ultimo.log", "w") 
        print ("------------------INICIO",datetime.now(),"------------------------", file=logfile)
        print ("Controlando", num_rangos, "rangos y",num_ips,"ips. Hacemos ping a",num_ips_ping,"ips.", file=logfile)
        fecha_actual=date.today() #Para mandar un correo una vez solo cuando cambiamos de día
        print("------------------------","Testeo numero", testeo, "-----------------------")
        print ("Controlando", num_rangos, "rangos y",num_ips,"ips. Hacemos ping a",num_ips_ping,"ips.")
        for rango in dic_rangos.keys():     # Por cada rango en el diccionario
            if len(dic_rangos[rango])>0:    # Si tiene al menos una ip que responde
                if len(dic_rangos[rango])<BUSCAIPS_SI_MENOS: # si tiene menos del limite 
                    if testeo % BUSCA_IP_CADA == 0: #Y además toca buscar
                        print ("Como solo tiene",len(dic_rangos[rango]),"ip, buscamos mas)")
                        dic_rangos[rango]+=busca_ips_en_rango(rango)
                        #podríamos quitar ips duplicadas, aunque puede ser interesante no hacerlo para que si no encuentra más no se quede siempre buscando
                comando= ["fping", "-aq"]
                comando+=dic_rangos[rango]      # Generamos el comando fping a cada ip
                result = subprocess.run(comando, capture_output=True, text=True)
                posicion=0  # Itero la lista de ips que responden del rango
                while posicion<len(dic_rangos[rango]):
                    if result.stdout.find(dic_rangos[rango][posicion]+"\n")>-1: # devuelve -1 si no la encuentra. Añadimos \n para no confundir las ip 1.1.1.1 con 1.1.1.11
                        #print("La IP",dic_rangos[rango][posicion] , "ha respondido")
                        posicion+=1
                    else:
                        #print("La IP", dic_rangos[rango][posicion] , "No ha respondido y la eliminamos de la lista")
                        dic_rangos[rango].pop(posicion) # Borro la ip que no responde. No incremento la posicion pq al borrarla ese numero es la siguiente posicion
                if  len(dic_rangos[rango])>0:
                    dic_rangos_contador[rango][EXITOSOS]+=1
                    dic_rangos_contador[rango][EXITOSOS_SEGUIDOS]+=1
                    dic_rangos_contador[rango][FALLIDOS_SEGUIDOS]=0
                else:
                    dic_rangos_contador[rango][FALLIDOS]+=1
                    dic_rangos_contador[rango][FALLIDOS_SEGUIDOS]+=1
                    dic_rangos_contador[rango][EXITOSOS_SEGUIDOS]=0
                dic_rangos_contador[rango][TESTEOS]+=1
                print(rango, len(dic_rangos[rango]),"IPs responden al ping", "T E ES F FS", dic_rangos_contador[rango])
                print(rango, len(dic_rangos[rango]),"IPs responden al ping", "T E ES F FS", dic_rangos_contador[rango], file=logfile)
            else:
                dic_rangos_contador[rango][FALLIDOS]+=1
                dic_rangos_contador[rango][FALLIDOS_SEGUIDOS]+=1
                dic_rangos_contador[rango][EXITOSOS_SEGUIDOS]=0
                dic_rangos_contador[rango][TESTEOS]+=1
                print ("**********ALERTA", rango, "SIN IP", "T E ES F FS", dic_rangos_contador[rango])
                print ("**********ALERTA", rango, "SIN IP", "T E ES F FS", dic_rangos_contador[rango], file=logfile)
                if testeo % BUSCA_IP_CADA == 0: #Testeamos rangos con 0
                    dic_rangos[rango]=busca_ips_en_rango(rango)
            if dic_rangos_contador[rango][FALLIDOS_SEGUIDOS] == MAIL_SI_FALLO:
                texto="FALLO en rango " + rango + " T E ES F FS " + str(dic_rangos_contador[rango])
                print (texto)
                envia_correo(texto, texto)
            if dic_rangos_contador[rango][EXITOSOS_SEGUIDOS] == MAIL_SI_RECUPERA: 
                if dic_rangos_contador[rango][EXITOSOS_SEGUIDOS] != dic_rangos_contador[rango][TESTEOS]: # controlamos que no sea al arranque
                    texto="Recuperacion en rango " + rango + " T E ES F FS " + str(dic_rangos_contador[rango])
                    print (texto)
                    envia_correo(texto, texto)
        print ("------------------FIN",datetime.now(),"------------------------", file=logfile)
        logfile.close()
        logfile2=open("ultimo.log", "r")
        logfile3=open("ultimo.txt", "w") # lo copiamos a .txt pq el .log al estar abierto siempre no tiene toda la info
        for linea in logfile2:
            print (linea[:-1], file=logfile3)
        logfile2.close()
        print (print_config(), file=logfile3)
        logfile3.close()
        if fecha_inicio.day != fecha_actual.day:
            mailfile=open("ultimo.txt", "r")
            texto=""
            for linea_log in mailfile:
                texto=texto+linea_log+ "<br>"
            envia_correo("Reporte diario PINGs", texto)
            fecha_inicio=date.today()
            mailfile.close()
        if testeo % LOG_CADA ==0:
            logfile4=open("daping.log","a+")
            logfile5=open("ultimo.log", "r")
            for linea_log in logfile5:
                print (linea_log[:-1], file=logfile4)
            logfile4.close()
            logfile5.close()
        if testeo % GUARDA_DIC_CADA == 0: #Guardamos diccionario
            guarda_diccionario(dic_rangos,"dic_rangos.dat")
            guarda_diccionario(dic_rangos_contador,"dic_rangos_cont.dat")
        
if __name__ == '__main__':
    main()

#Mejoras a futuro: 
    #1 proceso hace pings buscando ips mientras otro testea las existentes en paralelo



