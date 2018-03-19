#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, os.path
import sys
import time
import math
import pygame
import threading
import subprocess



""" constantes colores y presentacion """

COLOR_TITULO_LISTA = (255,255,255) #blanco
COLOR_LISTA = (204,204,0) #oro
COLOR_VIDEO = (0,204,0) #verde
COLOR_URL = (255,51,255) #morado
COLOR_IMAGEN = (255,133,51) #naranja
COLOR_DIRECTORIO = (51,133,255) #azul
COLOR_SCRIPT = (255,0,0) #rojo

COLOR_PAGINACION = (128,128,128) #gris

#[(1600, 1200), (1280, 1024), (1024, 1024), (1280, 960), (1152, 864), (1024, 768), (1184, 624), (800, 600), (768, 576), (640, 480)]

#SCREEN_SIZE = (1184, 624)
SCREEN_SIZE = (0, 0)
#SCREEN_SIZE = (1280, 720)
#SCREEN_SIZE = (1024, 768)
FONT_SIZE = 52
MARGEN_VERTICAL = 10
MARGEN_HORIZONTAL = 50
GAP = 70
C_FONDO = (0,0,0)
COLOR_BORDE_BORRAR = (128,0,0)
COLOR_SI = (0,128,0)
COLOR_NO = (0,0,158)
COLOR_SELECTOR = (40,40,40)
FACTOR_SEPARACION_ELEMENTOS = 1.4
FACTOR_SEPARACION_LISTA = 2


""" constantes modo lista """

TIPO_VIDEO = 0
TIPO_IMAGEN = 1
TIPO_URL = 2
TIPO_PLAYLIST = 3
TIPO_DIRECTORIO = 4
TIPO_SCRIPT = 5

NOMBRE_TIPOS = {
	TIPO_VIDEO: 'vídeo', 
	TIPO_IMAGEN: 'imagen', 
	TIPO_URL: 'enlace', 
	TIPO_PLAYLIST: 'lista', 
	TIPO_DIRECTORIO: 'carpeta', 
	TIPO_SCRIPT: 'script'}
COLORES_TIPOS = {
	TIPO_VIDEO: COLOR_VIDEO, 
	TIPO_IMAGEN: COLOR_IMAGEN, 
	TIPO_URL: COLOR_URL, 
	TIPO_PLAYLIST: COLOR_LISTA, 
	TIPO_DIRECTORIO: COLOR_DIRECTORIO, 
	TIPO_SCRIPT: COLOR_SCRIPT}

EXTENSIONES_IMAGENES = ['.jpg', '.jpeg', '.png', '.gif']
EXTENSIONES_VIDEO = ['.avi', '.mkv', '.mp4']
EXTENSION_URL = '.kurl'
EXTENSION_LISTA = '.klist'

NOMBRE_FICHERO = 0 # human readable
TIPO_FICHERO = 1
RUTA_FICHERO = 2

FICHERO_URL_VIDEO = '/var/tmp/webvideo' + EXTENSION_URL

BIBLIOTECAS = [ ('Descargas', TIPO_DIRECTORIO, '/media/datos/descargas'),
	(u'Películas', TIPO_DIRECTORIO, '/media/datos/peliculas') ,
	('Unidad externa', TIPO_DIRECTORIO, '/media/pendrive') ,
	('Montar unidad externa', TIPO_SCRIPT, '/home/pi/bin/montar_pendrive.sh'),
	('Desmontar unidad externa', TIPO_SCRIPT, '/home/pi/bin/desmontar_pendrive.sh')
#	,(u'Vídeo capturado desde el navegador', TIPO_URL, FICHERO_URL_VIDEO)
]

""" modos """
MODO_SPLASH = 0
MODO_GUI = 1
MODO_VIDEO = 2
MODO_IMAGEN = 3
MODO_CARRUSEL = 4   # slide show recursive
MODO_ELIMINAR = 5   # eliminar fichero desde el gui
MODO_ELIMINAR_IMAGEN = 6   # eliminar imagen desde la visualizacion
MODO_SLEEP = 7


""" constantes mando """

PULSAR = '44'
SOLTAR = '8b'

