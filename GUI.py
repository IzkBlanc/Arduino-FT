import tkinter as tk
from tkinter import messagebox, scrolledtext
import serial
import threading
import time

# Configuração da porta serial
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)  # Ajuste a porta correta!
    print("Conectado ao Arduino.")
except:
    messagebox.showerror("Erro", "Não foi possível conectar ao Arduino.")
    arduino = None

class InterfaceArduino:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Fluxo de Água")

        # Variáveis para armazenar dados
        self.taxa_fluxo = 0.0
        self.total_gasto = 0.0  # Total gasto em litros

        # Labels para exibir informações em tempo real
        self.fluxo_label = tk.Label(root, text="Taxa de Fluxo: --- L/min", font=("Arial", 14))
        self.fluxo_label.pack(pady=5)

        self.led_label = tk.Label(root, text="Alto consumo: ---", font=("Arial", 14))
        self.led_label.pack(pady=5)

        self.total_label = tk.Label(root, text="Total Gasto: 0.00 L", font=("Arial", 14))
        self.total_label.pack(pady=5)

        # Área de texto para exibir registros
        self.registros_text = scrolledtext.ScrolledText(root, width=50, height=10, font=("Arial", 12))
        self.registros_text.pack(pady=10)

        # Configuração das cores para os registros
        self.registros_text.tag_configure("verde", foreground="green")
        self.registros_text.tag_configure("vermelho", foreground="red")

        # Controle de scroll automático
        self.scroll_automatico = True
        self.registros_text.bind("<MouseWheel>", self.desativar_scroll)

        # Botões
        self.reset_button = tk.Button(root, text="Resetar Total", command=self.confirmar_reset, font=("Arial", 12))
        self.reset_button.pack(pady=5)

        self.exit_button = tk.Button(root, text="Sair", command=self.sair, font=("Arial", 12))
        self.exit_button.pack(pady=5)

        # Inicia a leitura assíncrona da porta serial
        if arduino:
            self.ler_dados()

    def ler_dados(self):
        def atualizar():
            while True:
                try:
                    linha = arduino.readline().decode().strip()
                    if linha:
                        print(f"Recebido: {linha}")  # Depuração
                        self.exibir_registro(linha)

                        if linha.startswith("Taxa de fluxo:"):
                            taxa_fluxo = float(linha.split(":")[1].strip())
                            self.atualizar_fluxo(taxa_fluxo)
                except Exception as e:
                    print(f"Erro na leitura: {e}")
                time.sleep(1)

        thread = threading.Thread(target=atualizar, daemon=True)
        thread.start()

    def atualizar_fluxo(self, taxa_fluxo):
        """Atualiza a taxa de fluxo e o total gasto."""
        self.taxa_fluxo = taxa_fluxo
        self.fluxo_label.config(text=f"Taxa de Fluxo: {self.taxa_fluxo:.2f} L/min")

        # Acumula o total gasto (considerando leituras por minuto)
        self.total_gasto += self.taxa_fluxo / 60  # Converte para litros por segundo
        self.total_label.config(text=f"Total Gasto: {self.total_gasto:.2f} L")

        # Atualiza o estado do LED
        led_status = "Não" if self.taxa_fluxo >= 7 else "Sim"
        self.led_label.config(text=f"Alto consumo: {led_status}")

    def exibir_registro(self, registro):
        """Exibe o registro na área de texto e controla a rolagem."""
        if "Taxa de fluxo:" in registro:
            valor = float(registro.split(":")[1].strip())
            cor = "vermelho" if valor >= 7 else "verde"
            self.registros_text.insert(tk.END, registro + '\n', cor)
        else:
            self.registros_text.insert(tk.END, registro + '\n')

        # Limita a quantidade de registros a 50
        if int(self.registros_text.index('end-1c').split('.')[0]) > 50:
            self.registros_text.delete(1.0, 2.0)

        if self.scroll_automatico:
            self.registros_text.see(tk.END)  # Rola para o fim automaticamente

    def desativar_scroll(self, event):
        """Desativa o scroll automático quando o usuário interage manualmente."""
        self.scroll_automatico = False
        if self.registros_text.yview()[1] == 1.0:
            self.scroll_automatico = True

    def confirmar_reset(self):
        """Confirma se o usuário deseja realmente resetar o total."""
        resposta = messagebox.askyesno("Confirmar Reset", "Tem certeza que deseja resetar o total gasto?")
        if resposta:
            self.resetar_total()

    def resetar_total(self):
        """Reseta o contador de total gasto."""
        self.total_gasto = 0.0
        self.total_label.config(text="Total Gasto: 0.00 L")

    def sair(self):
        """Fecha a conexão com o Arduino e encerra o programa."""
        if arduino:
            arduino.close()
        self.root.destroy()

# Criação da janela principal
root = tk.Tk()
app = InterfaceArduino(root)
root.mainloop()
