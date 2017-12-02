# noolite

Console app for MTRF-64.

http://www.noo.com.by/assets/files/PDF/MTRF-64.pdf

Usage:

    $ sudo pip install pyserial
    $ sudo python /home/pi/noolite/noolite-transmitter.py

Run as a service:
    
    $ sudo cp /home/pi/noolite/noolite-receiver.service /lib/systemd/system/noolite-receiver.service
    $ sudo systemctl enable noolite-receiver.service
    $ sudo systemctl status noolite-receiver.service
    $ sudo systemctl start noolite-receiver.service
    
    $ sudo cp /home/pi/noolite/noolite-transmitter.service /lib/systemd/system/noolite-transmitter.service
    $ sudo systemctl enable noolite-transmitter.service
    $ sudo systemctl start noolite-transmitter.service
    $ sudo systemctl status noolite-transmitter.service
    
    $ sudo cp /home/pi/noolite/ympd.service /lib/systemd/system/ympd.service
    $ sudo systemctl enable ympd.service
    $ sudo systemctl start ympd.service
    $ sudo systemctl status ympd.service

    $ alias start='sudo systemctl status noolite-receiver.service && sudo systemctl status noolite-transmitter.service && sudo systemctl status ympd.service'
