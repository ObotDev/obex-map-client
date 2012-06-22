# 05/22/12: adpated from lightblue's obex_ftp_client.py by Ojas Parekh.

import sys
import os
import uuid
import StringIO
import lightblue


# Target UUID for the Message Access Profile
MAS_TARGET_UUID = uuid.UUID('{bb582b40-420c-11db-b0de-0800200c9a66}').bytes

# Message Access Profile application parameters
FILTER_READ_STATUS_TAG    = '\x06\x01'
FILTER_READ_STATUS_BOTH   = FILTER_READ_STATUS_TAG + '\x00'
FILTER_READ_STATUS_UNREAD = FILTER_READ_STATUS_TAG + '\x01'
FILTER_READ_STATUS_READ   = FILTER_READ_STATUS_TAG + '\x02'

ATTACHMENT_TAG = '\x0A\x01'
ATTACHMENT_OFF = ATTACHMENT_TAG + '\x00'
ATTACHMENT_ON  = ATTACHMENT_TAG + '\x01'

CHARSET_TAG    = '\x14\x01'
CHARSET_NATIVE = CHARSET_TAG + '\x00'
CHARSET_UTF8   = CHARSET_TAG + '\x01'

STATUS_INDICATOR_TAG     = '\x17\x01'
STATUS_INDICATOR_READ    = STATUS_INDICATOR_TAG + '\x00';
STATUS_INDICATOR_DELETED = STATUS_INDICATOR_TAG + '\x01';

STATUS_VALUE_TAG = '\x18\x01'
STATUS_VALUE_NO  = STATUS_VALUE_TAG + '\x00';
STATUS_VALUE_YES = STATUS_VALUE_TAG + '\x01';

# A note about Connection ID headers:
# Notice that the MAPClient does not send the Connection ID in any of the 
# request headers, even though this is required by the Message Access Profile 
# specs. This is because the OBEXClient class automatically sends the Connection 
# ID with each request if it received one from the server in the initial Connect
# response headers, so you do not have to add it yourself.