MANDO_IZQUIERDA = '03'
MANDO_DERECHA = '04'
MANDO_ARRIBA = '01'
MANDO_ABAJO = '02'
MANDO_OK = '00'
MANDO_ROJO = '72'
MANDO_VERDE = '73'
MANDO_AMARILLO = '74'
MANDO_AZUL = '71'
MANDO_VOLVER = '0d'
MANDO_SALIR = '2c'
MANDO_OPCION = '0a'

MANDO_SI = MANDO_VERDE
MANDO_NO = MANDO_AZUL


""" constantes omxplayer """

OMX_STOP = "q"
OMX_PLAY_PAUSE = "p"
OMX_AVANCE_RAPIDO = '\\x1b[A'
OMX_AVANCE_LENTO = '\\x1b[C'
OMX_RETROCESO_RAPIDO = '\\x1b[B'
OMX_RETROCESO_LENTO = '\\x1b[D'


""" constantes asociacion botones mando con los de omx """

DIC_MANDO_OMXP = {MANDO_IZQUIERDA: OMX_RETROCESO_LENTO, MANDO_DERECHA: OMX_AVANCE_LENTO,
	MANDO_ARRIBA: OMX_AVANCE_RAPIDO, MANDO_ABAJO: OMX_RETROCESO_RAPIDO,
	MANDO_OK: OMX_PLAY_PAUSE,
	MANDO_SALIR: OMX_STOP, MANDO_VOLVER: OMX_STOP }


""" constantes carrusel """
PLAY = True
PAUSE = False


""" variables globales """

renombrar = None  # modulo renombrar
salir = False
modo = None
modo_anterior = None
fichero_reproducir = None
proceso_omxplayer = None

# pantalla
screen = None
font = None
altura_texto = 0
screen_size = (0,0)

# lista modo gui
elementos_lista = []  # elementos de la lista que se esta mostrando
tipo_lista = None  # tipo de lista que se esta mostrando
titulo_lista = ''  # titulo de ls lista que se esta mostrando (directorio principalmente)
filas_pagina = None  # numero de filas que caben en una pagina de la lisata
cursor = 0  # posicion del cursor en la lista
fichero_seleccionado = None  # fichero_anterior seleccionado para reproducir
num_paginas = 0  # numero de paginas de la lista
pila_listas = None  # pila de listas que se van viendo recursivamente

# carrusel imagenes
lista_imagenes = None  # lista de imagenes
tiempo_entre_imagenes = 3.0
contador_tiempo = 0
cursor_imagenes = 0
play_pause = PLAY
estado_play_pause = None
fin_carrusel_imagenes = False
imagen_seleccionada = None

# url video capturado
ultima_fecha = 0
hilo_fecha_fichero = None


#########################


def u(str):
	return unicode(str, 'utf-8')

 

#########################
##   G R A F I C O S   ##
#########################


def init_graficos():
	global screen, font, altura_texto, screen_size, filas_pagina

	#pygame.init()
	pygame.display.init()
	#print_info_graficos()
	pygame.mouse.set_visible(False)

	screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN | pygame.HWSURFACE)
	screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
	print 'screen_size', screen_size

	screen.fill( (0,0,110) )
	pygame.draw.rect(screen, C_FONDO, (10,10,screen_size[0]-20,screen_size[1]-20) )
	actualizar_graficos()

	# calculos
	pygame.font.init()
	font = pygame.font.Font(None, FONT_SIZE)
	text = font.render("Kodillo", 1, (110, 110, 250))
	altura_texto = text.get_height()
	print 'altura_texto', altura_texto
	num_filas = screen_size[1] - 2*MARGEN_VERTICAL - 2*altura_texto*FACTOR_SEPARACION_LISTA
	filas_pagina = int(num_filas / (altura_texto*FACTOR_SEPARACION_ELEMENTOS))
	print 'filas_pagina', filas_pagina



def print_info_graficos():
	print 'MODOS:', pygame.display.list_modes()
	print 'INFO:', pygame.display.Info()
	print 'DRIVER:', pygame.display.get_driver()



def actualizar_graficos():
	pygame.display.update()



