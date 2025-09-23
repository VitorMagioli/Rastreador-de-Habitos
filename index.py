import json
import tkinter as tk
import datetime
from tkinter import messagebox, simpledialog


class RastreadordeHabitos:
    def _carregar_habitos(self):
        # --- Bloco para tentar abrir o arquivo salvo, caso contrário pedir para o usuario criar um hábito ---
        try:
            with open('dados.json', 'r') as arquivo:
                self.habitos = json.load(arquivo)

        except FileNotFoundError:
            self.habitos = [] #Se não houver arquivo, a lista começa vazia


    # --- Função para verificar se a ofensiva foi quebrada, caso seja, ela Zera ofensiva.
    def _verificar_habitos(self):
        hoje = datetime.date.today()

        for habito in self.habitos:
            # Primeiro, checamos se o hábito já foi marcado alguma vez
            if 'ultimo_registro' in habito:
                # Converte o texto da data do arquivo para um objeto data
                ultimo_registro_data = datetime.date.fromisoformat(habito['ultimo_registro'])

                # Calcula a diferença entre as datas
                diferenca_em_dias = (hoje - ultimo_registro_data).days

                # Se a diferença for maior que 1, a ofensiva quebrou
                if diferenca_em_dias > 1:
                    habito['ofensiva'] = 0

        # Após verificar todos os hábitos, salvamos as possíveis alterações
        self._salvar_habitos()


    def __init__(self, root):
        self.root = root
        self.root.title("Rastreador-de-Habitos")
        self.root.geometry("400x300")  # Define um tamanho inicial para a janela

        self.habitos = [] #lista de hábitos

        #--- Widgets Principais ---
        self.frame_lista = tk.Frame(root)
        self.frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
        tk.Button(root, text="Adicionar Novo Hábito", command=self._adicionar_habitos).pack(pady=10)

        self._carregar_habitos()  # Função para carregar hábitos do JSON

        self._verificar_habitos() # Verifica se a ofensiva foi quebrada

        if not self.habitos:
            # A lista está vazia, então pedimos para criar o primeiro.
            # A função _adicionar_habito vai chamar _atualizar_lista_ui por nós.
            self._adicionar_habitos()
        else:
            # A lista já tem dados, então apenas desenhamos a UI.
            self._atualizar_lista_ui()  # Desenha a interface inicial do usuário - UI

    def _adicionar_habitos(self):
        #1. Pergunta o nome do novo hábito
        novo_habito_nome = simpledialog.askstring("Novo Hábito", "Qual o nome do Novo Hábito?")

        #2. Valida se o usuário digitou algo
        if novo_habito_nome:
            #3. Cria um dicionário com o novo hábito
            novo_habito = {
                "nome": novo_habito_nome,
                "ofensiva": 0
            }
            #4. Adiciona o novo hábito à lista na memória
            self.habitos.append(novo_habito)

            #5. Salva a lista atualizada no arquivo
            self._salvar_habitos()

            #6. Redesenha a interface para mostra a lista atualizada
            self._atualizar_lista_ui()

    def _salvar_habitos(self):
        with open('dados.json', 'w') as arquivo:
            json.dump(self.habitos, arquivo, indent=4) #indent4 deixa o JSON organizado

    def _deletar_habito(self, index_do_habito):
        habito = self.habitos[index_do_habito] # Pega o dicionário do hábito específico que o usuário quer deletar. Fazemos isso para usar o nome do hábito na mensagem de confirmação
        confirmado = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar o hábito '{habito['nome']}'?")
        if confirmado:
            self.habitos.pop(index_do_habito) #Remove um item em um índice específico
            self._salvar_habitos()
            self._atualizar_lista_ui() #Le novamente a lista de hábitos e cria os widgets na tela


    def _atualizar_lista_ui(self):
        #1. Limpa todos os Widgets antigos da lista
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        #2. Cria um widget para cada hábito da lista
        for index, habito in enumerate(self.habitos):
            #Frame Principal da linha
            frame_habito = tk.Frame(self.frame_lista, bd=1, relief="solid")
            frame_habito.pack(fill="x", pady=2, ipady=2)

            # 1. Frame da Direita (para os botões)
            frame_direita = tk.Frame(frame_habito)
            frame_direita.pack(side="right", padx=5)

            # 2. Frame Central (para a ofensiva)
            frame_central = tk.Frame(frame_habito)
            frame_central.pack(side="right")

            # 3. Frame da Esquerda (para o nome do hábito)
            frame_esquerda = tk.Frame(frame_habito)
            frame_esquerda.pack(side="left", expand=True, fill="x", padx=5)

            # --- Widgets dentro dos Frames ---

            # Nome do hábito: Frame da esquerda
            tk.Label(frame_esquerda, text=habito['nome'], anchor="w").pack(fill="x")
            # Número da ofensiva: Frame central
            tk.Label(frame_central, text=habito['ofensiva'], font=("Arial", 12, "bold"), width=4).pack()

            # Botões: Frame da direita
            #Botão Fiz Hoje - marca ofensiva feita
            btn_feito = tk.Button(frame_direita, text="Fiz Hoje!", command=lambda idx=index: self.marcar_feito(idx))
            btn_feito.pack(side="left")
            # Botão Deletar - apaga hábito
            btn_deletar = tk.Button(frame_direita, text="X", fg="red", command=lambda idx=index: self._deletar_habito(idx))
            btn_deletar.pack(side="left", padx=5)


    def marcar_feito(self, index_do_habito):
        # Esta é a função que o botão "Fiz hoje" vai executar
        habito = self.habitos[index_do_habito]
        hoje = datetime.date.today()
        # --- CLÁUSULA PARA GUARDA: Evitar cliques duplicados! ---
        if 'ultimo_registro' in habito:
            ultimo_registro_data = datetime.date.fromisoformat(habito['ultimo_registro'])
            if ultimo_registro_data == hoje:
                messagebox.showinfo("Aviso", "Você já marcou esse hábito como Feito hoje!")
                return # Para a execução da função aqui

        #--- 1. Incrementar a Ofensiva ---
        self.habitos[index_do_habito]['ofensiva'] += 1

        #--- 2. Adicionar/Atualizar a data do último registro ---
        hoje_em_texto = datetime.date.today().isoformat()
        self.habitos[index_do_habito]['ultimo_registro'] = hoje_em_texto

        #--- 3. Salvar tudo e redesenhar na tela ---
        self._salvar_habitos()
        self._atualizar_lista_ui() #redesenha a tela com os novos valores
        messagebox.showinfo("Parabéns!", "Você cumpriu seu hábito de hoje!")

# --- Código principal que inicia o programa ---
if __name__ == "__main__":
    janela_principal = tk.Tk()
    app = RastreadordeHabitos(janela_principal)
    janela_principal.mainloop()
