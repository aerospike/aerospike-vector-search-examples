from typing import Any

from . import types
from . import types_pb2


def toVectorDbValue(value: Any) -> types_pb2.Value:
    if isinstance(value, str):
        return types_pb2.Value(stringValue=value)
    elif isinstance(value, int):
        return types_pb2.Value(longValue=value)
    elif isinstance(value, (bytes, bytearray)):
        return types_pb2.Value(bytesValue=value)
    elif isinstance(value, list) and value:
        # TODO: Convert every element correctly to destination type.
        if isinstance(value[0], float):
            return types_pb2.Value(
                vectorValue=types_pb2.Vector(
                    floatArray={"value": [float(x) for x in value]}))
        if isinstance(value[0], bool):
            return types_pb2.Value(
                vectorValue=types_pb2.Vector(
                    boolArray={"value": [True if x else False for x in value]}))
    else:
        raise Exception("Invalid key type" + str(type(value)))


def fromVectorDbKey(key: types_pb2.Key) -> types.Key:
    keyValue = None
    if key.HasField("stringValue"):
        keyValue = key.stringValue
    elif key.HasField("intValue"):
        keyValue = key.intValue
    elif key.HasField("longValue"):
        keyValue = key.longValue
    elif key.HasField("bytesValue"):
        keyValue = key.bytesValue

    return types.Key(key.namespace, key.set, key.digest, keyValue)


def fromVectorDbRecord(record: types_pb2.Record) -> dict[str, Any]:
    bins = {}
    for bin in record.bins:
        bins[bin.name] = fromVectorDbValue(bin.value)

    return bins


def fromVectorDbRecordWithKey(input: types_pb2.RecordWithKey) -> (
        types.RecordWithKey):
    return types.RecordWithKey(fromVectorDbKey(input.key),
                               fromVectorDbRecord(input.record))


def fromVectorDbValue(input: types_pb2.Value) -> Any:
    if input.HasField("stringValue"):
        return input.stringValue
    elif input.HasField("intValue"):
        return input.intValue
    elif input.HasField("longValue"):
        return input.longValue
    elif input.HasField("bytesValue"):
        return input.bytesValue
    elif input.HasField("vectorValue"):
        vector = input.vectorValue
        if vector.HasField("floatArray"):
            return [v for v in vector.floatArray.value]
        if vector.HasField("boolArray"):
            return [v for v in vector.boolArray.value]

    return None