def caja_input_si_no(texto1, color1, texto2=None, color2=COLOR_TITULO_LISTA):
	global screen, screen_size, font

	text1 = font.render(texto1, 1, color1)
	if texto2:
		text2 = font.render(texto2, 1, color2)
	text_si = font.render(u'  Sí  ', 1, COLOR_TITULO_LISTA, COLOR_SI )
	text_no = font.render('  No  ', 1, COLOR_TITULO_LISTA, COLOR_NO )

	ancho = altura_texto*4
	if texto2:
		ancho += max(text1.get_width(), text2.get_width())
		alto = altura_texto * 9
	else:
		ancho += text1.get_width()
		alto = altura_texto * 7
	#print 'caja', (ancho, alto)
	caja = pygame.Surface( (ancho, alto) )
	caja.fill(COLOR_BORDE_BORRAR)
	pygame.draw.rect(caja, C_FONDO, (altura_texto,altura_texto,ancho-altura_texto*2,alto-altura_texto*2) )

	multy = 2
	caja.blit(text1, (get_X_centrado(text1, ancho), altura_texto*multy) )

	if texto2:
		multy += 2
		caja.blit(text2, (get_X_centrado(text2, ancho), altura_texto*multy) )

	multy += 2
	caja.blit(text_si, (ancho/2-50-text_si.get_width(), altura_texto*multy) )
	caja.blit(text_no, (ancho/2+50,altura_texto*multy) )

	screen.blit(caja, ( (screen_size[0]-ancho)/2 , (screen_size[1]-alto)/2 ) )
	actualizar_graficos()



def get_X_centrado(surface_text, ancho_parent=None):
	if ancho_parent == None:
		ancho_parent = screen_size[0]
	return int((ancho_parent - surface_text.get_width()) / 2)



def get_Y(fila):
	""" devuelve la coordenada Y para la fila dada """
	return MARGEN_VERTICAL + altura_texto*FACTOR_SEPARACION_LISTA + fila*altura_texto*FACTOR_SEPARACION_ELEMENTOS



#####################
##   MODO SPLASH   ##
#####################


def modo_splash():
	global modo, kodillo_path

	os.system('sudo sh -c "TERM=linux setterm -blank 0 >/dev/tty0"')
	print 'modo_splash()'
	init_graficos()

	visualizar_imagen('splash.png')
	modo = MODO_SPLASH

	invocar_sh('./modo_sleep_off.sh &')



def splash_ok():
	global pila_listas, cursor, modo, ultima_fecha, renombrar, config

	print 'splash_ok()'
	cursor = 0
	pila_listas = [ ('Bibliotecas', TIPO_DIRECTORIO, '/') ]
	actualizar_lista( pila_listas[-1] )
	ultima_fecha = get_fecha_fichero()

	eliminar_modulo('renombrar')
	import renombrar

	volver_al_modo_gui()



def eliminar_modulo(nombre_modulo):
	try:
		del sys.modules[nombre_modulo]
	except:
		pass



##################
##   MODO GUI   ##
##################



def volver_al_modo_gui():
	global modo, hilo_fecha_fichero

	print 'modo_gui()'
	screen.fill(C_FONDO)
	actualizar_graficos()
	actualizar_lista( pila_listas[-1], fichero_seleccionado )
	modo = MODO_GUI

	#hilo_fecha_fichero = threading.Thread(target=hilo_modo_gui)
	#print 'hilo_fecha_fichero', hilo_fecha_fichero
	#hilo_fecha_fichero.start()



def hilo_modo_gui():
	# comprueba cada x segundos si un fichero .ur1 se ha actualizado
	# si se ha actualizado se abre
	global ultima_fecha

	while modo == MODO_GUI:
		time.sleep(10)
		fecha_nueva = get_fecha_fichero()
		if fecha_nueva > ultima_fecha:
			ultima_fecha = fecha_nueva
			abrir_fichero_url( FICHERO_URL_VIDEO )



def get_fecha_fichero():
	try:
		return os.path.getctime(FICHERO_URL_VIDEO)
	except:
		return 0




def gui_subir_cursor():
	global cursor

	if cursor > 0:
		if cursor % filas_pagina == 0:
			cursor -= 1
			gui_actualizar_pagina()
		else:
			print_elemento(cursor, False)
			cursor -= 1
			print_elemento(cursor, True)
		actualizar_graficos()



def gui_bajar_cursor():
	global cursor

	if cursor < len(elementos_lista)-1:
		if cursor % filas_pagina == (filas_pagina-1):
			cursor += 1
			gui_actualizar_pagina()
		else:
			print_elemento(cursor, False)
			cursor += 1
			print_elemento(cursor, True)
		actualizar_graficos()



