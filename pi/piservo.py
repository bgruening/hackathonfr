#!/usr/bin/env python
import os, time, sys
import optparse, ConfigParser
import paramiko

class pyservo:
    def __init__(self, servo_channel, servo_range, pi_user, pi_ip, pi_key_file, pi_image_folder = "/root/data"):
        self.servo_cmd = "echo %s=" % servo_channel + "%s%% > /dev/servoblaster"
        self.image_folder = pi_image_folder
        # Dyanmic range of our servos
        range_min, range_max = int(servo_range[0]), int(servo_range[1])
        self.dyn_range = range_max - range_min
        self.range_min = range_min
        self.range_max = range_max
        self.channel = servo_channel
        assert (self.dyn_range >= 0),"Maximum servo range must be over minimum!"
        
        # ssh stuff
        paramiko.util.log_to_file("ssh.log")
        private_key = paramiko.RSAKey.from_private_key_file(pi_key_file)
        self.ssh_shell = paramiko.SSHClient()
        self.ssh_shell.load_system_host_keys()
        self.ssh_shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_shell.connect(pi_ip,
                username = pi_user,
                password='', pkey=private_key)
                
    def move(self, percent):
        if (percent < 0): percent = percent * -1
        if ( percent  / 100 ) % 2 == 0:
            ranged_percent = (self.dyn_range / 100.) * (percent % 100)  + self.range_min
        else: 
            ranged_percent = self.range_max - ((self.dyn_range / 100.) * ( 100 - (percent % 100)))
        print self.servo_cmd%ranged_percent
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh_shell.exec_command(self.servo_cmd%ranged_percent)
        fp = open("/tmp/pyservo.%s" % self.channel, 'w')
        fp.write("%i"%percent)
        fp.close()
        
    def move_left(self, percent):
        self.move_relative(percent)
        
    def move_right(self, percent):
        self.move_relative(-percent)
                
    def move_relative(self, percent):
        try: 
            fp = open("/tmp/pyservo.%s" % self.channel, 'r')
            lastpos_line = fp.readline()
            fp.close()
        except:
            lastpos_line = "50"
        new_pos = int(lastpos_line) + percent if len(lastpos_line) > 0 else 50 + percent
        self.move(new_pos)         
        
    def takePicture(self, filename):
        self.ssh_shell.exec_command("/root/snap.py %s" %  (os.path.join(self.image_folder, filename), ))
        
        

def main():
    
    # Parse args
    p = optparse.OptionParser(description="PiServo Control")
    p.add_option("-c", "--config", dest="cfg", help="The servo config file", 
        default = os.path.join(os.getcwd(), "x_axis.cfg"))
    p.add_option("-a", "--angle", dest="angle", help="The Servo angle in percent of dynamic range", default = '-1')
    p.add_option("-i", "--image", dest="img", help="Image filename to be taken", default = '')
    p.add_option("-r", "--relative", dest="rel", help="Relative Movements", default = 'no')
    (opts, args) = p.parse_args()
    
    # Sanity
    try:
        cfgfile = open(opts.cfg, 'r')
        angle = int(opts.angle)
    except Exception as e:
        p.print_help()
        print e.__doc__
        return -1
        
    # Parse config
    config = ConfigParser.ConfigParser()
    config.read(opts.cfg)            

    # Do someting
    p = pyservo(config.get('servo', 'channel'), (int(config.get('servo', 'range_min')), int(config.get('servo', 'range_max'))),
        config.get('pi', 'user'), config.get('pi', 'ip'), config.get('pi', 'key'), config.get('pi', 'image_folder'))
    try:
        rel_angle = int(opts.rel)
        p.move_relative(rel_angle)
    except:
        if len(opts.img) > 0:
            p.takePicture(opts.img)
        else:
            if angle > 0: p.move(angle)
            else:
                for i in range(10):
                    p.move(i*10)
                    time.sleep(.5)

if (__name__ == "__main__"): main()
