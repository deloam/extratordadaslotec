import requests
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk  # Importando ttk para a barra de progresso
import os  # Importando os para abrir a pasta
from datetime import datetime
import platform
import sys

# Configuração especial para PyInstaller
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

# Função para verificar a conexão com a internet
def verificar_conexao():
    try:
        requests.get("https://www.google.com", timeout=5)  # Verifica a conexão com um site confiável
        return True
    except requests.ConnectionError:
        return False

# URL base do site
base_url = "https://www.stlucialotto.com/snl/statistics.php?s_GameID=3&s_Month=10&s_Year=2005"

# Inicializando listas para os dados
datas = []
numeros_vencedores = []
letters = []
TopPrize = []
match3 = []
match2 = []

# Função para coletar dados de uma página
def coletar_dados(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrando a tabela pelo ID
        table = soup.find('table', id='TGrid')
        if table is None:
            print("Tabela não encontrada na URL:", url)  # Mensagem de depuração
            return  # Retorna se a tabela não for encontrada
        
        print("Tabela encontrada!")  # Mensagem de depuração
        
        # Iterando pelas linhas da tabela
        for row in table.find_all('tr')[1:]:  # Ignorando o cabeçalho
            cols = row.find_all('td')
            if len(cols) < 5:  # Verifica se há pelo menos 5 colunas
                continue  # Ignora a linha se não tiver colunas suficientes
            
            # Pegar os dados das colunas
            data = cols[0].text.strip()
            numeros = cols[1].text.strip().replace('\xa0', ' ').split()  # Substitui &nbsp; por espaço e divide os números
            letter = cols[3].text.strip()  # Captura a letra
            premio = cols[4].text.strip()  # Captura o prêmio
            match3_val = cols[7].text.strip()  # Captura Match 5
            match2_val = cols[8].text.strip()  # Captura Match 3
            
            # Adiciona os dados às listas
            datas.append(data)
            numeros_vencedores.append(numeros)
            letters.append(letter)
            TopPrize.append(premio)
            match3.append(match3_val)
            match2.append(match2_val)

            print(f"Dados coletados: {data}, {numeros}, {letter}, {premio}, {match3_val}, {match2_val}")  # Mensagem de depuração

    except Exception as e:
        print(f"Ocorreu um erro ao coletar os dados: {e}")

def extrair_dados():
    if not verificar_conexao():
        messagebox.showerror("Erro de Conexão", "Verifique sua conexão com a internet e tente novamente.")
        return

    global datas, numeros_vencedores, TopPrize, match3, match2
    datas = []
    numeros_vencedores = []
    TopPrize = []
    match3 = []
    match2 = []

    # Definindo o ano inicial e o ano atual
    ano_inicial = 2005
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month

    # Calcular o total de meses a serem coletados
    total_meses = (ano_atual - ano_inicial) * 12 + mes_atual - 10 + 1  # Começando em outubro de 2005

    # Criar a barra de progresso e o label de progresso
    progress['maximum'] = total_meses  # Definindo o valor máximo da barra de progresso
    progress.pack(pady=10)  # Empacotar a barra de progresso
    label_progresso.pack(pady=5)  # Empacotar o label de progresso

    # Iterando pelos anos e meses
    for ano in range(ano_inicial, ano_atual + 1):
        for mes in range(1, 13):
            # Se for o ano atual, limite o mês ao mês atual
            if ano == ano_atual and mes > mes_atual:
                break
            
            # Construindo a URL com base no mês e ano
            url = f"https://www.stlucialotto.com/snl/statistics.php?s_GameID=3&s_Month={str(mes).zfill(2)}&s_Year={ano}"
            print(f"Coletando dados de {mes}/{ano}...")  # Mensagem de depuração
            
            # Atualizar o label de progresso
            label_progresso.config(text=f"Coletando dados de {mes}/{ano}...")
            
            # Coletar dados da página
            coletar_dados(url)

            # Atualizar a barra de progresso
            progress['value'] += 1
            frame.update_idletasks()  # Atualiza a interface gráfica

    # Verifique se os dados foram coletados antes de salvar
    if not datas:
        messagebox.showwarning("Aviso", "Nenhum dado foi coletado.")
        return

    # Criar um DataFrame
    df = pd.DataFrame(numeros_vencedores, columns=['1', '2', '3', '4', '5', '6'])  # Colunas para os números vencedores
    df.insert(0, 'Data do sorteio', datas)  # Inserir a data no início
    df['Letra'] = letters  # Adicionar a coluna de letras
    df['Jackpot'] = TopPrize  # Adicionar a coluna de prêmio
    df['Match 5'] = match3  # Adicionar Match 5
    df['Match 4'] = match2  # Adicionar Match 3

    # Converter a coluna de datas para datetime e ordenar
    df['Data do sorteio'] = pd.to_datetime(df['Data do sorteio'], format='%d-%b-%Y')  # Ajuste o formato conforme necessário
    df = df.sort_values(by='Data do sorteio', ascending=False)  # Ordenar da mais recente para a mais antiga

   # Selecionar o diretório para salvar o arquivo
    save_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        initialfile="dados_loteria.xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        initialdir=os.path.expanduser("~\\Documents")
    )

    if save_path:
        try:
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Salva o arquivo Excel
            df.to_excel(save_path, index=False, engine='openpyxl')
            
            # Mostra mensagem de sucesso com o caminho completo
            messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\n{save_path}")
            
            # Abre a pasta no explorador de arquivos
            if platform.system() == "Windows":
                os.startfile(os.path.dirname(save_path))
            elif platform.system() == "Darwin":
                os.system(f'open "{os.path.dirname(save_path)}"')
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar o arquivo:\n{str(e)}") 
# Criar a interface gráfica
root = tk.Tk()
root.title("Extrair Dados - Programa de Coleta de Resultados da Loteria")  # Título do programa

# Definindo o tamanho da janela
root.geometry("400x300")  # Largura x Altura

# Adicionando uma margem
frame = tk.Frame(root, padx=20, pady=20)  # Margem de 20 pixels
frame.pack()

button = tk.Button(frame, text="Extrair Dados", command=extrair_dados)
button.pack(pady=20)

# Criar a barra de progresso e o label de progresso, mas não empacotar ainda
progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
label_progresso = tk.Label(frame, text="")

root.mainloop()
