#!/usr/bin/python3


import daemon
import inotify.adapters
import os
import sys
import OpenSSL
import socket
import subprocess
import OpenSSL
from OpenSSL.SSL import TLSv1_2_METHOD


HOST = '127.0.1.1'
PORT = 1234
audit_log = '.audit.log'


#Funcion demonio
#def daemonTask():
	#i = inotify.adapters.InotifyTree('/home/tfg/Escritorio')
	#print(os.getpid())
	#for event in i.event_gen(yield_nones=False):
	#	(_, type_names, path, filename) = event
		#logFile.write("{}: {} [{}]\n".format(type_names, path, filename))
		#print("{}: {} [{}]".format(type_names, path, filename))
		#print(event)



###############################################
#COMPROBAR USUARIO EXISTE
if len(sys.argv) < 4 or sys.argv[2] != '-ip':
	print('Número de argumentos incorrecto.\nSigue el siguiente esquema: ./demonio username -ip IP,PORT [-s kill,execve,etc] [--restart]')
	os._exit(0)

usuario = sys.argv[1]
if not os.path.isdir('/home/'+usuario):
	print("El usuario '{}' NO existe. Prueba con otro.".format(usuario))
	os._exit(0)


ip_port = sys.argv[3].split(',')
HOST = ip_port[0]
PORT = int(ip_port[1])


################################################
#CREACION FICHERO PARA COMPROBAR USUARIO ROOT CON is_sudo de processhider.c
if not os.path.isfile('/etc/hola'):
	os.system("touch /etc/hola")
os.system("chmod 600 /etc/hola")


#################################################
# Funcion para reiniciar y reconfigurar auditd
def restart_auditd():
	os.system('systemctl stop auditd')
	os.system('rm /home/'+usuario+'/'+audit_log)
	with open('/etc/audit/auditd.conf', "w") as audit_conf:
		audit_conf.write ('#\n# This file controls the configuration of the audit daemon\n#\n'
			'local_events = yes\n'
			'write_logs = yes\n'
			'log_file = /home/'+usuario+'/'+audit_log+'\n'
			'log_group = adm\n'
			'log_format = ENRICHED\n'
			'flush = INCREMENTAL_ASYNC\n'
			'freq = 50\n'
			'max_log_file = 8\n'
			'num_logs = 5\n'
			'priority_boost = 4\n'
			'disp_qos = lossy\n'
			'dispatcher = /sbin/audispd\n'
			'name_format = NONE\n'
			'##name = mydomain\n'
			'max_log_file_action = ROTATE\n'
			'space_left = 75\n'
			'space_left_action = SYSLOG\n'
			'verify_email = yes\n'
			'action_mail_acct = root\n'
			'admin_space_left = 50\n'
			'admin_space_left_action = SUSPEND\n'
			'disk_full_action = SUSPEND\n'
			'disk_error_action = SUSPEND\n'
			'use_libwrap = yes\n'
			'##tcp_listen_port = 60\n'
			'tcp_listen_queue = 5\n'
			'tcp_max_per_addr = 1\n'
			'##tcp_client_ports = 1024-65535\n'
			'tcp_client_max_idle = 0\n'
			'enable_krb5 = no\n'
			'krb5_principal = auditd\n'
			'##krb5_key_file = /etc/audit/audit.key\n'
			'distribute_network = no\n')

	os.system('touch /home/'+usuario+'/'+audit_log)
	with open('/etc/audit/rules.d/audit.rules', "w") as audit_rules:
		audit_rules.write('## First rule - delete all\n'
			'-D\n\n'
			'## Increase the buffers to survive stress events.\n'
			'## Make this bigger for busy systems\n'
			'-b 8192\n\n'
			'## This determine how long to wait in burst of events\n'
			'--backlog_wait_time 0\n\n'
			'## Set failure mode to syslog\n'
			'-f 1\n\n')
		syscalls = sys.argv[5].split(',')
		for s in syscalls:
			audit_rules.write('-a always,exit -F arch=b64 -S '+s+' -k '+s+'_rule -F uid='+usuario+'\n')

	os.system('systemctl restart auditd')


################################################
# Aniadir syscalls a auditd
def add_syscall():
	os.system('systemctl stop auditd')
	with open('/etc/audit/rules.d/audit.rules', "a") as audit_rules:
		syscalls = sys.argv[5].split(',')
		for s in syscalls:
			audit_rules.write('-a always,exit -F arch=b64 -S '+s+' -k '+s+'_rule -F uid='+usuario+'\n')

	os.system('systemctl restart auditd')


################################################
# Gestion de auditd segun argumentos de entrada
if (len(sys.argv) == 7 and sys.argv[6] == '--restart' and sys.argv[4] == '-s') or not os.path.isfile('/home/'+usuario+'/'+audit_log):
	restart_auditd()
elif len (sys.argv) == 6 and sys.argv[4] == '-s':
	add_syscall()



###############################################
#COMPILACION E INSERCION LIBRERIA DINAMICA
os.system("make")
os.system("mv libprocesshider.so /usr/local/lib/")
os.system("echo /usr/local/lib/libprocesshider.so >> /etc/ld.so.preload")



