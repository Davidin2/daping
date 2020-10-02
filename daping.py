# Programado por David Hernandez david.hernandezc@gmail.com
# https://github.com/Davidin2/dapings


import subprocess
import pickle
import ipaddress
from random import randrange
from datetime import datetime
from datetime import date
import smtplib

def envia_correo(asunto, mensaje):
    remitente = "david.hernandezc@gmail.com"
    destinatario = "david.hernandez@vodafone.com"
    asunto="DAPING: " + asunto
    email = """From: %s
To: %s
MIME-Version: 1.0
Content-type: text/html
Subject: %s
    
%s
""" % (remitente, destinatario, asunto, mensaje)
    try:
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(remitente, destinatario, email)
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
    try:
        with open(nombre_fichero, "rb") as f:
            dic_cargado=pickle.load(f)
            print ("---------------Diccionario cargado---------------")
            print(dic_cargado)
            return dic_cargado
    except (OSError, IOError) as e:
        print ("---------------No hay Diccionario a cargar---------------")
        return dict()

def busca_ips_en_rango(rango):
    MAXIMAS_IP_POR_RANGO=50 # Cuantas IPs guarda de cada rango como máximo
    MAXIMA_RED=21   # Si es más grande de X partimos la red en trozos como X
    print ("---------------Buscando IPs en rango", rango)
    network=ipaddress.ip_network(rango)
    mascara=network.prefixlen
    if mascara > MAXIMA_RED-1:
        result = subprocess.run(["fping", "-gaq", str(rango)], capture_output=True, text=True)
    else:  #Si el rango es <MAXIMA_RED seleccionamos uno de los MAXIMA_RED dentro de el
        lista_subredes=list(network.subnets(new_prefix=MAXIMA_RED)) #Spliteamos en MAXIMA_RED
        seleccionada=randrange(len(lista_subredes)) #Selecciona entre 0 y len-1
        print ("---------------Selecciono para ping la", seleccionada, "de",len(lista_subredes), str(lista_subredes[seleccionada]))
        result = subprocess.run(["fping", "-gaq", str(lista_subredes[seleccionada])], capture_output=True, text=True)
    lista_salida=result.stdout.splitlines() #result.stdout.splitlines es una lista de lineas con la salida del fping. Intentar limitar a 50 pings maximo, no tiene sentido tener mas.
    print("---------------Rango", rango, "procesado, ", len(lista_salida), "ips responden a ping")
    #aqui podíamos truncar lista si no queremos tantas ips
    if len(lista_salida) > MAXIMAS_IP_POR_RANGO:
        lista_salida=lista_salida[0:MAXIMAS_IP_POR_RANGO]
    return (lista_salida)


def main():
    print ("Empezamos")
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

    #dic_rangos["80.224.0.0/24"].append("80.224.0.1") #Añado una ip que no responde para que falle y probarla
    #dic_rangos["80.224.0.0/24"].append("80.224.0.5") #Añado una ip que no responde para que falle y probarla
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

    

    testeo=0
    
    while True:
        testeo+=1
        num_ips=0
        num_rangos=0
        num_ips_ping=0
        for rango in dic_rangos.keys():
            #si queremos recortar las ips de ping
            #dic_rangos[rango]=dic_rangos[rango][0:XX] no testeado∫
            network=ipaddress.ip_network(rango)
            num_ips+=network.num_addresses  
            num_rangos+=1
            num_ips_ping+=len(dic_rangos[rango])
        if testeo % LOG_CADA == 0:
            logfile2=open("ultimo.log", "w")
            print ("------------------INICIO",datetime.now(),"------------------------", file=logfile2)
            print ("Controlando", num_rangos, "rangos y",num_ips,"ips. Hacemos ping a",num_ips_ping,"ips.", file=logfile2)
            logfile=open("log.txt", "a+") 
            print ("------------------INICIO",datetime.now(),"------------------------", file=logfile)
            print ("Controlando", num_rangos, "rangos y",num_ips,"ips. Hacemos ping a",num_ips_ping,"ips.", file=logfile)
            fecha_actual=date.today() #Para mandar un correo una vez solo cuando cambiamos de día
            if fecha_inicio.day != fecha_actual.day:
                mailfile=open("mail.txt", "w") #pendente poner el dia mes y año al nombre fichero
                print ("------------------INICIO",datetime.now(),"------------------------", file=mailfile)
                print ("Controlando", num_rangos, "rangos y",num_ips,"ips. Hacemos ping a",num_ips_ping,"ips.", file=mailfile)
             
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
                if testeo % LOG_CADA == 0: #guardamos log de como vamos
                    print(rango, len(dic_rangos[rango]),"IPs responden al ping", "T E ES F FS", dic_rangos_contador[rango], file=logfile)
                    print(rango, len(dic_rangos[rango]),"IPs responden al ping", "T E ES F FS", dic_rangos_contador[rango], file=logfile2)      
                    if fecha_inicio.day != fecha_actual.day:
                        print(rango, len(dic_rangos[rango]),"IPs responden al ping", "T E ES F FS", dic_rangos_contador[rango], file=mailfile)           
            else:
                dic_rangos_contador[rango][FALLIDOS]+=1
                dic_rangos_contador[rango][FALLIDOS_SEGUIDOS]+=1
                dic_rangos_contador[rango][EXITOSOS_SEGUIDOS]=0
                dic_rangos_contador[rango][TESTEOS]+=1
                print ("**********ALERTA", rango, "SIN IP", "T E ES F FS", dic_rangos_contador[rango])
                if testeo % LOG_CADA == 0: #guardamos log de como vamos
                    print ("**********ALERTA", rango, "SIN IP", "T E ES F FS", dic_rangos_contador[rango], file=logfile)
                    print ("**********ALERTA", rango, "SIN IP", "T E ES F FS", dic_rangos_contador[rango], file=logfile2)
                    if fecha_inicio.day != fecha_actual.day:
                        print ("**********ALERTA", rango, "SIN IP", "T E ES F FS", dic_rangos_contador[rango], file=mailfile)
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
        if testeo % LOG_CADA == 0:
            print ("------------------FIN",datetime.now(),"------------------------", file=logfile)
            print ("------------------FIN",datetime.now(),"------------------------", file=logfile2)
            logfile.close()
            logfile2.close()
            logfile2=open("ultimo.log", "r")
            logfile3=open("ultimo.txt", "w")
            for linea in logfile2:
                print (linea[:-1], file=logfile3)
            logfile2.close()
            logfile3.close()
            if fecha_inicio.day != fecha_actual.day:
                print ("------------------FIN",datetime.now(),"------------------------", file=mailfile)
                mailfile.close()
                mailfile=open("mail.txt", "r")
                texto=""
                for linea_log in mailfile:
                    texto=texto+linea_log+ "<br>"
                mailfile.close()
                envia_correo("Reporte diario PINGs", texto)
                fecha_inicio=date.today()

        
        if testeo % GUARDA_DIC_CADA == 0: #Guardamos diccionario
            guarda_diccionario(dic_rangos,"dic_rangos.dat")
            guarda_diccionario(dic_rangos_contador,"dic_rangos_cont.dat")
        
if __name__ == '__main__':
    main()

#Mejoras a futuro: 
    #1 proceso hace pings buscando ips mientras otro testea las existentes en paralelo



