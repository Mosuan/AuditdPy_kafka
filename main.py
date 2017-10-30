#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Email: Mosuansb@gmail.com

import os
import re
import sys
import time
import random

from lib.log import Log
from lib.config import *
from lib.daemon import Daemon
from lib.RedisAdd import Redis
from lib.KafkaAdd import Kafkas

class Auditd(object):

	def __init__(self):
		self._command_reg = "=[\"](.*?)[\"]"
		self._command_int_reg = "=[\"]?(.*?)"
		self._log_split_reg = "time->((.*[\\n]){8})"
		# command white list regular
		self.command_white = [
			"^(sudo ausearch) -",
			"^grep [a-zA-Z1-9]{1,20}",
			"^ifconfig -a",
			"^sh -c\s+$",
		]
		if len(sys.argv) >= 2:
			self.time_list_log = "/tmp/auditd_time_list.log"
		else:
			self.time_list_log = "./log/auditd_time_list.log"
		self.ip = str(self._ip()).replace("\n"," ")

	def _time(self, msg):
		"""
		time.time()
		"""
		return msg.split("(")[1].split(")")[0].split(".")[0]

	def _command(self, msg):
		command = ""
		for num,item in enumerate(msg.split(" ")):
			if num > 2:
				# item is int?
				if len(item.split('"')) > 1:
					command += re.findall(self._command_reg, item)[0]+" "
				else:
					command += re.findall(self._command_int_reg, item)[0]+" "
		return str(command)

	def _ip(self):
		return os.popen("ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6 | awk '{print $2}' | tr -d 'addr:'").read()

	def _file(self, filename, msg='', type='read'):
		'''
		filename read/write/add
		'''
		try:
			if type == "read":
				if not os.path.exists(filename):
					open(filename, "w+").close()
				file_obj = open(filename, "r")
				content = file_obj.read()
			elif type == "write":
				file_obj = open(filename, "w")
				content = file_obj.write(msg)

			file_obj.close()
			return content

		except Exception,e:
			Log().debug("main.py _file error: %s" % (str(e)))
			

	def _user(self, uid):
		try:
			result = os.popen("getent passwd {}".format(uid)).read()
			return result.split(":")[0]
		except Exception,e:
			pass

	def _data(self, cmd):
		"""
		auditd log
		"""
		times = (self._file(self.time_list_log).replace("\n","")).split(",")
		_time_list = []
		result = ""
		content = "[auditdPy]: \n"
		# except error 
		try:
			result = os.popen(cmd).read()

			log_list = re.findall(self._log_split_reg, result)

			for item in log_list:
				if not item[0]: continue
				# userid
				uid = re.findall(" uid=(.*?) ", item[0])
				user = "None"
				if len(uid) > 0:
					user = self._user(uid[0])
				# command
				execve = re.findall("type=EXECVE(.*?)\\n", item[0])
				if len(execve) > 0:
					execve = execve[0]
					_time = int(self._time(execve))
					# not time
					if not str(_time) in times:
						_command_str = self._command(execve)
						# False or True
						_is = False
						# command is white?
						for _while in self.command_white:
							if len(re.findall(_while, _command_str)) > 0:
								_is = True
						if not  _is:
							_time_list.append(_time)
							_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_time))
							content += "user:{} ip:{} time:{}  command:{} \n".format(user, self.ip, _date, _command_str)
							# add msg
							msg_json = {"level":"info", "app":"linux_auditd", "command": _command_str, "time": _date, "user": user, "ip": self.ip}

							if log_status == "redis":
								Redis().push_msg(msg_json)
							elif log_status == "kafka":
								Kafkas().push_msg(msg_json)

			# filter rule
			times.extend(list(set(_time_list)))
			times_str =  ",".join(str(v) for v in times)
			# end position
			self._file(self.time_list_log, times_str, "write")

			# log
			if len(_time_list) > 0:
				print(content)
			else:
				print("[not log]")
		except Exception,e:
			Log().debug("main.py _data error: %s" % (str(e)))

	def main(self):
		cmd = "sudo ausearch -ts today -k security_audit"
		self._data(cmd)
		#time.sleep(10)

	def run(self):
		cmd = "sudo ausearch -ts today -k security_audit"
		while True:
			self._data(cmd)
			time.sleep(10)


class Auditd_daemon(Daemon):
	def run(self):
		while True:
			Auditd().main()
			time.sleep(10)

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		daemon = Auditd_daemon("/tmp/auditd_daemon.pid")
		if "start" == sys.argv[1]:
			daemon.start()
		elif "stop" == sys.argv[1]:
			daemon.stop()
		else:
			print("Unknown command")
			sys.exit(2)
		sys.exit(0)
	else:
		Auditd().run()
