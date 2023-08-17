def print_board(board):
    """
    Essa função printa no terminal o jogo em questão (3x3, 4x4, 5x5)
    """
    size = len(board)
    for row in board:
        print(" |".join(row))
        if row != board[-1]:
            print("--+" * (size - 1) + "---")

    print("\nEnter the number (1-{}) to make a move:".format(size * size))
    for row in range(size):
        print("|".join(str(col + 1 + row * size).rjust(2) for col in range(size)))
        if row != size - 1:
            print("--+" * (size - 1) + "--")

def check_win(board, player):
    """
    Essa parte da função checa se o jogador ganhou o jogo ou não
    """
    size = len(board)
    # checa as linhas
    for row in range(size):
        if all(board[row][col] == player for col in range(size)):
            return True
    # check as colunas
    for col in range(size):
        if all(board[row][col] == player for row in range(size)):
            return True
    # checa as diagonais
    if all(board[i][i] == player for i in range(size)):
        return True
    if all(board[i][size-i-1] == player for i in range(size)):
        return True
    return False

def get_empty_cells(board):
    """
    Essa função retorna as listas de tuplas que representam as celulas vazias do tabuleiro
    """
    empty_cells = []
    size = len(board)
    for row in range(size):
        for col in range(size):
            if board[row][col] == " ":
                empty_cells.append((row, col))
    return empty_cells

def generate_tree(board, current_player, alpha=-float('inf'), beta=float('inf'), depth=0, max_depth=6):
    """
    Aqui, essa função gera uma "árvore" de possibilidades que o computador pode jogar, usando o algoritmo do minimax
    junto ao "poda" alpha beta (alpha-beta prunning).
    retorna um dict representando essa árvore com a melhor jogada e sua pontuação

    """
    # Checa como o o jogo terminaria
    if check_win(board, "X"):
        # Se o jogador X ganha, retorna -1
        return {"score": -1}
    elif check_win(board, "O"):
        # Se o jogador O ganha, retorna +1 (no sentido de positivo)
        return {"score": 1}
    elif len(get_empty_cells(board)) == 0:
        # Se o jogo termina em empate a pontuação é 0
        return {"score": 0}
    elif depth >= max_depth:
        # Configuração de nível de profundidade da árvore, para evitar crash 
        # se a profundidade max for alcançada retorna uma pontuação estimada do momento
        return {"score": 0}

    # Inicializando a Arvore
    tree = {"score": None, "moves": []}
    
    #  Calcular sobre todos os movimentos possíveis
    for row, col in get_empty_cells(board):
        # Fazer a jogada no tabuleiro
        board[row][col] = current_player
        # Geração das sub-arvores de cada jogada
        subtree = generate_tree(board, "O" if current_player == "X" else "X", alpha, beta, depth + 1, max_depth)
        # Refazendo a movimentação do tabuleiro
        board[row][col] = " "
        # Adiciona a jogada e sua sub-arvore para a árvore do jogo
        tree["moves"].append({"row": row, "col": col, "subtree": subtree})

        # Atualiza os valores do alpha e do beta para o alpha-beta pruning (cortar jogadas futeis)
        if current_player == "X":
            beta = min(beta, subtree["score"])
            if beta <= alpha:
                break
        else:
            alpha = max(alpha, subtree["score"])
            if beta <= alpha:
                break

    # Calcula a pontuação da árvore de jogo baseado nas pontuações das sub-árvores
    if current_player == "X":
        tree["score"] = min(move["subtree"]["score"] for move in tree["moves"])
    else:
        tree["score"] = max(move["subtree"]["score"] for move in tree["moves"])

    return tree


def play_game():
    """
    Essa parte da função iniciliza um novo jogo, e manipula o input do usuário
    """
    