def gui_avanzar_pagina():
	global cursor

	if get_pagina(cursor) < num_paginas-1:
		cursor += filas_pagina
		if cursor >= len(elementos_lista):
			cursor = len(elementos_lista) - 1
		gui_actualizar_pagina()
		actualizar_graficos()



def gui_retroceder_pagina():
	global cursor

	if get_pagina(cursor) > 0:
		cursor -= filas_pagina
		gui_actualizar_pagina()
		actualizar_graficos()



def gui_actualizar_pagina():
	print '------pagina------'
	ini = get_pagina(cursor) * filas_pagina
	fin = min(ini+filas_pagina, len(elementos_lista))
	#print 'ini fin',ini,fin
	e = 0

	for i in range(ini, fin):
		try:
			print_elemento(i, i == cursor)
			e += 1
		except Exception as err:
			print err
	while e < filas_pagina:
		borrar_fila(e)
		e += 1
	print '------- %d/%d ------' % ( get_pagina(cursor) + 1, num_paginas )

	s = '<  %d/%d  >' % (get_pagina(cursor) + 1, num_paginas)
	text = font.render(s, 1, COLOR_PAGINACION, C_FONDO)

	screen.blit(text, (get_X_centrado(text), screen_size[1]-MARGEN_HORIZONTAL-altura_texto) )



def gui_actualizar_lista():
	try:
		fichero_ant = elementos_lista[cursor]
	except:
		fichero_ant = elementos_lista[-1]

	actualizar_lista( pila_listas[-1], fichero_ant )



def actualizar_lista(fichero, fichero_ant=None):
	global elementos_lista, titulo_lista, tipo_lista, num_paginas, cursor

	tipo_lista = fichero[TIPO_FICHERO]
	titulo_lista = fichero[NOMBRE_FICHERO]

	if fichero[RUTA_FICHERO] == '/':
		elementos_lista = BIBLIOTECAS
	elif tipo_lista == TIPO_DIRECTORIO:
		get_ficheros(fichero[RUTA_FICHERO])
	elif tipo_lista == TIPO_PLAYLIST:
		#print 'playlist', 
		get_elementos_playlist(fichero[RUTA_FICHERO])

	num_paginas = int(math.ceil( (len(elementos_lista)+0.0) /filas_pagina))
	#print 'num_paginas', num_paginas

	if fichero_ant:
		if fichero_ant in elementos_lista:
			cursor = elementos_lista.index(fichero_ant)
		elif cursor >= len(elementos_lista):	
			cursor = len(elementos_lista) - 1
	else:
		cursor = 0

	print_titulo_lista()
	gui_actualizar_pagina()
	actualizar_graficos()



def gui_borrar():
	#global cursor, screen, screen_size, font, modo
	global modo

	print 'gui_borrar()', fichero_seleccionado
	tipo = NOMBRE_TIPOS[fichero_seleccionado[TIPO_FICHERO]]
	#print tipo
	#print '¿Borrar %s?' % unicode(tipo, 'utf-8')
	caja_input_si_no( u('¿Borrar %s?' % tipo), COLOR_TITULO_LISTA, 
		fichero_seleccionado[NOMBRE_FICHERO], COLOR_TITULO_LISTA  )

	actualizar_graficos()
	modo = MODO_ELIMINAR



""" seleccionar un elemento de la lista """
def gui_seleccionar():
	print 'gui_seleccionar()', fichero_seleccionado

	if fichero_seleccionado[TIPO_FICHERO] in [TIPO_DIRECTORIO,TIPO_PLAYLIST]:
		pila_listas.append( fichero_seleccionado )
		actualizar_lista( fichero_seleccionado )
	elif fichero_seleccionado[TIPO_FICHERO] == TIPO_VIDEO:
		modo_video( fichero_seleccionado[RUTA_FICHERO] )
	elif fichero_seleccionado[TIPO_FICHERO] == TIPO_IMAGEN:
		modo_imagen( fichero_seleccionado[RUTA_FICHERO] )
	elif fichero_seleccionado[TIPO_FICHERO] == TIPO_URL:
		abrir_fichero_url( fichero_seleccionado[RUTA_FICHERO] )
	elif fichero_seleccionado[TIPO_FICHERO] == TIPO_SCRIPT:
		invocar_sh(fichero_seleccionado[RUTA_FICHERO])



