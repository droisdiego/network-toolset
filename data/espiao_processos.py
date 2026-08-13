import psutil
import os
import time
import socket

def limpar_tela():
    """Limpa o terminal para criar o efeito de atualização em tempo real."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_process_name(pid, cache):
    """Tenta descobrir o nome do processo pelo PID, usando cache para ficar rápido."""
    if pid in cache:
        return cache[pid]
    try:
        nome = psutil.Process(pid).name()
        cache[pid] = nome
        return nome
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        cache[pid] = "Acesso Negado (Admin)"
        return cache[pid]

def espionar_conexoes(filtro_alvo=""):
    cache_processos = {}
    cache_dns = {}
    
    print(f"Iniciando o Espião de Processos... (Filtro: {'Nenhum (Mostrando Todos)' if not filtro_alvo else filtro_alvo})")
    time.sleep(1)

    try:
        while True:
            # Pega todas as conexões de rede atuais (IPv4 e IPv6)
            conexoes = psutil.net_connections(kind='inet')
            
            linhas_exibicao = []
            
            for conn in conexoes:
                # Nos interessa apenas conexões que estão efetivamente "conversando" com o exterior
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    pid = conn.pid
                    if not pid:
                        continue
                        
                    nome_processo = get_process_name(pid, cache_processos)
                    
                    # Se o usuário digitou um filtro (ex: "chrome"), pula os outros processos
                    if filtro_alvo and filtro_alvo.lower() not in nome_processo.lower():
                        continue
                        
                    ip_local, porta_local = conn.laddr
                    ip_remoto, porta_remoto = conn.raddr
                    
                    # Ignora conexões locais (loopback) para focar na internet
                    if ip_remoto == '127.0.0.1' or ip_remoto.startswith('192.168.'):
                        continue

                    linhas_exibicao.append(
                        f"{nome_processo[:20]:<20} | {pid:<8} | {ip_remoto:<15} | {porta_remoto:<6} | {conn.type.name}"
                    )
            
            # Atualiza a tela
            limpar_tela()
            print("=" * 70)
            print(" 🕵️  ESPIÃO DE REDE EM TEMPO REAL ".center(70))
            print("=" * 70)
            print(f"Filtro Ativo: {filtro_alvo if filtro_alvo else 'Nenhum (Todos os processos externos)'}")
            print(f"Pressione Ctrl+C para sair.\n")
            
            print(f"{'PROCESSO':<20} | {'PID':<8} | {'IP DESTINO':<15} | {'PORTA':<6} | {'TIPO'}")
            print("-" * 70)
            
            if linhas_exibicao:
                # Ordena pelo nome do processo para ficar organizado
                for linha in sorted(linhas_exibicao):
                    print(linha)
            else:
                print("Nenhuma conexão estabelecida correspondente encontrada no momento.")
            
            print("-" * 70)
            
            # Atualiza a cada 2 segundos
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nEspionagem encerrada.")

if __name__ == "__main__":
    print("Bem-vindo ao Espião de Processos!")
    print("Digite o nome de um aplicativo para espionar (ex: chrome, discord, valorant)")
    print("Ou apenas pressione ENTER para ver todas as conexões externas.")
    alvo = input("\nAlvo: ").strip()
    espionar_conexoes(alvo)
