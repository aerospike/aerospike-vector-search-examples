# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: types.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0btypes.proto\x1a\x1bgoogle/protobuf/empty.proto\"\xa1\x01\n\x03Key\x12\x11\n\tnamespace\x18\x01 \x01(\t\x12\x10\n\x03set\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x0e\n\x06\x64igest\x18\x03 \x01(\x0c\x12\x15\n\x0bstringValue\x18\x04 \x01(\tH\x00\x12\x14\n\nbytesValue\x18\x05 \x01(\x0cH\x00\x12\x12\n\x08intValue\x18\x06 \x01(\x05H\x00\x12\x13\n\tlongValue\x18\x07 \x01(\x03H\x00\x42\x07\n\x05valueB\x06\n\x04_set\"\x1a\n\tBoolArray\x12\r\n\x05value\x18\x01 \x03(\x08\"\x1b\n\nFloatArray\x12\r\n\x05value\x18\x01 \x03(\x02\"T\n\x06Vector\x12\x1f\n\tboolArray\x18\x01 \x01(\x0b\x32\n.BoolArrayH\x00\x12!\n\nfloatArray\x18\x02 \x01(\x0b\x32\x0b.FloatArrayH\x00\x42\x06\n\x04\x64\x61ta\"\xb3\x01\n\x05Value\x12\x15\n\x0bstringValue\x18\x01 \x01(\tH\x00\x12\x14\n\nbytesValue\x18\x02 \x01(\x0cH\x00\x12\x12\n\x08intValue\x18\x03 \x01(\x05H\x00\x12\x13\n\tlongValue\x18\x04 \x01(\x03H\x00\x12\x14\n\nfloatValue\x18\x05 \x01(\x02H\x00\x12\x15\n\x0b\x64oubleValue\x18\x06 \x01(\x01H\x00\x12\x1e\n\x0bvectorValue\x18\x07 \x01(\x0b\x32\x07.VectorH\x00\x42\x07\n\x05value\"*\n\x03\x42in\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\x05value\x18\x02 \x01(\x0b\x32\x06.Value\"D\n\x06Record\x12\x12\n\ngeneration\x18\x01 \x01(\r\x12\x12\n\nexpiration\x18\x02 \x01(\r\x12\x12\n\x04\x62ins\x18\x03 \x03(\x0b\x32\x04.Bin\"K\n\rRecordWithKey\x12\x11\n\x03key\x18\x01 \x01(\x0b\x32\x04.Key\x12\x1c\n\x06record\x18\x02 \x01(\x0b\x32\x07.RecordH\x00\x88\x01\x01\x42\t\n\x07_record\"*\n\x07IndexId\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tnamespace\x18\x02 \x01(\t\"\xe1\x01\n\x0fIndexDefinition\x12\x14\n\x02id\x18\x01 \x01(\x0b\x32\x08.IndexId\x12\x18\n\x04type\x18\x02 \x01(\x0e\x32\n.IndexType\x12\x10\n\x03set\x18\x03 \x01(\tH\x00\x88\x01\x01\x12\x0b\n\x03\x62in\x18\x04 \x01(\t\x12\x12\n\ndimensions\x18\x05 \x01(\r\x12,\n\x06params\x18\x06 \x03(\x0b\x32\x1c.IndexDefinition.ParamsEntry\x1a\x35\n\x0bParamsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x15\n\x05value\x18\x02 \x01(\x0b\x32\x06.Value:\x02\x38\x01\x42\x06\n\x04_set\"8\n\x13IndexDefinitionList\x12!\n\x07indices\x18\x01 \x03(\x0b\x32\x10.IndexDefinition*&\n\x0bIndexStatus\x12\x0c\n\x08\x43REATING\x10\x00\x12\t\n\x05READY\x10\x01*\x15\n\tIndexType\x12\x08\n\x04HNSW\x10\x00\x42=\n\x1b\x63om.aerospike.vector.clientP\x01Z\x1c\x61\x65rospike.com/vector/protos/b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\033com.aerospike.vector.clientP\001Z\034aerospike.com/vector/protos/'
  _INDEXDEFINITION_PARAMSENTRY._options = None
  _INDEXDEFINITION_PARAMSENTRY._serialized_options = b'8\001'
  _globals['_INDEXSTATUS']._serialized_start=1054
  _globals['_INDEXSTATUS']._serialized_end=1092
  _globals['_INDEXTYPE']._serialized_start=1094
  _globals['_INDEXTYPE']._serialized_end=1115
  _globals['_KEY']._serialized_start=45
  _globals['_KEY']._serialized_end=206
  _globals['_BOOLARRAY']._serialized_start=208
  _globals['_BOOLARRAY']._serialized_end=234
  _globals['_FLOATARRAY']._serialized_start=236
  _globals['_FLOATARRAY']._serialized_end=263
  _globals['_VECTOR']._serialized_start=265
  _globals['_VECTOR']._serialized_end=349
  _globals['_VALUE']._serialized_start=352
  _globals['_VALUE']._serialized_end=531
  _globals['_BIN']._serialized_start=533
  _globals['_BIN']._serialized_end=575
  _globals['_RECORD']._serialized_start=577
  _globals['_RECORD']._serialized_end=645
  _globals['_RECORDWITHKEY']._serialized_start=647
  _globals['_RECORDWITHKEY']._serialized_end=722
  _globals['_INDEXID']._serialized_start=724
  _globals['_INDEXID']._serialized_end=766
  _globals['_INDEXDEFINITION']._serialized_start=769
  _globals['_INDEXDEFINITION']._serialized_end=994
  _globals['_INDEXDEFINITION_PARAMSENTRY']._serialized_start=933
  _globals['_INDEXDEFINITION_PARAMSENTRY']._serialized_end=986
  _globals['_INDEXDEFINITIONLIST']._serialized_start=996
  _globals['_INDEXDEFINITIONLIST']._serialized_end=1052
# @@protoc_insertion_point(module_scope)