def gui_carrusel_imagenes():
	print 'gui_carrusel_imagenes()', fichero_seleccionado

	if fichero_seleccionado[TIPO_FICHERO] == TIPO_DIRECTORIO:
		modo_carrusel(fichero_seleccionado[RUTA_FICHERO], recursivo=True)
	elif fichero_seleccionado[TIPO_FICHERO] == TIPO_IMAGEN:
		directorio, fichero = os.path.split( fichero_seleccionado[RUTA_FICHERO] )
		modo_carrusel(directorio, recursivo=False)



""" volver a la lista padre """
def gui_volver():
	global cursor

	if len(pila_listas) > 1:
		fichero_anterior = pila_listas.pop()
		#print 'fichero_anterior', fichero_anterior
		fichero_actual = pila_listas[-1]
		#print 'fichero actual', fichero_actual
		actualizar_lista(fichero_actual, fichero_anterior)



def gui_salir():
	# pasar al modo sleep
	global modo

	print 'gui_salir()'
	modo = MODO_SLEEP
	pygame.display.quit()

	invocar_sh('./modo_sleep_on.sh')


### helpers ###


# obtiene los ficheros de un directorio
def get_ficheros(path):
	global elementos_lista, renombrar

	print 'get_ficheros(%s)' % path
	elementos_lista = []
	ff = os.listdir(path)
	print 'ficheros en dir:', len(ff)#, ff
	ff.sort()

	for fichero in ff:
		try:
			fichero = path + '/' + fichero
			namext = os.path.basename(fichero)
			name, ext = os.path.splitext(namext)
			name = u(name)
			ext = ext.lower()

			if os.path.isdir(fichero):
				name = renombrar.renombrar( u(namext) )
				elementos_lista.append( (name, TIPO_DIRECTORIO, fichero) )
			elif ext in EXTENSIONES_VIDEO:
				name = renombrar.renombrar(name)
				elementos_lista.append( (name, TIPO_VIDEO, fichero) )
			elif ext in EXTENSIONES_IMAGENES:
				elementos_lista.append( (name, TIPO_IMAGEN, fichero) )
			elif ext == EXTENSION_URL:
				elementos_lista.append( (name, TIPO_URL, fichero) )
			elif ext == EXTENSION_LISTA:
				elementos_lista.append( (name, TIPO_PLAYLIST, fichero) )
		except Exception as err:
			print fichero, err



# obtiene los elementos de un fichero playlist
def get_elementos_playlist(fichero_lista):
	global elementos_lista

	print 'get_elementos_playlist(%s)' % fichero_lista
	elementos_lista = []
	infile = open(fichero_lista, 'r')
	#print 'infile', infile

	for line in infile:
		igual = line.find('=')
		print line, igual
		if igual > 0:
			nombre = u(line[:igual]).strip()
			ruta = line[igual+1:].strip()
			print nombre, ruta
			elementos_lista.append( (nombre, TIPO_VIDEO, ruta) )



def abrir_fichero_url(f):
	infile = open(f, 'r')
	# Mostramos por pantalla lo que leemos desde el fichero
	url = infile.readline().strip()
	# Cerramos el fichero.
	infile.close()
	print 'Reproducir:', url
	modo_video( url )
	
		

""" fila de la pagina que le corresponde a un fichero """
def get_fila(num_elemento_lista):
	return num_elemento_lista % filas_pagina



""" pagina a la que pertenece un fichero (para visualizar en la lista) """
def get_pagina(num_elemento_lista=cursor):
	return int(num_elemento_lista / filas_pagina)



def borrar_fila(fila):
	pintar_selector(fila, C_FONDO)



def pintar_selector(fila, color):
	global screen

	ancho = screen_size[0] - 2*MARGEN_HORIZONTAL
	pygame.draw.rect(screen, color, (MARGEN_HORIZONTAL, get_Y(fila), ancho, altura_texto) )



""" pinta un elemento de la lista """
def print_elemento(i, seleccion=False):
	global screen, font, fichero_seleccionado

	ele = elementos_lista[i]
	#sel = {False: ' ', True: '*'} [seleccion]
	#print '[%s] %s' % (sel, ele[NOMBRE_FICHERO])

	color_selector = {True: COLOR_SELECTOR, False: C_FONDO} [seleccion]
	fila = get_fila(i)
	pintar_selector(fila, color_selector)

	color_texto = COLORES_TIPOS[ele[TIPO_FICHERO]]
	#texto = unicode(ele[NOMBRE_FICHERO, 'utf-8')
	text = font.render(ele[NOMBRE_FICHERO], 1, color_texto)

	screen.blit(text, (GAP, get_Y(fila)))

	if seleccion:
		fichero_seleccionado = elementos_lista[cursor]



