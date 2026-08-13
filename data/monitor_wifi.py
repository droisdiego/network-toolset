import sys
import subprocess

# --- INSTALADOR AUTOMÁTICO DE DEPENDÊNCIAS ---
def instalar_dependencias():
    pacotes = ['psutil', 'pandas', 'matplotlib']
    for pacote in pacotes:
        try:
            __import__(pacote)
        except ImportError:
            print(f">>> Biblioteca '{pacote}' não encontrada.")
            print(f">>> Baixando e instalando automaticamente (isso acontece só na primeira vez). Aguarde...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
            print(f">>> '{pacote}' instalado com sucesso!\n")

instalar_dependencias()
# ---------------------------------------------

import psutil
import time
import re
import csv
from datetime import datetime

def get_wifi_info():
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'interfaces'], 
            capture_output=True, 
            text=True, 
            encoding='latin1',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        output = result.stdout
        
        estado_match = re.search(r'(State|Estado)\s*:\s*([^\n\r]+)', output, re.IGNORECASE)
        
        if not estado_match:
            # Retorna zeros para os novos campos caso a placa esteja desligada
            return -100, "Placa Desligada", 0, 0.0, 0.0
            
        estado = estado_match.group(2).strip().lower()
        if estado not in ['connected', 'conectado']:
            return -100, "Sem Sinal", 0, 0.0, 0.0
        
        # Expressões regulares atualizadas para pegar as novas métricas
        sinal_match = re.search(r'(Signal|Sinal)\s*:\s*(\d+)%', output, re.IGNORECASE)
        radio_match = re.search(r'(Radio type|Tipo de r.dio)\s*:\s*([^\n\r]+)', output, re.IGNORECASE)
        canal_match = re.search(r'(Channel|Canal)\s*:\s*(\d+)', output, re.IGNORECASE)
        rx_match = re.search(r'(Receive rate|Taxa de recep..o).*?:\s*([\d\.]+)', output, re.IGNORECASE)
        tx_match = re.search(r'(Transmit rate|Taxa de transmiss..).*?:\s*([\d\.]+)', output, re.IGNORECASE)
        
        # Tratamento dos dados capturados
        sinal_pct = int(sinal_match.group(2)) if sinal_match else 0
        tipo_radio = radio_match.group(2).strip() if radio_match else "Desconhecido"
        canal = int(canal_match.group(2)) if canal_match else 0
        rx_rate = float(rx_match.group(2)) if rx_match else 0.0
        tx_rate = float(tx_match.group(2)) if tx_match else 0.0
        
        # Converte a % do Windows para dBm
        dbm = (sinal_pct / 2) - 100 if sinal_pct > 0 else -100
        
        return int(dbm), tipo_radio, canal, rx_rate, tx_rate
        
    except Exception:
        return -100, "Erro de Leitura", 0, 0.0, 0.0

def main():
    print("Iniciando monitoramento avançado de rede Wi-Fi...")
    print("Pressione Ctrl+C a qualquer momento para encerrar.\n")
    
    with open('log_rede_wifi.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Cabeçalho atualizado com os novos dados
        writer.writerow(['Data/Hora', 'Download (KB/s)', 'Upload (KB/s)', 'Sinal (dBm)', 'Padrão Wi-Fi', 'Canal', 'RX (Mbps)', 'TX (Mbps)'])
        
        io_anterior = psutil.net_io_counters()
        
        try:
            while True:
                time.sleep(1)
                
                io_atual = psutil.net_io_counters()
                download_kb = (io_atual.bytes_recv - io_anterior.bytes_recv) / 1024
                upload_kb = (io_atual.bytes_sent - io_anterior.bytes_sent) / 1024
                io_anterior = io_atual
                
                dbm, tipo, canal, rx, tx = get_wifi_info()
                agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Salvando os dados no CSV
                writer.writerow([agora, f"{download_kb:.2f}", f"{upload_kb:.2f}", dbm, tipo, canal, rx, tx])
                csvfile.flush() 
                
                # Imprimindo no terminal de forma organizada
                print(f"[{agora}] DL: {download_kb:8.2f} KB/s | UP: {upload_kb:8.2f} KB/s | Sinal: {dbm:4} dBm | "
                      f"Padrão: {tipo:7} | Canal: {canal:3} | TX: {tx:6.1f} Mbps | RX: {rx:6.1f} Mbps")
        
        except KeyboardInterrupt:
            print("\nMonitoramento encerrado. Salvo em 'log_rede_wifi.csv'.")

if __name__ == "__main__":
    main()
