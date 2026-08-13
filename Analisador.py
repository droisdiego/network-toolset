import os
import sys
import subprocess
import time

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_menu():
    limpar_tela()
    print("   ╔══════════════════════════════════════════════════════╗")
    print("   ║             SUPER MEGA BLASTER TOOLSET               ║")
    print("   ╠══════════════════════════════════════════════════════╣")
    print("   ║                                                      ║")
    print("   ║  [1] Iniciar Monitoramento Wi-Fi (Segundo Plano)     ║")
    print("   ║  [2] Abrir Gráficos do Monitoramento                 ║")
    print("   ║  [3] Radar de Redes Vizinhas (Site Survey)           ║")
    print("   ║  [4] Scanner de Rede Local (Força Bruta)             ║")
    print("   ║  [5] Espião de Processos e Conexões                  ║")
    print("   ║  [6] Auditoria de Arquivo Hosts (Bloqueios)          ║")
    print("   ║  [7] Canivete Suíço (Diagnóstico de Rota/DNS)        ║")
    print("   ║                                                      ║")
    print("   ║  [0] Sair                                            ║")
    print("   ╚══════════════════════════════════════════════════════╝")

def executar_em_nova_janela(nome_arquivo):
    caminho = os.path.join("data", nome_arquivo)
    
    if not os.path.exists(caminho):
        print(f"\n[!] Erro: O arquivo '{caminho}' não foi encontrado.")
        print("Verifique se ele está dentro da pasta 'scripts'.")
        input("\nPressione ENTER para voltar ao menu...")
        return
        
    print(f"\nAbrindo a ferramenta em uma nova janela...")
    try:
        # O segredo: CREATE_NEW_CONSOLE faz o script rodar em uma janela separada!
        subprocess.Popen([sys.executable, caminho], creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(1.5) # Dá um tempinho para a janela abrir antes de recarregar o menu
    except Exception as e:
        print(f"\n[!] Erro ao abrir a ferramenta: {e}")
        input("\nPressione ENTER para voltar ao menu...")

def main():
    while True:
        exibir_menu()
        opcao = input("\nDigite a opção desejada: ").strip()

        if opcao == '1':
            executar_em_nova_janela("monitor_wifi.py")
        elif opcao == '2':
            executar_em_nova_janela("gerar_grafico.py")
        elif opcao == '3':
            executar_em_nova_janela("scanner_vizinhanca.py")
        elif opcao == '4':
            executar_em_nova_janela("scanner_rede.py")
        elif opcao == '5':
            executar_em_nova_janela("espiao_processos.py")
        elif opcao == '6':
            executar_em_nova_janela("auditor_hosts.py")
        elif opcao == '7':
            executar_em_nova_janela("testador_geral.py")
        elif opcao == '0':
            limpar_tela()
            print("Encerrando a Toolset... Até a próxima!")
            break
        else:
            print("\n[!] Opção inválida. Tente novamente.")
            time.sleep(1)

if __name__ == "__main__":
    main()