def print_titulo_lista():
	global screen

	#print 'Titulo:', titulo_lista
	text = titulo_lista.ljust(100,' ')
	text = font.render(text, 1, COLOR_TITULO_LISTA, C_FONDO)
	screen.blit(text, (GAP, MARGEN_VERTICAL))



##################################################
##   modo eliminar ficheros desde el modo gui   ##
##################################################


def eli_eliminar():
	print 'eli_eliminar()', fichero_seleccionado

	if fichero_seleccionado[TIPO_FICHERO] == TIPO_DIRECTORIO:
		cmd = 'rm -Rf "%s"'% fichero_seleccionado[RUTA_FICHERO]
	else:
		cmd = 'rm -f "%s"'% fichero_seleccionado[RUTA_FICHERO]

	print cmd
	os.system(cmd)
	volver_al_modo_gui()



def eli_noEliminar():
	volver_al_modo_gui()



####################
##   MODO VIDEO   ##
####################


def modo_video(uri):
	global fichero_reproducir

	invocar_sh('antes_video.sh')
	fichero_reproducir = uri
	hilo_omxplayer = threading.Thread(target=hilo_modo_video)
	print hilo_omxplayer
	hilo_omxplayer.start()



def hilo_modo_video():
	global modo, proceso_omxplayer

	modo = MODO_VIDEO

	args = ['/usr/bin/omxplayer', fichero_reproducir]
	print args
	proceso_omxplayer = subprocess.Popen(args, stdin=subprocess.PIPE)
	screen.fill( (0,0,0) )
	print 'omxplayer lanzado, proceso=', proceso_omxplayer
	proceso_omxplayer.wait()
	print 'omxplayer terminado, proceso=', proceso_omxplayer
	invocar_sh('despues_video.sh')
	volver_al_modo_gui()



def procesar_orden_omxplayer(boton_mando):
	global proceso_omxplayer

	print boton_mando
	cmd_omxp = DIC_MANDO_OMXP[boton_mando]
	proceso_omxplayer.stdin.write(cmd_omxp)
	print 'comando enviado a omxplayer'



def invocar_sh(cmd):
	try:
		os.system(cmd)
	except Exception as err:
		print cmd, err



#####################
##   MODO IMAGEN   ##
#####################



def modo_imagen(fichero):
	global modo

	print 'modo_imagen()', fichero
	modo = MODO_IMAGEN
	visualizar_imagen(fichero)



def visualizar_imagen(path):
	global screen, screen_size, imagen_seleccionada

	imagen_seleccionada = path
	image = pygame.image.load(path)
	tam_imagen = image.get_size()
	factor_x = (0.0 + screen_size[0]) / tam_imagen[0]
	factor_y = (0.0 + screen_size[1]) / tam_imagen[1]

	min_factor = min(factor_x, factor_y)
	new_width  = int(min_factor * tam_imagen[0])
	new_height = int(min_factor * tam_imagen[1])

	x = (screen_size[0] - new_width) / 2
	y = (screen_size[1] - new_height) / 2

	image = pygame.transform.smoothscale(image, (new_width, new_height) )

	screen.fill((0,0,0))
	screen.blit(image, (x,y))
	actualizar_graficos()



def img_borrar():
	#global cursor, screen, screen_size, font, modo, modo_anterior, estado_play_pause, play_pause
	global cursor, modo, modo_anterior, estado_play_pause, play_pause

	if modo == MODO_CARRUSEL:
		estado_play_pause = play_pause
		play_pause = PAUSE
	modo_anterior = modo
	modo = MODO_ELIMINAR_IMAGEN

	caja_input_si_no(u'¿Borrar imagen?', COLOR_TITULO_LISTA )



###############################################
##   MODO ELIMINAR IMAGEN QUE SE VISUALIZA   ##
###############################################


