import tkinter as tk
from tkinter import messagebox
import multiprocessing
import copy
import logging

# Configura logging para depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def evaluate_move(args):
    """
    Avalia um movimento no minimax em um processo separado.
    Recebe apenas dados serializáveis para evitar erros de pickling.
    """
    try:
        board, row, col, current_player, alpha, beta, depth, max_depth = args
        logging.debug(f"Avaliando movimento ({row}, {col}) para jogador {current_player}")
        
        board = copy.deepcopy(board)
        board[row][col] = current_player
        
        # Avalia a posição resultante
        score = minimax(board, "O" if current_player == "X" else "X", alpha, beta, depth + 1, max_depth, False)
        
        return {"row": row, "col": col, "score": score}
    except Exception as e:
        logging.error(f"Erro em evaluate_move: {e}")
        raise

def minimax(board, current_player, alpha, beta, depth, max_depth, is_maximizing):
    """
    Algoritmo minimax com poda alfa-beta simplificado.
    """
    try:
        size = len(board)
        
        # Verifica condições de término
        if check_win_state(board, "X"):
            return -1000 + depth  # Vitória do adversário (quanto mais rápido, melhor)
        elif check_win_state(board, "O"):
            return 1000 - depth   # Vitória do computador (quanto mais rápido, melhor)
        elif not any(" " in row for row in board):
            return 0  # Empate
        elif depth >= max_depth:
            return evaluate_position(board)  # Avaliação heurística
        
        empty_cells = [(r, c) for r in range(size) for c in range(size) if board[r][c] == " "]
        
        if current_player == "O":  # Maximizando (computador)
            max_eval = -float('inf')
            for r, c in empty_cells:
                board[r][c] = current_player
                eval_score = minimax(board, "X", alpha, beta, depth + 1, max_depth, False)
                board[r][c] = " "
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:  # Minimizando (jogador)
            min_eval = float('inf')
            for r, c in empty_cells:
                board[r][c] = current_player
                eval_score = minimax(board, "O", alpha, beta, depth + 1, max_depth, True)
                board[r][c] = " "
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
            
    except Exception as e:
        logging.error(f"Erro em minimax: {e}")
        raise

def check_win_state(board, player):
    """Verifica se o jogador venceu."""
    size = len(board)
    # Verifica linhas
    for row in range(size):
        if all(board[row][col] == player for col in range(size)):
            return True
    # Verifica colunas
    for col in range(size):
        if all(board[row][col] == player for row in range(size)):
            return True
    # Verifica diagonal principal
    if all(board[i][i] == player for i in range(size)):
        return True
    # Verifica diagonal secundária
    if all(board[i][size-i-1] == player for i in range(size)):
        return True
    return False

def evaluate_position(board):
    """
    Avaliação heurística simples da posição.
    Pontos positivos para o computador (O), negativos para o jogador (X).
    """
    size = len(board)
    score = 0
    
    # Avalia linhas, colunas e diagonais
    lines = []
    
    # Adiciona linhas
    for row in range(size):
        lines.append([board[row][col] for col in range(size)])
    
    # Adiciona colunas
    for col in range(size):
        lines.append([board[row][col] for row in range(size)])
    
    # Adiciona diagonais
    lines.append([board[i][i] for i in range(size)])
    lines.append([board[i][size-i-1] for i in range(size)])
    
    # Pontua cada linha
    for line in lines:
        o_count = line.count("O")
        x_count = line.count("X")
        empty_count = line.count(" ")
        
        if x_count == 0 and o_count > 0:
            score += o_count * o_count
        elif o_count == 0 and x_count > 0:
            score -= x_count * x_count
    
    return score

def computer_move(board, max_depth, num_workers):
    """
    Função para calcular a jogada do computador usando minimax com paralelização.
    """
    try:
        logging.info("Calculando jogada do computador")
        size = len(board)
        empty_cells = [(r, c) for r in range(size) for c in range(size) if board[r][c] == " "]
        
        if not empty_cells:
            return None
        
        # Para tabuleiros pequenos ou poucas jogadas, não usa paralelização
        if len(empty_cells) <= 4 or size <= 3:
            best_score = -float('inf')
            best_move = None
            
            for r, c in empty_cells:
                board[r][c] = "O"
                score = minimax(board, "X", -float('inf'), float('inf'), 1, max_depth, False)
                board[r][c] = " "
                
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
            
            return best_move
        
        # Para tabuleiros maiores, usa paralelização
        with multiprocessing.Pool(processes=min(num_workers, len(empty_cells))) as pool:
            args = [(board, r, c, "O", -float('inf'), float('inf'), 0, max_depth) for r, c in empty_cells]
            results = pool.map(evaluate_move, args)
        
        if not results:
            return None
            
        best_move = max(results, key=lambda x: x["score"])
        logging.info(f"Melhor jogada encontrada: ({best_move['row']}, {best_move['col']}) com score {best_move['score']}")
        return best_move["row"], best_move["col"]
        
    except Exception as e:
        logging.error(f"Erro em computer_move: {e}")
        raise

