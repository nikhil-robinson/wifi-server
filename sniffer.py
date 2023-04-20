import sys
import scapy.all as scapy

iface = sys.argv[1]
sniff_filter = sys.argv[2]

def process_packet(packet):
    # Process the packet here
    print(packet.summary())

scapy.sniff(iface=iface, filter=sniff_filter, prn=process_packet)
