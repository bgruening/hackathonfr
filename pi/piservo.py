#!/usr/bin/env python
import optparse, os, time, sys
import optparse, ConfigParser
import paramiko

class pyservo:
    def __init__(self, cfg_file):
        # Parse config
        config = ConfigParser.ConfigParser()
        config.read(cfg_file)
        self.servo_cmd = "echo %s=" % config.get("servo", "channel") + "%s%% > /dev/servoblaster"
        
        # 
        self.dyn_range=
        # ssh stuff
        paramiko.util.log_to_file("ssh.log")
        private_key = paramiko.RSAKey.from_private_key_file(config.get("pi", "key"))
        self.ssh_shell = paramiko.SSHClient()
        self.ssh_shell.load_system_host_keys()
        self.ssh_shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_shell.connect(config.get("pi", "ip"),
                username = config.get("pi", "user"),
                password='', pkey=private_key)
                
    def move(self, percent):
        assert (percent >= 0),"Percentage must be greater than zero!"
        assert (percent <= 100),"Percentage must be lower than hundred!"
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh_shell.exec_command(self.servo_cmd%percent)
        print ssh_stdin, ssh_stdout, ssh_stderr

def main():
    p = optparse.OptionParser(description="PiServo Control")
    p.add_option("-c", "--config", dest="cfg", help="The servo config file", default = 'x_axis.cfg')
    (opts, args) = p.parse_args()
    # Sanity
    try:
        cfgfile = open(opts.cfg, 'r')
    except Exception as e:
        p.print_help()
        print e.__doc__
        return -1

    p = pyservo(opts.cfg)
    for i in range(10):
        p.move(80)
        time.sleep(.5)
        p.move(20)
        time.sleep(.5)

if (__name__ == "__main__"): main()