while True:
        while True:
            size = input("Enter the size of the board (3, 4 or 5): ") # tamanho do tabuleiro
            if size.isdigit() and int(size) in [3, 4, 5]: #limitação do tamanho do tabuleiro
                size = int(size)
                break
            else:
                print("Invalid input. Please enter a valid size (3, 4 or 5).")#limitação para obrigar o input requerido

        board = [[" " for _ in range(size)] for _ in range(size)]
        current_player = "X"# o jogador humano sempre será o X
        
        while True:
            print_board(board)

            if current_player == "X" or size > 5:
                while True:
                    move = input("Player {}, enter your move (1-{}): ".format(current_player, size * size))
                    if move.isdigit() and 1 <= int(move) <= size * size:
                        move = int(move) - 1
                        row = move // size
                        col = move % size
                        if board[row][col] == " ":
                            break
                        else:
                            print("Invalid move. That cell is already occupied. Try again.") # bloqueando jogadas repetidas
                    else:
                        print("Invalid move. Please enter a valid move (1-{}).".format(size * size))
                board[row][col] = current_player
            else:
                tree = generate_tree(board, current_player) # quando o jogador faz uma jogada legal, chamando a função de calculo das possibilidades
                best_move = max(tree["moves"], key=lambda move: move["subtree"]["score"])
                row, col = best_move["row"], best_move["col"]
                board[row][col] = current_player

            if check_win(board, current_player): #função para declarar vitória
                print_board(board)
                if current_player == "X":
                    print("Player X wins!")
                else:
                    print("Player O wins!")
                break

            if len(get_empty_cells(board)) == 0:
                print_board(board)
                print("It's a tie!")
                break

            current_player = "O" if current_player == "X" else "X"

        while True:# chamada para jogar de novo
            play_again = input("Do you want to play again? (y/n): ")
            if play_again.lower() in ["y", "n"]:
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

        if play_again.lower() != "y":
            break

play_game()
'''
Esta função usa o algoritmo minimax com a "poda" alfa-beta (prunning) para gerar uma árvore de jogo representando todos os movimentos possíveis e seus resultados.
A função recebe como entrada o estado atual do tabuleiro, o jogador atual (seja “X” ou “O”) e parâmetros opcionais para remoção alfa-beta (alfa e beta), 
a profundidade atual da árvore (depth) e a profundidade máxima da árvore (max_depth).

A função, primeiro, verifica se o jogo terminou, chamando check_win para ambos os jogadores e verificando se ainda há células vazias no tabuleiro.

Se alguma dessas condições forem atendidas, ele retorna um dicionário com uma chave de pontuação representando o resultado do jogo 
(-1 se o jogador X vencer, 1 se o jogador O vencer ou 0 se houver empate).

Se nenhuma dessas condições forem atendidas, e a profundidade máxima ainda não tiver sido atingida (depth < max_depth),
ele inicializa uma árvore de jogo vazia com pontuação definida como None e uma lista vazia de movimentos. 
Em seguida, repete sobre todos os movimentos possíveis (células vazias no tabuleiro) e faz cada movimento em uma cópia do tabuleiro. 

Para cada movimento, ele gera uma sub-árvore chamando o generate_tree, recursivamente(repetição), com parâmetros atualizados 
(o novo estado do tabuleiro depois de fazer o movimento, alternando para a vez do outro jogador, atualizando alfa e beta, incrementando a profundidade 
e mantendo max_depth inalterado).

Em seguida, ele desfaz o movimento no tabuleiro e adiciona uma entrada à árvore ["movimentos"] representando esse movimento e sua subárvore.

Depois de gerar todas as subárvores para todos os movimentos possíveis, ele atualiza a árvore ["pontuação"] com base na vez do jogador X ou do jogador O.

Se for a vez do jogador X (o jogador minimizador), ele define a árvore ["pontuação"] para ser igual à pontuação mínima entre todas as subárvores.

Se for a vez do jogador O (o jogador maximizador), ele define a árvore ["pontuação"] para ser igual à pontuação máxima entre todas as subárvores.

Finalmente, ele retorna a árvore, que representa todos os movimentos possíveis a partir deste ponto junto com suas pontuações.
'''