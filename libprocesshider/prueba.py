#!/usr/bin/python3


import daemon
import inotify.adapters
import os
import sys

IN_ISDIR = 0

#summaryFile = open(hiddenD+"/summaryLog.txt", "a")

options = {0:"FICHERO", 1:"DIRECTORIO"}
i = inotify.adapters.InotifyTree('/home/prueba2')

for event in i.event_gen(yield_nones=False):
	print(str(event)+"\n")

"""	(_, type_names, path, filename) = event
	if 'IN_ISDIR' in type_names:
		IN_ISDIR = 1
	else:
		IN_ISDIR = 0


	if 'IN_CREATE' in type_names:
		summaryFile.write("{} '{}'\tCREADO en {}\n".format(options[IN_ISDIR], filename, path))
		d = hiddenD+path.split(usuario)[1]+"/"+filename
		if IN_ISDIR == 1:
			os.system("mkdir {}".format(d))
		else:
			os.system("touch {}".format(d))
	elif 'IN_DELETE' in type_names:
		summaryFile.write("{} '{}'\tELIMINADO de la ruta {}\n".format(options[IN_ISDIR], filename, path))
	elif 'IN_MOVED_FROM' in type_names:
		summaryFile.write("{} '{}'\tMOVIDO DE la ruta {}\n".format(options[IN_ISDIR], filename, path))
	elif 'IN_MOVED_TO' in type_names:
		summaryFile.write("{} '{}'\tMOVIDO A la ruta {}\n".format(options[IN_ISDIR], filename, path))			
	elif 'IN_MODIFY' in type_names:
		summaryFile.write("{} '{}'\tMODIFICADO en la ruta {}\n".format(options[IN_ISDIR], filename, path))
	elif 'IN_CLOSE_WRITE' in type_names and ".cache" not in path and ".config" not in path and ".swp" not in filename:
		fuente = path+"/"+filename
		destino = hiddenD+path.split(usuario)[1]
		print("cp {} {}".format(fuente, destino))
		os.system("cp {} {}".format(fuente, destino))"""
		for event in i.event_gen(yield_nones=False):

		(_, type_names, path, filename) = event
		if 'IN_ISDIR' in type_names:
			IN_ISDIR = 1
		else:
			IN_ISDIR = 0
		pruebaFile.write("HOLA 0")
		logFile.write(str(event)+"\n")
		pruebaFile.write("HOLA 1\n")
		pruebaFile.write("HOLA 2\n")
		summaryFile.write("hola llego aqui= 1\n")
		if 'IN_CREATE' in type_names :#and ".cache" not in path and ".config" not in path and ".swp" not in filename:
			summaryFile.write("hola llego aqui= 2\n")
			summaryFile.write("{} '{}'\tCREADO en {}\n".format(options[IN_ISDIR], filename, path))
			d = hiddenD+path.split(usuario)[1]+"/"+filename
			pruebaFile.write("HOLA 3\n")
			if IN_ISDIR == 1:
				os.system("mkdir {}".format(d))
		elif 'IN_DELETE' in type_names:
			summaryFile.write("{} '{}'\tELIMINADO de la ruta {}\n".format(options[IN_ISDIR], filename, path))
			pruebaFile.write("HOLA 4\n")
		elif 'IN_MOVED_FROM' in type_names and ".cache" not in path and ".config" not in path and ".swp" not in filename:
			summaryFile.write("{} '{}'\tMOVIDO DE la ruta {}\n".format(options[IN_ISDIR], filename, path))
			pruebaFile.write("HOLA 5\n")
		elif 'IN_MOVED_TO' in type_names:
			pruebaFile.write("HOLA 6\n")
			if ".config" in path and borrar == 1:
				os.system("cp {} {}".format(fuente, destino))
				borrar = 0
				summaryFile.write("{} '{}'\tMODIFICADO en la ruta {}\n".format(options[IN_ISDIR], fichero, fuente))
			elif ".cache" not in path and ".config" not in path and ".swp" not in filename:
				summaryFile.write("{} '{}'\tMOVIDO A la ruta {}\n".format(options[IN_ISDIR], filename, path))
		elif 'IN_CLOSE_WRITE' in type_names and ".cache" not in path and ".config" not in path and ".swp" not in filename:
			pruebaFile.write("HOLA 7\n")
			borrar = 1
			fuente = path+"/"+filename
			destino = hiddenD+path.split(usuario)[1]+"/"+filename
			fichero = filename