import tkinter as tk
from tkinter import ttk, messagebox
import re

LIMITE_COMANDO = 1800

# LER $MMAK=

def ler_mmak(texto):

    texto = texto.replace("**", "")
    texto = texto.replace("\r", "")

    linhas = texto.split("\n")

    personagens = []
    serie_atual = None

    for linha in linhas:

        linha = linha.strip()

        if not linha:
            continue

        # Verifica se a linha começa com uma nova série

        match_serie = re.match(
            r"^(.*?)\s+-\s+(\d+/\d+)\s*$",
            linha
        )

        if match_serie:
            serie_atual = match_serie.group(1).strip()
            continue

        # Caso a série e o personagem estejam na mesma linha

        match_mesma_linha = re.match(
            r"^(.*?)\s+-\s+\d+/\d+\s+(.+?)\s+([\d,]+)\s+ka$",
            linha,
            re.IGNORECASE
        )

        if match_mesma_linha:

            serie = match_mesma_linha.group(1).strip()
            nome = match_mesma_linha.group(2).strip()
            kakera = int(match_mesma_linha.group(3).replace(",", ""))

            personagens.append({
                "serie": serie,
                "nome": nome,
                "kakera": kakera
            })

            serie_atual = serie
            continue

        # Personagem pertencente à série atual

        if serie_atual:

            match_personagem = re.match(
                r"^(.+?)\s+([\d,]+)\s+ka$",
                linha,
                re.IGNORECASE
            )

            if match_personagem:

                nome = match_personagem.group(1).strip()
                kakera = int(match_personagem.group(2).replace(",", ""))

                personagens.append({
                    "serie": serie_atual,
                    "nome": nome,
                    "kakera": kakera
                })

    return personagens


# ORGANIZAR

def organizar(personagens):

    series = {}

    # Agrupar TODOS os personagens da mesma série
    for personagem in personagens:

        serie = personagem["serie"]

        if serie not in series:
            series[serie] = []

        series[serie].append(personagem)

    # Dentro de cada série:
    # maior kakera primeiro

    for serie in series:

        series[serie].sort(
            key=lambda p: (
                -p["kakera"],
                p["nome"].lower()
            )
        )

    # A MAIOR kakera da série decide onde a série inteira fica

    ordem_series = sorted(
        series.keys(),
        key=lambda serie: (
            -max(p["kakera"] for p in series[serie]),
            serie.lower()
        )
    )

    resultado = []

    for serie in ordem_series:

        # Coloca TODOS os personagens daquela série juntos
        resultado.extend(series[serie])

    return resultado


# GERAR COMANDOS

def gerar_comandos(personagens):

    if not personagens:
        return []

    nomes = [p["nome"] for p in personagens]

    comandos = []

    atual = "$smp"

    for i, nome in enumerate(nomes):

        parte = " $ " + nome

        if len(atual) + len(parte) > LIMITE_COMANDO:

            comandos.append(atual)

            anterior = nomes[i - 1]

            atual = "$smpos " + anterior

        atual += parte

    if atual != "$sm":
        comandos.append(atual)

    return comandos

def criar_resultado(personagens):

    linhas = []

    serie_anterior = None

    for numero, personagem in enumerate(personagens, 1):

        if personagem["serie"] != serie_anterior:

            if serie_anterior is not None:
                linhas.append("")

            linhas.append(
                f"[ {personagem['serie']} ]"
            )

            serie_anterior = personagem["serie"]

        linhas.append(
            f"{numero:4} | "
            f"{personagem['kakera']:4} ka | "
            f"{personagem['nome']}"
        )

    return "\n".join(linhas)


# ORGANIZAR BOTÃO

def executar():

    texto = caixa_entrada.get(
        "1.0",
        tk.END
    ).strip()

    if not texto:

        messagebox.showwarning(
            "Nothing to sort",
            "Paste the result of $mmak= first."
        )

        return

    personagens = ler_mmak(texto)

    if not personagens:

        messagebox.showerror(
            "Error",
            "Couldn't find any characters in the input. Make sure you pasted the entire result of $mmak=."
        )

        return

    organizados = organizar(personagens)

    # Ordem
    caixa_ordem.delete(
        "1.0",
        tk.END
    )

    caixa_ordem.insert(
        tk.END,
        criar_resultado(organizados)
    )

    # Comandos
    comandos = gerar_comandos(organizados)

    caixa_comandos.delete(
        "1.0",
        tk.END
    )

    for comando in comandos:

        caixa_comandos.insert(
            tk.END,
            comando + "\n\n"
        )

    status.set(
        f"{len(personagens)} personagens | "
        f"{len(set(p['serie'] for p in personagens))} séries | "
        f"{len(comandos)} comando(s)"
    )


# COPIAR

def copiar_comandos():

    texto = caixa_comandos.get(
        "1.0",
        tk.END
    ).strip()

    if not texto:
        return

    janela.clipboard_clear()
    janela.clipboard_append(texto)
    janela.update()

    status.set("Commands copied!")

def limpar():

    caixa_entrada.delete(
        "1.0",
        tk.END
    )

    caixa_ordem.delete(
        "1.0",
        tk.END
    )

    caixa_comandos.delete(
        "1.0",
        tk.END
    )

    status.set("Pronto.")


# HUD

janela = tk.Tk()

janela.title("Mudae SortMarry")
janela.geometry("850x650")
janela.minsize(650, 500)

# TÍTULO

titulo = ttk.Label(
    janela,
    text="Mudae SortMarry",
    font=("Segoe UI", 16, "bold")
)

titulo.pack(pady=(10, 2))


subtitulo = ttk.Label(
    janela,
    text="Paste the entire $mmak= result below."
)

subtitulo.pack(pady=(0, 8))

# INPUT

ttk.Label(
    janela,
    text="$mmak=:"
).pack(
    anchor="w",
    padx=12
)


caixa_entrada = tk.Text(
    janela,
    height=10,
    wrap="word",
    font=("Consolas", 9)
)

caixa_entrada.pack(
    fill="both",
    expand=True,
    padx=12,
    pady=(3, 7)
)


# BOTÕES

frame_botoes = ttk.Frame(janela)

frame_botoes.pack(
    pady=3
)


ttk.Button(
    frame_botoes,
    text="SORT",
    command=executar
).pack(
    side="left",
    padx=3
)


ttk.Button(
    frame_botoes,
    text="CLEAR",
    command=limpar
).pack(
    side="left",
    padx=3
)


# COMMANDS

ttk.Label(
    janela,
    text="Commands to Mudae:"
).pack(
    anchor="w",
    padx=12,
    pady=(6, 2)
)


caixa_comandos = tk.Text(
    janela,
    height=5,
    wrap="word",
    font=("Consolas", 9)
)

caixa_comandos.pack(
    fill="x",
    padx=12,
    pady=(2, 3)
)


ttk.Button(
    janela,
    text="COPY COMMANDS",
    command=copiar_comandos
).pack(
    anchor="e",
    padx=12,
    pady=(0, 5)
)


# -----------------------------
# LOG
# -----------------------------

ttk.Label(
    janela,
    text="Log:"
).pack(
    anchor="w",
    padx=12
)


caixa_ordem = tk.Text(
    janela,
    height=4,
    wrap="word",
    font=("Consolas", 8)
)

caixa_ordem.pack(
    fill="x",
    padx=12,
    pady=(2, 4)
)


# STATUS

status = tk.StringVar()
status.set("Ready.")

ttk.Label(
    janela,
    textvariable=status
).pack(
    pady=(2, 6)
)


janela.mainloop()