class MAPClient(object):

    def __init__(self, address, port):
        self.client = lightblue.obex.OBEXClient(address, port)

    def connect(self):
        response = self.client.connect({'target': MAS_TARGET_UUID})
        if response.code != lightblue.obex.OK:
            raise Exception('OBEX server refused Connect request (server \
                response was "%s")' % response.reason)

    def disconnect(self):
        print "Disconnecting..."
        response = self.client.disconnect()
        print 'Server response:', response.reason

    def ls(self):
        dirlist = StringIO.StringIO()
        response = self.client.get({'type': 'x-obex/folder-listing\x00'}, dirlist)
        print 'Server response:', response.reason
        if response.code == lightblue.obex.OK:
            files = self._parsefolderlisting(dirlist.getvalue())
            if len(files) == 0:
                print 'No files found'
            else:
                print 'Found files:'
                for f in files:
                    print '\t', f

    def cd(self, dirname):
        if dirname == os.sep:
            # change to root dir
            response = self.client.setpath({'name': ''})
        elif dirname == '..':
            # change to parent directory
            response = self.client.setpath({}, cdtoparent=True)
        else:
            # change to subdirectory
            response = self.client.setpath({'name': dirname})
        print 'Server response:', response.reason

    def put(self, filename):
        print 'Sending %s...' % filename
        try:
            f = file(filename, 'rb')
        except Exception, e:
            print "Cannot open file %s" % filename
            return
        response = self.client.put({'name': os.path.basename(filename)}, f)
        f.close()
        print 'Server response:', response.reason

    def get(self, filename):
        if os.path.isfile(filename):
            if raw_input("Overwrite local file %s?" % filename).lower() != "y":
                return
        print 'Retrieving %s...' % filename
        f = file(filename, 'wb')
        response = self.client.get({'name': filename}, f)
        f.close()
        print 'Server response:', response.reason

    def rm(self, filename):
        response = self.client.delete({'name': filename})
        print 'Server response:', response.reason

    def mkdir(self, dirname):
        response = self.client.setpath({'name': dirname}, createdirs=True)
        print 'Server response:', response.reason

    def rmdir(self, dirname):
        response = self.client.delete({'name': dirname})
        print 'Server response:', response.reason
        if response.code == lightblue.obex.PRECONDITION_FAILED:
            print 'Directory contents must be deleted first'

    # OP: MAP-specific commands
    def lsmsg(self, type='unread'):
        # additional application parameters go below
        parameters = ''
        if type == 'unread':
            parameters += FILTER_READ_STATUS_UNREAD
        elif type == 'read':
            parameters += FILTER_READ_STATUS_READ
        else:
            parameters += FILTER_READ_STATUS_BOTH

        msglist = StringIO.StringIO()
        response = self.client.get({'type': 'x-bt/MAP-msg-listing\x00', 
                                    'name': '',
                                    'application-parameters': parameters},
                                   msglist)
        print 'Server response:', response.reason
        if response.code == lightblue.obex.OK:
            print 'Messages XML:'
            print msglist.getvalue()

    def getmsg(self, handle):
        if handle == '':
            print 'Must specify a valid message handle'
            return

        msg = StringIO.StringIO()
        response = self.client.get({'type': 'x-bt/message\x00',
                                    'name': handle,
                                    'application-parameters': ATTACHMENT_OFF + CHARSET_UTF8},
                                   msg)
        print 'Server response:', response.reason
        if response.code == lightblue.obex.OK:
            print 'Message', handle + ':'
            print msg.getvalue()

    def setmsgread(self, handle):
        if handle == '':
            print 'Must specify a valid message handle'
            return
        
        fillerbody = StringIO.StringIO('0')
        response = self.client.put({'type': 'x-bt/messageStatus\x00',
                                    'name': handle,
                                    'application-parameters': STATUS_INDICATOR_READ + STATUS_VALUE_YES}, 
                                   fillerbody)
        fillerbody.close()
        print 'Server response:', response.reason

    def _parsefolderlisting(self, xmldata):
        """
        Returns a list of basic details for the files and folders contained in
        the given XML folder-listing data. (The complete folder-listing XML DTD
        is documented in the IrOBEX specification.)
        """
        if len(xmldata) == 0:
            print "Error parsing folder-listing XML: no xml data"
            return []
        entries = []
        import xml.dom.minidom
        import xml.parsers.expat
        try:
            dom = xml.dom.minidom.parseString(xmldata)
        except xml.parsers.expat.ExpatError, e:
            print "Error parsing folder-listing XML (%s): '%s'" % \
                (str(e), xmldata)
            return []
        parent = dom.getElementsByTagName('parent-folder')
        if len(parent) != 0:
            entries.append('..')
        folders = dom.getElementsByTagName('folder')
        for f in folders:
            entries.append('%s/\t%s' % (f.getAttribute('name'),
                                        f.getAttribute('size')))
        files = dom.getElementsByTagName('file')
        for f in files:
            entries.append('%s\t%s' % (f.getAttribute('name'),
                                       f.getAttribute('size')))
        return entries


def processcommands(client):
    while True:
        input = raw_input('\nEnter command: ')
        cmd = input.split(" ")[0].lower()
        if not cmd:
            continue
        if cmd == 'exit':
            break

        try:
            method = getattr(client, cmd)
        except AttributeError:
            print 'Unknown command "%s".' % cmd
            print main.__doc__
            continue

        if cmd == 'ls':
            if " " in input.strip():
                print "(Ignoring path, can only list contents of current dir)"
            method()
        else:
            name = input[len(cmd)+1:]     # file or directory name required
            method(name)


def main():
    """
    Usage: python obex_map_client.py [address channel]

    If the address and channel are not provided, the user will be prompted to
    choose a service.

    Once the client is connected, you can enter one of these commands:
        ls
        cd <directory>  (use '..' to change to parent, or '/' to change to root)
        put <file>
        get <file>
        rm <file>
        mkdir <directory>
        rmdir <directory>
        lsmsg [unread/read/both]
        getmsg <handle>
        setmsgread <handle>
        exit
        
    Some servers accept "/" path separators within the <file> or <filename> 
    arguments. Otherwise, you will have to just send either a single directory 
    or filename, without any paths.
    """
    if len(sys.argv) > 1:
        address = sys.argv[1]
        channel = int(sys.argv[2])
    else:
        # ask user to choose a service
        # a FTP service is usually called 'FTP', 'OBEX File Transfer', etc.
        address, channel, servicename = lightblue.selectservice()
    print 'Connecting to %s on channel %d...' % (address, channel)

    mapclient = MAPClient(address, channel)
    mapclient.connect()
    print 'Connected.'

    try:
        processcommands(mapclient)
    finally:
        try:
            mapclient.disconnect()
        except Exception, e:
            print "Error while disconnecting:", e
            pass


if __name__ == "__main__":
    main()
