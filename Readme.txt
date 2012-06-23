The obex_map_client.py program is a modification of lightblue's
obex_ftp_client.py program which allows interactively communicating
with a MAP device.  I have fixed several bugs within the lightblue
OS X source code, so you will have to build that as well.

1. Install the lightblue python module as well as the Mac OS
   X-specific LightAquaBlue framework:

     sudo python setup.py install

   in the lightblue-0.4/ directory.


2. Run the obex_map_client.py program:

     python obex_map_client.py


3. You will be prompted to select a bluetooth device and service.


4. Note the bluetooth address and channel of the device which may be
   specified as command line parameters to circumvent the device
   selection dialog.


5. Type 'help' for a list of commands.  You will have to

     cd telecom
     cd msg
     cd inbox

   to get the inbox, where new messages arrive.

   Note: 'ls' displays folders while 'lsmsg' displays messages.
