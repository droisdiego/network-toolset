import socket
import subprocess
import time
import os

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def testar_dns_local(alvo):
    try:
        ip = socket.gethostbyname(alvo)
        return True, ip
    except socket.gaierror:
        return False, None

def testar_dns_publico(alvo, servidor_dns):
    try:
        cmd = ['nslookup', alvo, servidor_dns]
        resultado = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
        
        # Correção: Verifica a existência do campo "Name:"/"Nome:" que só aparece em caso de sucesso real.
        if "Name:" in resultado.stdout or "Nome:" in resultado.stdout:
            return True
        return False
    except subprocess.TimeoutExpired:
        return False

def testar_porta_tcp(alvo, porta):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.5)
            s.connect((alvo, porta))
        return True
    except:
        return False

def executar_tracert_rapido(alvo):
    cmd = ['tracert', '-h', '12', '-w', '500', alvo]
    try:
        processo = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            encoding='latin1',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        for linha in processo.stdout:
            if linha.strip():
                print(f"   {linha.strip()}")
    except Exception as e:
        print(f"   Erro ao executar a rota: {e}")

def main():
    limpar_tela()
    print("=" * 70)
    print(" 🛠️  CANIVETE SUÍÇO - DIAGNÓSTICO ATIVO DE CONEXÃO ".center(70))
    print("=" * 70)
    
    alvo_bruto = input("Digite o Domínio ou IP alvo (ex: google.com, 104.16.12.3): ").strip()
    
    if not alvo_bruto:
        print("Nenhum alvo digitado. Encerrando...")
        return
    
    # Tratamento de erro do usuário: Troca vírgula por ponto automaticamente
    alvo = alvo_bruto.replace(',', '.')
    if alvo != alvo_bruto:
        print(f"\n[!] Vírgula detectada. Corrigindo alvo para: {alvo}")
        
    print("\nIniciando bateria de testes. Isso pode levar cerca de 30 segundos...\n")
    
    sucesso_local = False
    sucesso_cloudflare = False
    sucesso_google = False
    portas_abertas = 0
    ip_alvo = alvo
    
    # 1. RESOLUÇÃO DE DNS LOCAL
    print("[1/4] Testando DNS Local (Sua Operadora / Roteador)... ", end="", flush=True)
    sucesso_local, ip_resolvido = testar_dns_local(alvo)
    if sucesso_local:
        ip_alvo = ip_resolvido
        print(f"OK! (Resolvido para {ip_alvo})")
    else:
        print("FALHOU!")

    # 2. RESOLUÇÃO DE DNS PÚBLICO
    print("[2/4] Testando DNS Públicos (Bypass de Operadora)...")
    
    print("      -> Cloudflare (1.1.1.1)... ", end="", flush=True)
    sucesso_cloudflare = testar_dns_publico(alvo, '1.1.1.1')
    if sucesso_cloudflare: 
        print("OK!") 
    else: 
        print("FALHOU!")
    
    print("      -> Google (8.8.8.8)....... ", end="", flush=True)
    sucesso_google = testar_dns_publico(alvo, '8.8.8.8')
    if sucesso_google: 
        print("OK!") 
    else: 
        print("FALHOU!")

    # 3. TESTE DE PORTAS (Disponibilidade do Serviço)
    print("\n[3/4] Testando Portas Comuns TCP (Disponibilidade do Servidor)...")
    portas = {
        80: "HTTP (Navegação Web)",
        443: "HTTPS (Web Seguro)",
        53: "DNS (Resolução de Nomes)"
    }
    
    for porta, descricao in portas.items():
        print(f"      -> Porta {porta:<4} ({descricao:<28})... ", end="", flush=True)
        if testar_porta_tcp(ip_alvo, porta):
            print("[ ABERTA ]")
            portas_abertas += 1
        else:
            print("[ FECHADA/BLOQUEADA ]")

    porta_extra = input("\nDeseja testar uma porta customizada? (Digite número ou ENTER p/ pular): ").strip()
    if porta_extra.isdigit():
        porta_extra = int(porta_extra)
        print(f"      -> Porta {porta_extra:<4} (Teste Customizado)........ ", end="", flush=True)
        if testar_porta_tcp(ip_alvo, porta_extra): 
            print("[ ABERTA ]")
            portas_abertas += 1
        else: 
            print("[ FECHADA/BLOQUEADA ]")

    # 4. MAPEAMENTO DE ROTA (TRACEROUTE)
    print("\n[4/4] Mapeando Rota (Traceroute - Máx 12 saltos)...")
    executar_tracert_rapido(ip_alvo)
    
    # --- LAUDO DE DIAGNÓSTICO FINAL ---
    print("\n" + "=" * 70)
    print(" 📋 DIAGNÓSTICO FINAL (RESUMO) ".center(70))
    print("=" * 70)
    
    if not sucesso_local and not sucesso_cloudflare and not sucesso_google:
        print("🔴 CONCLUSÃO: O destino não existe ou o endereço está incorreto.")
        print("   -> Nenhum servidor de DNS (nem o seu, nem os mundiais) conseguiu encontrar esse endereço. Verifique se há erro de digitação.")
        
    elif not sucesso_local and (sucesso_cloudflare or sucesso_google):
        print("🟠 CONCLUSÃO: Problema no DNS da sua Operadora local (Bloqueio ou Falha).")
        print("   -> A sua internet não sabe o caminho, mas os servidores globais sabem. Alterar o DNS do seu adaptador de rede para 1.1.1.1 ou 8.8.8.8 resolverá o problema.")
        
    elif sucesso_local and portas_abertas == 0:
        print("🟠 CONCLUSÃO: O servidor de destino está OFFLINE ou bloqueando acessos (Firewall).")
        print("   -> O DNS resolveu o caminho perfeitamente, mas o destino final está com as portas fechadas para você. O problema está 'na ponta de lá', não na sua rede.")
        
    elif sucesso_local and portas_abertas > 0:
        print("🟢 CONCLUSÃO: Comunicação Básica Perfeita.")
        print("   -> O DNS resolveu o endereço corretamente e as portas do servidor estão abertas respondendo à conexão.")
        print("   -> Se ainda houver problemas, verifique o log do Traceroute acima buscando saltos com 'Esgotado o tempo limite'.")
        
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTeste cancelado pelo usuário.")
    
    print("\n")
    input("Pressione ENTER para fechar a ferramenta...")
