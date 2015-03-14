#!/usr/bin/env python
import os, time, sys
import optparse, ConfigParser
import paramiko

class pyservo:
    def __init__(self, cfg_file):
        # Parse config
        config = ConfigParser.ConfigParser()
        config.read(cfg_file)
        self.servo_cmd = "echo %s=" % config.get("servo", "channel") + "%s%% > /dev/servoblaster"
        self.image_folder = config.get("pi", "image_folder")
        # Dyanmic range of our servos
        range_min, range_max = int(config.get("servo", "range_min")), int(config.get("servo", "range_max"))
        self.dyn_range = range_max - range_min
        self.range_min = range_min
        assert (self.dyn_range >= 0),"Maximum servo range must be over minimum!"
        
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
        ranged_percent = (self.dyn_range / 100.) * percent + self.range_min
        print self.servo_cmd%ranged_percent
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh_shell.exec_command(self.servo_cmd%ranged_percent)
        
    def takePicture(self, filename):
        self.ssh_shell.exec_command("/root/snap.py %s" %  (os.path.join(self.image_folder, filename), ))
        
        

def main():
    p = optparse.OptionParser(description="PiServo Control")
    p.add_option("-c", "--config", dest="cfg", help="The servo config file", default = 'x_axis.cfg')
    p.add_option("-a", "--angle", dest="angle", help="The Servo angle in percent of dynamic range", default = '-1')
    p.add_option("-i", "--image", dest="img", help="Image filename to be taken", default = '')
    
    
    (opts, args) = p.parse_args()
    # Sanity
    try:
        cfgfile = open(opts.cfg, 'r')
        angle = int(opts.angle)
    except Exception as e:
        p.print_help()
        print e.__doc__
        return -1

    p = pyservo(opts.cfg)
    if len(opts.img) > 0:
        p.takePicture(opts.img)
    else:
        if angle > 0: p.move(angle)
        else:
            for i in range(10):
                p.move(i*10)
                time.sleep(.5)
                #~ p.takePicture("moved_%.2i.jpg"%i)

if (__name__ == "__main__"): main()
