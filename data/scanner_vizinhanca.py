import subprocess
import re

def scan_wifi_networks():
    print("Iniciando radar Wi-Fi...")
    print("Escaneando as redes ao redor (isso pode levar alguns segundos)...\n")
    
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True,
            text=True,
            encoding='latin1',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        output = result.stdout
        
        blocos_ssid = re.split(r'\nSSID \d+\s*:\s*', output)[1:] 
        
        redes_encontradas = []
        
        for bloco in blocos_ssid:
            linhas = bloco.split('\n')
            ssid = linhas[0].strip()
            if not ssid:
                ssid = "<Rede Oculta>"
            
            bssid_atual = None
            sinal_atual = 0
            canal_atual = ""
            
            for linha in linhas:
                linha_limpa = linha.strip()
                
                if linha_limpa.startswith("BSSID"):
                    if bssid_atual:
                        dbm = (sinal_atual / 2) - 100 if sinal_atual > 0 else -100
                        redes_encontradas.append((ssid, bssid_atual, canal_atual, sinal_atual, int(dbm)))
                    
                    bssid_atual = linha_limpa.split(":", 1)[1].strip()
                    sinal_atual = 0
                    canal_atual = ""
                    
                elif re.search(r'(Signal|Sinal)\s*:\s*(\d+)%', linha_limpa, re.IGNORECASE):
                    sinal_atual = int(re.search(r'(\d+)%', linha_limpa).group(1))
                    
                elif re.search(r'(Channel|Canal)\s*:\s*(\d+)', linha_limpa, re.IGNORECASE):
                    canal_atual = re.search(r'(\d+)', linha_limpa).group(1)
            
            if bssid_atual:
                dbm = (sinal_atual / 2) - 100 if sinal_atual > 0 else -100
                redes_encontradas.append((ssid, bssid_atual, canal_atual, sinal_atual, int(dbm)))

        redes_encontradas.sort(key=lambda x: x[4], reverse=True)
        
        # --- EXIBIÇÃO DA TABELA ATUALIZADA ---
        print(f"{'SSID (Nome da Rede)':<26} | {'BSSID (MAC do Roteador)':<17} | {'Banda':<7} | {'Canal':<5} | {'Sinal (%)':<9} | {'Sinal (dBm)'}")
        print("-" * 93)
        
        uso_24g = {}
        uso_5g = {}
        
        for rede in redes_encontradas:
            ssid, bssid, canal_str, pct, dbm = rede
            ssid_str = ssid[:25] if len(ssid) > 25 else ssid
            
            # Identifica se é 2.4 GHz ou 5 GHz baseado no número do canal
            banda = "---"
            if canal_str.isdigit():
                canal_int = int(canal_str)
                banda = "2.4 GHz" if canal_int <= 14 else "5 GHz"
            
            print(f"{ssid_str:<26} | {bssid:<17} | {banda:<7} | {canal_str:<5} | {pct:>3}%      | {dbm:>4} dBm")
            
            # --- COLETA DE DADOS PARA ANÁLISE DE ESPECTRO ---
            if canal_str.isdigit():
                canal = int(canal_str)
                peso_interferencia = 100 + dbm if dbm > -100 else 0
                
                if canal <= 14:
                    uso_24g[canal] = uso_24g.get(canal, 0) + peso_interferencia
                else:
                    uso_5g[canal] = uso_5g.get(canal, 0) + peso_interferencia
            
        print(f"\nTotal de pontos de acesso detectados: {len(redes_encontradas)}")
        
        # --- ALGORITMO DE RECOMENDAÇÃO DE CANAL ---
        print("\n" + "=" * 93)
        print("📊 ANÁLISE DE ESPECTRO E RECOMENDAÇÃO".center(93))
        print("=" * 93)
        
        if redes_encontradas:
            score_1 = sum(uso_24g.get(c, 0) for c in [1, 2, 3])
            score_6 = sum(uso_24g.get(c, 0) for c in [4, 5, 6, 7, 8])
            score_11 = sum(uso_24g.get(c, 0) for c in [9, 10, 11, 12, 13, 14])
            
            melhor_24 = min([(1, score_1), (6, score_6), (11, score_11)], key=lambda x: x[1])
            
            canais_comuns_5g = [36, 40, 44, 48, 149, 153, 157, 161]
            scores_5g = {c: uso_5g.get(c, 0) for c in canais_comuns_5g}
            melhor_5 = min(scores_5g.items(), key=lambda x: x[1])
            
            print(f"📡 REDE 2.4 GHz:")
            print(f"   - Pior canal atual (mais congestionado): {max([(1, score_1), (6, score_6), (11, score_11)], key=lambda x: x[1])[0]}")
            print(f"   - CANAL RECOMENDADO: {melhor_24[0]} (Menor índice de interferência cruzada)")
            
            print(f"\n🚀 REDE 5.0 GHz:")
            print(f"   - CANAL RECOMENDADO: {melhor_5[0]} (Livre ou com menor ruído na vizinhança)")
            print("-" * 93)
            print("Dica: Altere os canais nas configurações do seu roteador se notar lentidão.")
        else:
            print("Nenhuma rede encontrada para análise.")
            
    except Exception as e:
        print(f"Ocorreu um erro ao escanear as redes: {e}")

if __name__ == "__main__":
    scan_wifi_networks()
    print("\n")
    input("Pressione ENTER para fechar a ferramenta...")
