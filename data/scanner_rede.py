import socket
import subprocess
import concurrent.futures
import re
import psutil
import ipaddress

def get_local_network():
    """Descobre qual é o IP do notebook e a máscara da rede atual."""
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            # Pega apenas IPv4 e ignora o localhost (127.0.0.1)
            if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                # Só nos interessa a interface que tem um gateway (que tem internet)
                # Uma forma simples é tentar resolver a rede
                try:
                    network = ipaddress.IPv4Network(f"{addr.address}/{addr.netmask}", strict=False)
                    # Filtra redes genéricas do Windows (como as de máquinas virtuais)
                    if not str(network.network_address).startswith('169.254'):
                        return network, addr.address
                except:
                    continue
    return None, None

def ping_and_get_latency(ip):
    """Envia 1 pacote de ping e mede a latência. Retorna o IP e o tempo se responder."""
    cmd = ['ping', '-n', '1', '-w', '400', str(ip)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='latin1', creationflags=subprocess.CREATE_NO_WINDOW)
    
    if result.returncode == 0:
        # Busca o tempo de resposta (suporta Windows em PT-BR "tempo=" e EN "time=")
        match = re.search(r'(?:time|tempo)[=<]\s*(\d+\s*ms)', result.stdout, re.IGNORECASE)
        latency = match.group(1) if match else "<1ms"
        return str(ip), latency
    return str(ip), None

def get_arp_table():
    """Lê a tabela ARP do Windows para capturar os MAC Addresses."""
    cmd = ['arp', '-a']
    result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    arp_map = {}
    for line in result.stdout.split('\n'):
        # Busca o padrão: IP seguido de MAC Address
        match = re.search(r'([0-9\.]+)\s+([0-9a-f\-]{17})\s+', line, re.IGNORECASE)
        if match:
            ip = match.group(1)
            mac = match.group(2).replace('-', ':').upper()
            arp_map[ip] = mac
    return arp_map

def resolve_hostname(ip):
    """Tenta descobrir o nome do dispositivo na rede."""
    try:
        # Tenta resolver o nome, com timeout bem curto para não travar o script
        socket.setdefaulttimeout(0.5)
        host = socket.gethostbyaddr(ip)
        return host[0]
    except (socket.herror, socket.timeout, Exception):
        return "Desconhecido / Protegido"

def scan_network():
    print("Iniciando Scanner de Rede Local...")
    
    network, meu_ip = get_local_network()
    
    if not network:
        print("Erro: Não foi possível identificar a rede local. Você está conectado?")
        return

    print(f"Sua Rede Atual: {network}")
    print(f"Seu IP Local  : {meu_ip}")
    print(f"Calculando alvos... Mapeando de {network.network_address} até {network.broadcast_address}\n")
    print("Disparando Pings simultâneos... Aguarde um momento.\n")

    ips_to_scan = [str(ip) for ip in network.hosts()]
    ativos = []

    # Dispara os pings simultaneamente usando até 100 "trabalhadores"
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        resultados = executor.map(ping_and_get_latency, ips_to_scan)
        
        for ip, latencia in resultados:
            if latencia:  # Se retornou latência, o dispositivo está vivo
                ativos.append((ip, latencia))

    print("Varredura concluída. Lendo Tabela ARP e resolvendo nomes (DNS)...")
    
    # A tabela ARP só é atualizada no Windows DEPOIS que pingamos os IPs
    arp_table = get_arp_table()
    
    # Montagem e exibição da tabela final
    print("\n" + "=" * 90)
    print(f"{'ENDEREÇO IP':<16} | {'MAC ADDRESS':<19} | {'LATÊNCIA':<10} | {'HOSTNAME (NOME DO DISPOSITIVO)'}")
    print("=" * 90)
    
    for ip, latencia in ativos:
        # Se for o seu próprio IP, o MAC pode não estar na tabela ARP, então marcamos como "Seu Notebook"
        if ip == meu_ip:
            mac = "(Seu Adaptador Local)"
            nome = socket.gethostname()
        else:
            mac = arp_table.get(ip, "Desconhecido")
            nome = resolve_hostname(ip)
            
        print(f"{ip:<16} | {mac:<19} | {latencia:<10} | {nome}")

    print("-" * 90)
    print(f"Total de dispositivos online encontrados: {len(ativos)}")

if __name__ == "__main__":
    scan_network()
    print("\n")
    input("Pressione ENTER para fechar a ferramenta...")