class JogoDaVelha:
    def __init__(self):
        """Inicializa a interface gráfica e variáveis do jogo."""
        self.window = tk.Tk()
        self.window.title("Jogo da Velha")
        self.size = None
        self.board = None
        self.current_player = "X"
        self.buttons = []
        self.thinking = False
        self.play_again_button = None  # Referência para o botão "Jogar Novamente"
        
        # Configurações
        self.num_workers = min(4, multiprocessing.cpu_count())
        self.max_depth = 8
        
        self.frame = tk.Frame(self.window)
        self.frame.pack(pady=20)
        
        tk.Label(self.frame, text="Escolha o tamanho:", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.frame, text="3x3", command=lambda: self.show_config(3)).pack(side=tk.LEFT, padx=10)
        tk.Button(self.frame, text="4x4", command=lambda: self.show_config(4)).pack(side=tk.LEFT, padx=10)
        tk.Button(self.frame, text="5x5", command=lambda: self.show_config(5)).pack(side=tk.LEFT, padx=10)
        
    def show_config(self, size):
        """Exibe tela de configuração para profundidade e número de workers."""
        self.size = size
        self.frame.destroy()
        self.frame = tk.Frame(self.window)
        self.frame.pack(pady=20)
        
        tk.Label(self.frame, text="Profundidade (1-12):", font=("Arial", 12)).pack(pady=5)
        self.depth_entry = tk.Spinbox(self.frame, from_=1, to=12, width=5, font=("Arial", 12))
        self.depth_entry.delete(0, tk.END)  # Remove o conteúdo atual
        self.depth_entry.insert(0, "8")     # Define o valor padrão como "8"
        self.depth_entry.pack(pady=5)
        
        tk.Label(self.frame, text="Número de Workers (1-20):", font=("Arial", 12)).pack(pady=5)
        self.workers_entry = tk.Spinbox(self.frame, from_=1, to=20, width=5, font=("Arial", 12))
        self.workers_entry.delete(0, tk.END)  # Remove o conteúdo atual
        self.workers_entry.insert(0, str(min(4, multiprocessing.cpu_count())))  # Define o padrão
        self.workers_entry.pack(pady=5)
        
        tk.Button(self.frame, text="Iniciar Jogo", command=self.start_game, font=("Arial", 12)).pack(pady=10)
        
    def start_game(self):
        """Inicia o jogo com as configurações escolhidas."""
        try:
            self.max_depth = int(self.depth_entry.get())
            workers_input = int(self.workers_entry.get())
            cpu_count = multiprocessing.cpu_count()
            self.num_workers = min(workers_input, cpu_count)
            
            if workers_input > cpu_count:
                messagebox.showwarning("Aviso", f"Número de workers reduzido para {cpu_count} (máximo de núcleos disponíveis).")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores válidos para profundidade e workers.")
            return
        
        if self.max_depth < 1 or self.max_depth > 12 or self.num_workers < 1 or self.num_workers > 20:
            messagebox.showerror("Erro", "Profundidade deve estar entre 1 e 12, e workers entre 1 e 20.")
            return
            
        logging.info(f"Iniciando jogo com profundidade {self.max_depth} e {self.num_workers} workers")
        
        self.board = [[" " for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = "X"
        
        self.frame.destroy()
        self.frame = tk.Frame(self.window)
        self.frame.pack(pady=20)
        
        self.buttons = []
        for row in range(self.size):
            row_buttons = []
            for col in range(self.size):
                btn = tk.Button(self.frame, text="", font=("Arial", 20), width=4, height=2,
                              command=lambda r=row, c=col: self.make_move(r, c))
                btn.grid(row=row, column=col, padx=5, pady=5)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        
        # Cria o botão "Jogar Novamente" e armazena a referência
        self.play_again_button = tk.Button(self.window, text="Jogar Novamente", command=self.reset_game, font=("Arial", 12))
        self.play_again_button.pack(pady=10)
        
        self.thinking_label = tk.Label(self.window, text="", font=("Arial", 12))
        self.thinking_label.pack(pady=5)
        
        self.update_board()
        
    def update_board(self):
        """Atualiza a interface gráfica com o estado do tabuleiro."""
        for row in range(self.size):
            for col in range(self.size):
                self.buttons[row][col].config(text=self.board[row][col],
                                            bg="lightblue" if self.board[row][col] == "X" else
                                            "salmon" if self.board[row][col] == "O" else "white")
        
    def make_move(self, row, col):
        """Processa a jogada do jogador humano (X)."""
        if self.thinking or self.board[row][col] != " " or self.current_player != "X":
            return
            
        logging.info(f"Jogada do jogador humano: ({row}, {col})")
        self.board[row][col] = "X"
        self.update_board()
        
        if self.check_win("X"):
            messagebox.showinfo("Fim do Jogo", "Jogador X venceu!")
            self.reset_game()
            return
        if not self.get_empty_cells():
            messagebox.showinfo("Fim do Jogo", "Empate!")
            self.reset_game()
            return
            
        self.current_player = "O"
        self.thinking = True
        self.thinking_label.config(text="Computador computando...")
        self.window.update()
        
        # Executa a jogada do computador em uma thread separada
        import threading
        thread = threading.Thread(target=self.computer_move_thread)
        thread.daemon = True
        thread.start()
        
    def computer_move_thread(self):
        """Executa a jogada do computador em uma thread separada."""
        try:
            result = computer_move(self.board, self.max_depth, self.num_workers)
            
            # Agenda a aplicação do resultado na interface principal
            self.window.after(0, lambda: self.apply_computer_move(result))
            
        except Exception as e:
            logging.error(f"Erro na thread do computador: {e}")
            self.window.after(0, lambda: self.handle_computer_error(str(e)))
        
    def apply_computer_move(self, result):
        """Aplica a jogada do computador na interface."""
        try:
            if self.thinking and result:
                row, col = result
                self.board[row][col] = "O"
                self.update_board()
                self.thinking = False
                self.thinking_label.config(text="")
                
                if self.check_win("O"):
                    messagebox.showinfo("Fim do Jogo", "Jogador O (Computador) venceu!")
                    self.reset_game()
                    return
                if not self.get_empty_cells():
                    messagebox.showinfo("Fim do Jogo", "Empate!")
                    self.reset_game()
                    return
                    
                self.current_player = "X"
                logging.info("Jogada do computador aplicada")
            else:
                self.thinking = False
                self.thinking_label.config(text="")
                
        except Exception as e:
            logging.error(f"Erro em apply_computer_move: {e}")
            self.thinking = False
            self.thinking_label.config(text="")
            messagebox.showerror("Erro", f"Falha ao aplicar jogada do computador: {e}")
        
    def handle_computer_error(self, error_msg):
        """Trata erros ocorridos durante a jogada do computador."""
        logging.error(f"Erro no cálculo da jogada do computador: {error_msg}")
        self.thinking = False
        self.thinking_label.config(text="")
        messagebox.showerror("Erro", f"Falha no cálculo da jogada: {error_msg}")
        
    def check_win(self, player):
        """Verifica se o jogador venceu."""
        return check_win_state(self.board, player)
    
    def get_empty_cells(self):
        """Retorna a lista de células vazias."""
        empty_cells = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == " ":
                    empty_cells.append((row, col))
        return empty_cells
        
    def reset_game(self):
        """Reinicia o jogo, voltando à tela de seleção."""
        self.frame.destroy()
        if hasattr(self, 'thinking_label') and self.thinking_label.winfo_exists():
            self.thinking_label.destroy()
        if hasattr(self, 'play_again_button') and self.play_again_button and self.play_again_button.winfo_exists():
            self.play_again_button.destroy()
        self.thinking = False
        
        self.frame = tk.Frame(self.window)
        self.frame.pack(pady=20)
        
        tk.Label(self.frame, text="Escolha o tamanho:", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.frame, text="3x3", command=lambda: self.show_config(3)).pack(side=tk.LEFT, padx=10)
        tk.Button(self.frame, text="4x4", command=lambda: self.show_config(4)).pack(side=tk.LEFT, padx=10)
        tk.Button(self.frame, text="5x5", command=lambda: self.show_config(5)).pack(side=tk.LEFT, padx=10)
        
    def run(self):
        """Executa o loop principal do Tkinter."""
        try:
            logging.info("Iniciando loop principal do Tkinter")
            self.window.mainloop()
        except KeyboardInterrupt:
            logging.info("Programa encerrado pelo usuário")
            self.window.destroy()
        except Exception as e:
            logging.error(f"Erro no loop principal: {e}")
            self.window.destroy()

if __name__ == '__main__':
    if multiprocessing.get_start_method(allow_none=True) != 'spawn':
        multiprocessing.set_start_method('spawn')  # Necessário para Windows
    logging.info(f"Número de núcleos disponíveis: {multiprocessing.cpu_count()}")
    game = JogoDaVelha()
    game.run()
