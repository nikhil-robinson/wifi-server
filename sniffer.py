import pyshark
capture = pyshark.LiveCapture(interface='eth0')
capture.sniff(timeout=50)
capture

capture[3]


for packet in capture.sniff_continuously(packet_count=5):
    print('Just arrived:', packet)