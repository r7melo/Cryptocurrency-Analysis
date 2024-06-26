from scapy.all import ARP, Ether, srp

def scan_network(ip_range):
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=3, verbose=0)[0]

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    return devices

if __name__ == "__main__":
    ip_range = "192.168.0.1/24"  # Substitua pelo intervalo de IP da sua rede
    devices = scan_network(ip_range)
    print("Dispositivos conectados à rede:")
    for device in devices:
        print("IP:", device['ip'], "  MAC:", device['mac'])