def elimg_eliminar():
	global lista_imagenes, cursor_imagenes, modo, play_pause, estado_play_pause

	print 'rm -f "%s"' % imagen_seleccionada
	os.system('rm -f "%s"' % imagen_seleccionada)
	modo = modo_anterior
	
	if modo_anterior == MODO_CARRUSEL:
		lista_imagenes.remove(imagen_seleccionada)
		cursor_imagenes -= 1
		car_siguiente()
		play_pause = estado_play_pause
	elif modo_anterior == MODO_IMAGEN:
		volver_al_modo_gui()



def elimg_noEliminar():
	global modo, play_pause

	modo = modo_anterior
	visualizar_imagen(imagen_seleccionada)

	if modo_anterior == MODO_CARRUSEL:
		play_pause = estado_play_pause
	


#######################
##   MODO CARRUSEL   ##
#######################



def modo_carrusel(directorio, recursivo=True):
	global lista_imagenes

	print 'carrusel:', directorio, '    recursivo:', recursivo

	if recursivo:
		lista_imagenes = get_imagenes_directorio_recur(directorio)
	else:
		lista_imagenes = get_imagenes_directorio(directorio)
	print 'imagenes',  lista_imagenes
	hilo_carrusel = threading.Thread(target=hilo_modo_carrusel)
	print 'hilo_carrusel', hilo_carrusel
	hilo_carrusel.start()



def hilo_modo_carrusel():
	global contador_tiempo, cursor_imagenes, play_pause, modo, fin_carrusel_imagenes, lista_imagenes

	modo = MODO_CARRUSEL
	cursor_imagenes = 0
	play_pause = PLAY
	fin_carrusel_imagenes = False

	#print 'lista_imagenes', lista_imagenes
	while not fin_carrusel_imagenes:
		print cursor_imagenes, len(lista_imagenes), lista_imagenes[cursor_imagenes]
		visualizar_imagen(lista_imagenes[cursor_imagenes])
		contador_tiempo = tiempo_entre_imagenes
		while contador_tiempo > 0.0:
			time.sleep(0.25)
			if play_pause == PLAY:
				contador_tiempo -= 0.25
		cursor_imagenes += 1
		if cursor_imagenes == len(lista_imagenes):
			cursor_imagenes = 0

	lista_imagenes = None
	volver_al_modo_gui()



def get_imagenes_directorio(directorio):
	imagenes = []
	ff = os.listdir(directorio)

	for x in ff:
		name, ext = os.path.splitext(x)
		ext = ext.lower()

		if ext in EXTENSIONES_IMAGENES:
			imagenes.append( directorio + '/' + x )

	imagenes.sort()
	return imagenes



def get_imagenes_directorio_recur(directorio):
	imagenes = []
	for root, dirs, files in os.walk(directorio, topdown=True):
		imagenes_directorio = []
		for name in files:
			filename, extension = os.path.splitext(name)
			extension = extension.lower()
			if extension in EXTENSIONES_IMAGENES:
				filepath = os.path.join(root, name)
			imagenes_directorio.append(filepath)
		imagenes_directorio.sort()
		imagenes.extend(imagenes_directorio)

	return imagenes



def car_play_pause():
	global play_pause

	play_pause = not play_pause



def car_siguiente():
	global contador_tiempo

	contador_tiempo = 0



def car_anterior():
	global cursor_imagenes, contador_tiempo

	cursor_imagenes = cursor_imagenes - 2
	contador_tiempo = 0



def car_incrementar_delay():
	global tiempo_entre_imagenes
	tiempo_entre_imagenes += 1.0
	


def car_decrementar_delay():
	global tiempo_entre_imagenes

	if tiempo_entre_imagenes > 1.0:
		tiempo_entre_imagenes += 1.0
	


def car_borrar():
	pass



def car_salir():
	global contador_tiempo, fin_carrusel_imagenes

	contador_tiempo = 0.0
	fin_carrusel_imagenes = True


########################################

def force_quit():
	gui_salir()
	cerrar_programa()

	

def cerrar_programa():
	# salir del programa
	global salir
	salir = True



def procesar_orden(orden):
	print 'modo: %s   orden: %s' % (modo,orden)
	if modo == MODO_VIDEO:
		procesar_orden_omxplayer(orden)
	else:
		if orden in ACCIONES_MODOS[modo]:
			accion = ACCIONES_MODOS[modo][orden]
			print accion
			accion()
		else:
			print 'accion no valida para el modo ', modo



