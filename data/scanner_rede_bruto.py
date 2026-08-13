import socket
import subprocess
import concurrent.futures
import re
import psutil
import ipaddress
import time

def get_local_network():
    """Descobre qual é o IP do notebook e a máscara da rede atual."""
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                try:
                    network = ipaddress.IPv4Network(f"{addr.address}/{addr.netmask}", strict=False)
                    if not str(network.network_address).startswith('169.254'):
                        return network, addr.address
                except:
                    continue
    return None, None

def force_arp_resolution(ip):
    """
    TÁTICA DE HACKER (UDP FORCING):
    Envia um pacote de dados vazio forçando o alvo a processar a requisição no nível físico.
    Isso obriga a placa de rede do alvo a revelar seu MAC Address para o Windows,
    mesmo que o firewall esteja configurado para bloquear pings.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Envia para a porta 137 (NetBIOS), que costuma forçar uma resposta de negação física
        sock.sendto(b'\x00', (ip, 137))
        sock.close()
    except:
        pass

def ping_device(ip):
    """Envia o Ping tradicional apenas para tentar capturar a latência (se o aparelho permitir)."""
    cmd = ['ping', '-n', '1', '-w', '300', ip]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='latin1', creationflags=subprocess.CREATE_NO_WINDOW)
    
    if result.returncode == 0:
        match = re.search(r'(?:time|tempo)[=<]\s*(\d+\s*ms)', result.stdout, re.IGNORECASE)
        return match.group(1) if match else "<1ms"
    return None

def get_arp_table(network):
    """Lê a tabela ARP bruta do Windows, que agora estará cheia graças ao UDP Forcing."""
    cmd = ['arp', '-a']
    result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    arp_map = {}
    for line in result.stdout.split('\n'):
        # Busca IP e MAC na tabela
        match = re.search(r'([0-9\.]+)\s+([0-9a-f\-]{17})', line, re.IGNORECASE)
        if match:
            ip = match.group(1)
            mac = match.group(2).replace('-', ':').upper()
            
            # Filtra apenas IPs que pertencem à nossa rede (ignora IPs de broadcast/multicast do Windows)
            try:
                if ipaddress.IPv4Address(ip) in network:
                    # Ignora MACs genéricos de broadcast da rede (ex: FF:FF:FF:FF:FF:FF)
                    if not mac.startswith('FF:FF:FF') and not mac.startswith('01:00:5E'):
                        arp_map[ip] = mac
            except:
                pass
    return arp_map

def resolve_hostname(ip):
    """Tenta descobrir o nome legível do dispositivo."""
    try:
        socket.setdefaulttimeout(0.3)
        host = socket.gethostbyaddr(ip)
        return host[0]
    except:
        return "Dispositivo Oculto"

def scan_network():
    print("Iniciando Scanner de Rede Local Agressivo (Bypass de Firewall)...")
    
    network, meu_ip = get_local_network()
    
    if not network:
        print("Erro: Não foi possível identificar a rede local.")
        return

    print(f"Sua Rede Atual: {network}")
    print(f"Seu IP Local  : {meu_ip}\n")
    
    ips_to_scan = [str(ip) for ip in network.hosts()]

    # PASSO 1: O "Ataque" UDP (Preenchendo a tabela ARP à força)
    print("1. Disparando pacotes UDP forçados para quebrar as defesas... ", end="", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        executor.map(force_arp_resolution, ips_to_scan)
    print("OK!")

    # PASSO 2: Ping tradicional para quem é "educado" e medir latência
    print("2. Testando latência com pacotes ICMP... ", end="", flush=True)
    ping_results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_ip = {executor.submit(ping_device, ip): ip for ip in ips_to_scan}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            ping_results[ip] = future.result()
    print("OK!")

    # Dá 1 segundinho para o Windows terminar de escrever os MACs na memória
    time.sleep(1)

    # PASSO 3: Leitura da verdade absoluta (Tabela ARP)
    print("3. Extraindo Tabela MAC/ARP do sistema...")
    arp_table = get_arp_table(network)
    
    # Adicionamos nosso próprio notebook manualmente (pois ele não aparece no próprio ARP)
    if meu_ip not in arp_table:
        arp_table[meu_ip] = "(Seu Adaptador Local)"

    # --- MONTAGEM DA TABELA FINAL ---
    print("\n" + "=" * 105)
    print(f"{'ENDEREÇO IP':<16} | {'MAC ADDRESS':<19} | {'STATUS / LATÊNCIA':<19} | {'HOSTNAME (NOME)'}")
    print("=" * 105)
    
    dispositivos_encontrados = 0
    
    # Vamos listar apenas os aparelhos que estão na tabela ARP (Prova física de que estão vivos)
    # Ordenamos os IPs de forma crescente para ficar organizado
    ips_ordenados = sorted(list(arp_table.keys()), key=lambda ip: int(ipaddress.IPv4Address(ip)))
    
    for ip in ips_ordenados:
        mac = arp_table[ip]
        latencia = ping_results.get(ip)
        nome = socket.gethostname() if ip == meu_ip else resolve_hostname(ip)
        
        # O Pulo do Gato: Se o dispositivo apareceu no ARP, mas não respondeu ao ping, é um ninja!
        if latencia is None:
            if ip == meu_ip:
                status = "<1ms (Você)"
            else:
                status = "Bloqueado (Firewall)"
        else:
            status = latencia
            
        print(f"{ip:<16} | {mac:<19} | {status:<19} | {nome}")
        dispositivos_encontrados += 1

    print("-" * 105)
    print(f"Total de dispositivos encontrados na força bruta: {dispositivos_encontrados}")

if __name__ == "__main__":
    scan_network()
    print("\n")
    input("Pressione ENTER para fechar a ferramenta...")
