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
import datetime


HOST = '127.0.1.1'
PORT = 1234
audit_log = '.audit.log'


###############################################
#COMPILACION E INSERCION LIBRERIA DINAMICA
if len(sys.argv) == 3 and sys.argv[2] == '-make':
	os.system("make")
	os.system("mv libprocesshider.so /usr/local/lib/")
	if not os.path.isfile("/etc/ld.so.preload"):
		os.system("echo /usr/local/lib/libprocesshider.so >> /etc/ld.so.preload")
	os._exit(0)

###############################################
#COMPROBAR QUE EL ACTIVO EXISTE
if not os.path.isfile('/home/'+sys.argv[1]+'/credenciales/credenciales.txt'):
	print('EL ACTIVO DE ENGAÑO NO EXISTE. Por favor créalo.')
	os._exit(0)


def agent():
	###############################################
	#COMPROBAR USUARIO EXISTE
	if len(sys.argv) < 4 or sys.argv[2] != '-ip':
		print('Número de argumentos incorrecto.\n'
			'Sigue el siguiente esquema: ./agente username -ip IP,PORT [-s kill,execve,etc] [--restart]')
		os._exit(0)

	usuario = sys.argv[1]
	if not os.path.isdir('/home/'+usuario):
		print("El usuario '{}' NO existe. Prueba con otro.".format(usuario))
		os._exit(0)

	ip_port = sys.argv[3].split(',')
	HOST = ip_port[0]
	PORT = int(ip_port[1])


	###############################################
	#BUCLE INFINITO PARA LA ACTIVACION DEL ACTIVO
	i = inotify.adapters.Inotify()
	i.add_watch('/home/'+usuario+'/credenciales')

	for event in i.event_gen(yield_nones=False):
	    (_, type_names, path, filename) = event

	    if filename == 'credenciales.txt' and path == '/home/'+usuario+'/credenciales':
	    	break


	################################################
	#CREACION FICHERO PARA COMPROBAR USUARIO ROOT CON is_sudo de processhider.c
	if not os.path.isfile('/etc/hola'):
		os.system("touch /etc/hola")
	os.system("chmod 600 /etc/hola")


	#################################################
	# Funcion para reiniciar y reconfigurar auditd
	def restart_auditd():
		os.system('systemctl stop auditd')
		if os.path.isfile('/home/'+usuario+'/'+audit_log):
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
		os.system('chmod 600 /home/'+usuario+'/'+audit_log)
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



	##############################################
	#ESTRUCTURACION DIRECTORIO DE EVIDENCIAS
	hiddenD = "/etc/dpkg/origins/..."

	if not os.path.isdir(hiddenD):
		os.system("mkdir "+hiddenD)

	hiddenD = hiddenD+'/'+usuario
	os.system("cp -r /home/{} {}".format(usuario, hiddenD))
	os.system("chmod 600 "+hiddenD)

	if not os.path.isfile(hiddenD+'/auditd.txt'):
		os.system('touch '+hiddenD+'/auditd.txt')



	#########################################################
	# AGENTE DE ENGAÑO: monitoriza todos los eventos en el sistema de ficheros
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
	old = ""

	options = {0:"FICHERO", 1:"DIRECTORIO"}
	
	content_aux = 'Key Report\n===============================================\n# date time key success exe auid event\n===============================================\n'

	with open(hiddenD+'/auditd.txt', "w") as writer:
		writer.write(content_aux)

	for event in i.event_gen(yield_nones=False):
		(extra_info, type_names, path, filename) = event				
			
		#no_metadatos = ".local" not in path and ".cache" not in path and ".config" not in path and ".swp" not in filename
		no_metadatos = "." not in path and ".swp" not in filename

		if no_metadatos:

			source = path+"/"+filename
			destiny = hiddenD+path.split(usuario)[1]+"/"+filename

			#BORRAR, ES PARA PRUEBA
			if "instance" in path:
				pass

			# AUDITD LOG HANDLING
			elif filename == audit_log and 'IN_MODIFY' in type_names:

				cmd_aureport = "aureport -k"
				p = subprocess.Popen(cmd_aureport, shell=True, stdout=subprocess.PIPE)
				content = p.stdout.read().decode()

				lista_aux = content.split('\n')

				with open(hiddenD+'/auditd.txt', "r") as reader:
					old = reader.read()

				with open(hiddenD+'/auditd.txt', "a") as writer:
					for e in lista_aux:
						if e not in old:
							conn.write(e)
							writer.write(e)


			# REST OF FILESYSTEM HANDLING
			elif 'IN_CREATE' in type_names:
				create = 1

			elif 'IN_CLOSE_WRITE' in type_names:
				# copiar fichero, ya sea por creacion o por modificacion					
				os.system("cp -r {} {}".format(source, destiny))
				if create == 1:
					conn.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" FICHERO '{}'\tCREADO en la ruta {}\n".format(filename, source))
					create = 0
				elif move_to == 1 or modify == 1:					
					conn.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" FICHERO '{}'\tMODIFICADO en la ruta {}\n".format(filename, source))
					move_to = modify = 0


			elif 'IN_CLOSE_NOWRITE' in type_names:
				# copiar dir
				if create==1 and 'IN_ISDIR' in type_names:						
					os.system("cp -r {} {}".format(source, destiny)) 					
					conn.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" DIRECTORIO '{}'\tCREADO en la ruta {}\n".format(filename, source))
					create = 0

			elif 'IN_DELETE' in type_names:
				IN_ISDIR = 'IN_ISDIR' in type_names
				aux_destiny = destiny
				destiny = hiddenD+path.split(usuario)[1]+"/DELETED_"+filename
				os.system("mv {} {}".format(aux_destiny, destiny))
				conn.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" {} '{}'\tELIMINADO en la ruta {}\n".format(options[IN_ISDIR],filename, source))
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
					conn.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" {} '{}'\tMOVIDO de la ruta {} a la ruta {}\n".format(options[IN_ISDIR], fichero, aux_source, source))
					move = 0
				else:
					move_to = 1

			elif 'IN_MODIFY' in type_names:
				modify = 1
		

#############################################################
# DEMONIZACION
#with daemon.DaemonContext(stdin=sys.stdin, stdout=sys.stdout):
agent()
