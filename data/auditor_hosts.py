import os
import re

def auditar_arquivo_hosts():
    # Caminho oficial do arquivo hosts no Windows
    caminho_hosts = r"C:\Windows\System32\drivers\etc\hosts"
    
    print("Iniciando Auditoria de Serviços Bloqueados e Redirecionamentos...")
    print(f"Alvo: {caminho_hosts}\n")
    
    if not os.path.exists(caminho_hosts):
        print("Erro: O arquivo 'hosts' não foi encontrado no seu sistema.")
        return

    bloqueios = []
    redirecionamentos = []
    
    try:
        with open(caminho_hosts, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
            
        for linha in linhas:
            # Remove espaços em branco do início e fim
            linha = linha.strip()
            
            # Ignora linhas vazias e comentários (linhas que começam com #)
            if not linha or linha.startswith('#'):
                continue
            
            # Divide a linha onde houver espaços ou tabs (ex: "127.0.0.1    site.com")
            partes = re.split(r'\s+', linha)
            
            if len(partes) >= 2:
                ip = partes[0]
                dominio = partes[1]
                
                # Se o IP alvo for o localhost (127.0.0.1) ou nulo (0.0.0.0), é um bloqueio
                # Ignoramos a regra padrão do próprio "localhost"
                if ip in ['127.0.0.1', '0.0.0.0'] and dominio.lower() != 'localhost':
                    bloqueios.append((ip, dominio))
                else:
                    redirecionamentos.append((ip, dominio))
                    
        # --- EXIBIÇÃO: BLOQUEIOS (BURACO NEGRO) ---
        print("=" * 65)
        print(" 🚫 DOMÍNIOS BLOQUEADOS (Buraco Negro: 127.0.0.1 / 0.0.0.0)".center(65))
        print("=" * 65)
        if bloqueios:
            print(f"{'DOMÍNIO ALVO (O que está bloqueado)':<40} | {'IP FALSO'}")
            print("-" * 65)
            # Ordena alfabeticamente pelo nome do domínio
            for ip, dom in sorted(bloqueios, key=lambda x: x[1]):
                print(f"{dom:<40} | {ip}")
            print("-" * 65)
            print(f"Total de domínios bloqueados localmente: {len(bloqueios)}\n")
        else:
            print("Nenhum bloqueio encontrado. Arquivo limpo.\n")

        # --- EXIBIÇÃO: REDIRECIONAMENTOS (ROTAS CUSTOMIZADAS) ---
        print("=" * 65)
        print(" 🔀 REDIRECIONAMENTOS CUSTOMIZADOS (Rotas VIP)".center(65))
        print("=" * 65)
        if redirecionamentos:
            print(f"{'DOMÍNIO ALVO':<40} | {'REDIRECIONADO PARA IP'}")
            print("-" * 65)
            for ip, dom in sorted(redirecionamentos, key=lambda x: x[1]):
                print(f"{dom:<40} | {ip}")
            print("-" * 65)
            print(f"Total de rotas customizadas: {len(redirecionamentos)}\n")
        else:
            print("Nenhum redirecionamento customizado encontrado.\n")
            
    except PermissionError:
        print("Erro: Permissão negada pelo Windows para ler o arquivo hosts.")
        print("Dica: Tente rodar este script clicando com o botão direito no .bat e escolhendo 'Executar como Administrador'.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")

if __name__ == "__main__":
    auditar_arquivo_hosts()
    print("\n")
    input("Pressione ENTER para fechar a ferramenta...")
