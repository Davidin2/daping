Daping es una herramienta para controlar que tenemos ping a ciertos rangos de Internet.

Para funcionar necesita un fichero nuevos_rangos.txt donde indicamos los rangos que queremos tener controlados

Al inciar el programa cargará los rangos del fichero (en formato x.x.x.x/y) y los añade a la motorización

Automaticamente guardará los rangos durante cada ejecución, usando el fichero nuevos_rangos.txt solo para cargar los nuevos.

Si al iniciar una ejecución queremos borrar algún rango los pondremos en el fichero borrar_rangos.txt.

De una ejecución a la siguiente guarda los ficheros dic_rangos.dat y dic_rangos_cont.dat donde almacena los rangos que tiene que buscar, las ips que responden en ese momento y los contadores de exito y fracaso de ping del rango.

Las siguientes variables permiten modificar el comportamiento del programa:

MAXIMAS_IP_POR_RANGO=50 # Cuantas IPs guarda de cada rango como máximo
MAXIMA_RED=21   # Si la red es más grande de /21 partimos la red en trozos /21
LOG_CADA=1              #Cada cuando escupimos log al fichero log.txt
BUSCA_IP_CADA=1         #Si un rango no tiene ips cada cuanto buscamos
GUARDA_DIC_CADA=1       #Cada cuando salvamos el diccionario de rangos a disco
MAIL_SI_FALLO=1         #Correo si falla un rango x veces seguidas
MAIL_SI_RECUPERA=1      #Correo cuando recupera un rango x veces seguidas
BUSCAIPS_SI_MENOS=10    #Busca IPs de nuevo en el rango si tiene menos de x

Fase inicial:
Cuando se inicia el programa carga los rangos que tenía de la última ejecuación, después añade los nuevos rangos del fichero y busca ips que respondan al ping. Despues procede al borrado de rangos según se indica en el fichero.

Fase principal:
En esta fase va recorriendo los rangos uno a uno probando las ips que tiene que responden al ping. Si un rango tiene menos de "BUSCAIPS_SI_MENOS" busca de nuevo IPs. Si encuentra más de "MAXIMAS_IP_POR_RANGO" limita las ips a dicho número. Si un rango no tiene ips que respondan al ping durante "MAIL_SI_FALLO" pasadas, manda un mail indicando que el rango no responde. Cuando el rango responda durante "MAIL_SI_RECUPERA" pasadas, manda un mail indicando que se ha recuperado.

Una vez al día (a las 00:00) mánda por mail un reporte de estado.

Guarda también un estado de log cada "LOG_CADA" pasadas.

Guarda las IPs en disco cada "GUARDA_DIC_CADA" pasadas.

Ejemplo de output por rango:
8.8.8.8/32 2 IPs responden al ping T E ES F FS [1, 1, 1, 0, 0]
T-->Número de testeos de ese rango
E-->Número de testeos de ese rango y que ha respondido
ES-->Número de testeos de ese rango y que ha respondido de manera consecutiva al momento actual
F-->Número de testeos de ese rango y que no ha respondido
FS-->Número de testeos de ese rango y que no ha respondido de manera consecutiva al momento actual

Si queremos resetear los contadores, antes de la ejecución borraremos el fichero dic_rangos_cont.dat.
Si queremos borrar los rangos, antes de la ejecución borraremos el fichero dic_rangos.dat y dic_rangos_cont.dat.

En el fichero mail.txt tendremos el resultado del ultimo mail de reporte enviado.

En el fichero log.txt tendremos los logs que se guardan cada "LOG_CADA" pasadas



Programado por David.hernandezc@gmail.com

