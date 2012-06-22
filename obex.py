import lightblue
import uuid

print "Finished imports"

host = "1C:AB:A7:B9:76:90"
channel = 2
MAS_UUID = uuid.UUID('{bb582b40-420c-11db-b0de-0800200c9a66}').bytes
MNS_UUID = uuid.UUID('{bb582b41-420c-11db-b0de-0800200c9a66}').bytes
FTP_UUID = uuid.UUID('{F9EC7BC4-953C-11D2-984E-525400DC9E09}').bytes

client = lightblue.obex.OBEXClient(host, channel)
client.connect({'target':MAS_UUID})
