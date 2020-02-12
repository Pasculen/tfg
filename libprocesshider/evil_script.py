#!/usr/bin/python3


import daemon
import inotify.adapters
import os
import sys

def daemonTask():
	i = inotify.adapters.InotifyTree('/home/tfg/Escritorio')
	print(os.getpid())
	for event in i.event_gen(yield_nones=False):
		(_, type_names, path, filename) = event
		logFile.write("{}: {} [{}]\n".format(type_names, path, filename))
		logFile.flush()

logFile = open("logdaemon.txt", "a")
with daemon.DaemonContext(stdout=sys.stdout,
	files_preserve=[logFile]):
	daemonTask()