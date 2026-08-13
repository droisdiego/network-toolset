import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

def plotar_graficos():
    print("Lendo os dados do arquivo CSV...")
    
    try:
        # Lê o arquivo CSV
        df = pd.read_csv('log_rede_wifi.csv')
        
        # Converte a coluna de data/hora para o formato de tempo real
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])
        
        # Garante que as colunas sejam tratadas como números
        df['Download (KB/s)'] = pd.to_numeric(df['Download (KB/s)'])
        df['Upload (KB/s)'] = pd.to_numeric(df['Upload (KB/s)'])
        df['Sinal (dBm)'] = pd.to_numeric(df['Sinal (dBm)'])
        df['TX (Mbps)'] = pd.to_numeric(df['TX (Mbps)'])
        df['RX (Mbps)'] = pd.to_numeric(df['RX (Mbps)'])
        
        # Cria a janela agora com 3 gráficos empilhados
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        
        # --- DETECÇÃO DE DESCONEXÃO (Outages) ---
        is_disconnected = df['Sinal (dBm)'] == -100
        start_end_indices = []
        if is_disconnected.any():
            starts = df[is_disconnected & ~is_disconnected.shift(1).fillna(False)].index
            ends = df[is_disconnected & ~is_disconnected.shift(-1).fillna(False)].index
            start_end_indices = list(zip(starts, ends))

        def shade_outages(ax):
            for start, end in start_end_indices:
                ax.axvspan(df['Data/Hora'].iloc[start], 
                          df['Data/Hora'].iloc[end], 
                          color='red', alpha=0.15, zorder=0)

        # --- GRÁFICO 1: TRÁFEGO DE INTERNET (KB/s) ---
        ax1.plot(df['Data/Hora'], df['Download (KB/s)'], label='Download (Internet)', color='#007acc', linewidth=2)
        ax1.plot(df['Data/Hora'], df['Upload (KB/s)'], label='Upload (Internet)', color='#28a745', linewidth=2)
        ax1.set_title('Tráfego Real (KB/s)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Velocidade (KB/s)')
        ax1.grid(True, linestyle='--', alpha=0.6)
        shade_outages(ax1)
        ax1.legend(loc='upper left')

        # --- GRÁFICO 2: VELOCIDADE FÍSICA DA PLACA (TX / RX em Mbps) ---
        ax2.plot(df['Data/Hora'], df['TX (Mbps)'], label='TX (Transmissão Roteador)', color='#8e44ad', linewidth=2)
        ax2.plot(df['Data/Hora'], df['RX (Mbps)'], label='RX (Recepção Notebook)', color='#e67e22', linewidth=2)
        ax2.set_title('Link Speed Negociado (Mbps)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Megabits (Mbps)')
        ax2.grid(True, linestyle='--', alpha=0.6)
        shade_outages(ax2)
        ax2.legend(loc='upper left')

        # --- GRÁFICO 3: SINAL WI-FI (dBm) ---
        ax3.plot(df['Data/Hora'], df['Sinal (dBm)'], label='Sinal Wi-Fi', color='#dc3545', linewidth=2, zorder=3)
        shade_outages(ax3)
        ax3.set_title('Força do Sinal (dBm)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('dBm')
        ax3.set_ylim(-105, -35) 
        aten_line = ax3.axhline(y=-75, color='orange', linestyle='--', label='Atenção (-75 dBm)', zorder=2)
        ax3.grid(True, linestyle='--', alpha=0.6)
        
        # Legenda do Outage apenas no último gráfico para não poluir
        red_patch = mpatches.Patch(color='red', alpha=0.15, label='Outage (Desconexão)')
        handles, labels = ax3.get_legend_handles_labels()
        handles.append(red_patch)
        labels.append('Outage (Desconexão)')
        ax3.legend(handles=handles, labels=labels, loc='upper left')

        # --- FORMATAÇÃO DO HORÁRIO (Eixo X) ---
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)
        plt.xlabel('Horário da Medição', fontsize=12)
        
        plt.tight_layout()
        
        print("Gerando o painel de gráficos... (Feche a janela para encerrar)")
        plt.show()
        
    except FileNotFoundError:
        print("Erro: O arquivo 'log_rede_wifi.csv' não foi encontrado.")
        print("Certifique-se de ter rodado o script de monitoramento antes.")
    except KeyError as k:
        print(f"Erro: Coluna {k} não encontrada. Lembre-se de apagar o .csv antigo!")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    plotar_graficos()