def leer_ordenes_teclado():
	mm = [MANDO_IZQUIERDA,MANDO_DERECHA,MANDO_ARRIBA,MANDO_ABAJO,MANDO_OK,
		MANDO_ROJO,MANDO_VERDE,MANDO_AMARILLO,MANDO_AZUL,MANDO_VOLVER,MANDO_SALIR,MANDO_OPCION]
	tt = ['4', '6', '8', '2', '5',  'ro', 've', 'am', 'az',  'v', 's', 'o']

	while not salir:
		cmd = raw_input('%d? ' % modo)
		try:
			boton = tt.index(cmd)
			boton = mm[boton]
			procesar_orden(boton)
		except:
			pass



def leer_ordenes_mando():
	while not salir:
		cmd = raw_input()
		#cmd = raw_input('%d? ' % modo)
		#print cmd

		if cmd.startswith('TRAFFIC') and '>> 0' in cmd:
			try:
				# >> 04:xx:ff
				pos_codigo = cmd.find('>> 0') + 6
				cmd = cmd[pos_codigo:]
				evento, boton = cmd.split(':')
				print 'cmd:', cmd

				if evento == PULSAR:
					procesar_orden(boton)
			except Exception as ex:
				#print ex
				pass


###########################################################


""" asociacion ordenes de mando con los metodos a invocar en funcion del modo """

ACCIONES_GUI = { MANDO_IZQUIERDA: gui_retroceder_pagina, MANDO_DERECHA: gui_avanzar_pagina,
	MANDO_ARRIBA: gui_subir_cursor, MANDO_ABAJO: gui_bajar_cursor,
	MANDO_OK: gui_seleccionar, MANDO_ROJO: gui_borrar, MANDO_AMARILLO: gui_carrusel_imagenes,
	MANDO_AZUL: gui_actualizar_lista, MANDO_VOLVER: gui_volver, MANDO_SALIR: gui_salir,
	MANDO_OPCION: force_quit }

ACCIONES_ELIMINAR = { MANDO_SI: eli_eliminar,
	MANDO_NO: eli_noEliminar, MANDO_VOLVER: eli_noEliminar, MANDO_SALIR: eli_noEliminar,
	MANDO_OPCION: force_quit}

ACCIONES_IMG = { MANDO_ROJO: img_borrar, 
	MANDO_OK: volver_al_modo_gui, MANDO_VOLVER: volver_al_modo_gui, MANDO_SALIR: volver_al_modo_gui,
	MANDO_OPCION: force_quit}

ACCIONES_ELIMINAR_IMAGEN = { MANDO_SI: elimg_eliminar,
	MANDO_NO: elimg_noEliminar, MANDO_VOLVER: elimg_noEliminar, MANDO_SALIR: elimg_noEliminar,
	MANDO_OPCION: force_quit}

ACCIONES_CARRUSEL = { MANDO_IZQUIERDA: car_anterior, MANDO_DERECHA: car_siguiente,
	MANDO_ARRIBA: car_incrementar_delay, MANDO_ABAJO: car_decrementar_delay,
	MANDO_OK: car_play_pause, MANDO_ROJO: img_borrar,
	MANDO_VOLVER: car_salir, MANDO_SALIR: car_salir,
	MANDO_OPCION: force_quit }

ACCIONES_SLEEP = { MANDO_VERDE: modo_splash, MANDO_ROJO: modo_splash, 
	MANDO_AZUL: cerrar_programa, MANDO_SALIR: cerrar_programa }

ACCIONES_SPLASH = { MANDO_OK: splash_ok,
	MANDO_OPCION: force_quit }

ACCIONES_MODOS = {MODO_GUI: ACCIONES_GUI, MODO_ELIMINAR: ACCIONES_ELIMINAR,
	MODO_IMAGEN: ACCIONES_IMG, MODO_CARRUSEL: ACCIONES_CARRUSEL, MODO_ELIMINAR_IMAGEN: ACCIONES_ELIMINAR_IMAGEN,
	MODO_SLEEP: ACCIONES_SLEEP, MODO_SPLASH: ACCIONES_SPLASH }


###########################################################


modo_splash()

print 'esperando eventos ...'

leer_ordenes_mando()
#leer_ordenes_teclado()

print 'FIN. Esperando fin hilo...'