##############################################
#ESTRUCTURACION DIRECTORIO DE EVIDENCIAS
hiddenD = "/etc/dpkg/origins/..."
"""os.system("mkdir {}".format(hiddenD))
os.system("mkdir {}/Descargas".format(hiddenD))
os.system("mkdir {}/Escritorio".format(hiddenD))
os.system("mkdir {}/Música".format(hiddenD))
os.system("mkdir {}/Público".format(hiddenD))
os.system("mkdir {}/Documentos".format(hiddenD))
os.system("mkdir {}/Imágenes".format(hiddenD))
os.system("mkdir {}/Plantillas".format(hiddenD))
os.system("mkdir {}/Vídeos".format(hiddenD))"""
if not os.path.isdir(hiddenD):
	os.system("mkdir "+hiddenD)
hiddenD = hiddenD+'/'+usuario
os.system("cp -r /home/{} {}".format(usuario, hiddenD))
os.system("chmod 600 "+hiddenD)
with open(hiddenD+'/'+audit_log, "w") as reader:
	pass


		

#########################################################
# AGENTE DE ENGAÑO: monitoriza todos los eventos en el sistema de ficheros
def agent():
	# Create context for de TLS session
	context = OpenSSL.SSL.Context(TLSv1_2_METHOD)

	# Create connection
	conn = OpenSSL.SSL.Connection(context, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
	conn.set_connect_state()

	# Connect to server
	conn.connect((HOST, PORT))

	i = inotify.adapters.InotifyTree('/home/'+usuario)
	# Variables
	create = 0
	modify = 0
	move = 0
	move_to = 0
	delete = 0
	fichero = ""
	aux_destiny = ""
	aux_source = ""
	IN_ISDIR = 0
	flag_aux = 0

	options = {0:"FICHERO", 1:"DIRECTORIO"}

	content_aux = '# date time key success exe auid event\n===============================================\n'

	for event in i.event_gen(yield_nones=False):
		(extra_info, type_names, path, filename) = event				
			
		#no_metadatos = ".local" not in path and ".cache" not in path and ".config" not in path and ".swp" not in filename
		no_metadatos = "." not in path and ".swp" not in filename

		if no_metadatos:

			source = path+"/"+filename
			destiny = hiddenD+path.split(usuario)[1]+"/"+filename

			#BORRAR, ES PARA PRUEBA
			if "flask" in path:
				pass

			# AUDITD LOG HANDLING
			elif filename == audit_log and 'IN_MODIFY' in type_names:

				cmd_aureport = "aureport -k"
				p = subprocess.Popen(cmd_aureport, shell=True, stdout=subprocess.PIPE)
				content = p.stdout.read().decode()

				lista_aux = content.split(content_aux)
				if len(lista_aux) > 1 and lista_aux[1] != '':
					res = lista_aux[1]
					try:
						conn.write(res)
					except OpenSSL.SSL.SysCallError as e:
						pass	
					content_aux = res

			# REST OF FILESYSTEM HANDLING
			elif 'IN_CREATE' in type_names:
				create = 1

			elif 'IN_CLOSE_WRITE' in type_names:
				# copiar fichero, ya sea por creacion o por modificacion					
				os.system("cp -r {} {}".format(source, destiny))
				if create == 1:
					conn.write("FICHERO '{}'\tCREADO en la ruta {}\n".format(filename, source))
					create = 0
				elif move_to == 1 or modify == 1:					
					conn.write("FICHERO '{}'\tMODIFICADO en la ruta {}\n".format(filename, source))
					move_to = modify = 0


			elif 'IN_CLOSE_NOWRITE' in type_names:
				# copiar dir
				if create==1 and 'IN_ISDIR' in type_names:						
					os.system("cp -r {} {}".format(source, destiny)) 
					print ("cp -r {} {}".format(source, destiny))
					conn.write("DIRECTORIO '{}'\tCREADO en la ruta {}\n".format(filename, source))
					create = 0

			elif 'IN_DELETE' in type_names:
				IN_ISDIR = 'IN_ISDIR' in type_names
				aux_destiny = destiny
				destiny = hiddenD+path.split(usuario)[1]+"/DELETED_"+filename
				os.system("mv {} {}".format(aux_destiny, destiny))
				conn.write("{} '{}'\tELIMINADO en la ruta {}\n".format(options[IN_ISDIR],filename, source))
				#logica para eliminar tanto dir como files

			elif 'IN_MOVED_FROM' in type_names:
				move = 1
				fichero = filename
				aux_source = source
				aux_destiny = destiny

			elif 'IN_MOVED_TO' in type_names:
				# comprobar move==1 y mover	
				if move == 1:
					IN_ISDIR = 'IN_ISDIR' in type_names
					os.system("mv {} {}".format(aux_destiny, destiny))
					conn.write("{} '{}'\tMOVIDO de la ruta {} a la ruta {}\n".format(options[IN_ISDIR], fichero, aux_source, source))
					move = 0
				else:
					move_to = 1

			elif 'IN_MODIFY' in type_names:
				modify = 1
		

#############################################################
# DEMONIZACION
#with daemon.DaemonContext(stdout=sys.stdout):
agent()
