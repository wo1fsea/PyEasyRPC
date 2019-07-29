# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	Huang Quanyong
	gzhuangquanyong@corp.netease.com
Date:
	2019/7/29
Description:
	rpc_manager
----------------------------------------------------------------------------"""

from .singleton import Singleton


class RPCManager(Singleton):
	"""
	RPCManager
	"""

	@staticmethod
	def gen_service_uuid():
		raise NotImplementedError()

	@staticmethod
	def gen_rpc_uuid():
		raise NotImplementedError()

	def __init__(self):
		raise NotImplementedError()

	def register_service(self, service_name, method_name_list, enable_multi_instance=True):
		raise NotImplementedError()

	def service_heartbeat(self, service_name, service_uuid):
		raise NotImplementedError()

	def get_services(self):
		raise NotImplementedError()

	def get_service_uuids(self, service_name):
		raise NotImplementedError()

	def get_service_uuid(self, service_name):
		raise NotImplementedError()

	def get_method_list(self, service_name):
		raise NotImplementedError()

	def call_method_by_service_name(self, service_name, method_name, args, kwargs):
		raise NotImplementedError()

	def call_method_by_service_uuid(self, service_uuid, method_name, args, kwargs):
		raise NotImplementedError()

	def get_call_method_result(self, rpc_uuid):
		raise NotImplementedError()

	def block_call_method_by_service_name(self, service_name, method_name, args, kwargs):
		raise NotImplementedError()

	def block_call_method_by_service_uuid(self, service_uuid, method_name, args, kwargs):
		raise NotImplementedError()

	async def async_call_method_by_service_name(self, service_name, method_name, args, kwargs):
		raise NotImplementedError()

	async def async_call_method_by_service_uuid(self, service_name, method_name, args, kwargs):
		raise NotImplementedError()

	def get_call_method_request(self, service_uuid, method_name):
		raise NotImplementedError()

	def set_call_method_result(self, rpc_uuid, result):
		raise NotImplementedError()
