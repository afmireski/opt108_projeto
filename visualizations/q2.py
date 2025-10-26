# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pandas",
# ]
# ///
import pandas as pd
import os
from collections import defaultdict
from itertools import combinations

# Caminho do arquivo de entrada
input_file = "datasets/netflix_titles.csv"

# Leitura do dataset
print("Lendo o arquivo...")
data = pd.read_csv(input_file)

# Função para computar os países associados a cada diretor e determinar o grupo
def compute_director_groups(data):
    """
    Para cada diretor, percorre todos os filmes em que ele participou, coleta os países
    (ignorando valores nulos) e determina o grupo:
      - único país -> nome do país
      - mais de um país -> 'Internacional'
      - nenhum país -> 'S/P'

    Args:
        data (DataFrame): DataFrame contendo as colunas 'director' e 'country'.

    Returns:
        dict: mapeamento diretor -> grupo (string)
    """
    director_countries = defaultdict(set)

    for _, row in data.iterrows():
        # Só percorre se houver diretor; países nulos são ignorados
        if pd.notna(row.get('director')):
            # lista de diretores (algumas células podem ter múltiplos, separados por ', ')
            directors = [d.strip() for d in str(row['director']).split(',') if d.strip()]
            # se houver country válido, extrai a lista de países; caso contrário, não adiciona nada
            if pd.notna(row.get('country')):
                countries = [c.strip() for c in str(row['country']).split(',') if c.strip()]
            else:
                countries = []

            for director in directors:
                director_countries[director].update(countries)

    # Determina o grupo de cada diretor
    director_groups = {}
    for director, countries in director_countries.items():
        if len(countries) == 1:
            director_groups[director] = next(iter(countries))
        elif len(countries) > 1:
            director_groups[director] = 'Internacional'
        else:
            director_groups[director] = 'S/P'

    return director_groups

# Extração e limpeza dos diretores
print("Extraindo e limpando os dados da coluna 'director'...")
directors = defaultdict(int)

# Contagem de aparições (filmes) por diretor
for dcell in data['director'].dropna():
    # algumas células têm múltiplos diretores separados por vírgula
    for director in [s.strip() for s in str(dcell).split(',') if s.strip()]:
        directors[director] += 1

# Contagem de filmes por diretor
director_movie_count = {director: count for director, count in directors.items()}

# Exibe o número total de diretores únicos
print(f"Número total de diretores únicos na base: {len(director_movie_count)}")

# Seleção dos top 100 diretores (configurável)
TOP_N = 100

top_directors = sorted(director_movie_count.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

# Exibe os top 100 diretores
print(f"Top {TOP_N} diretores selecionados:")
for director, count in top_directors:
    print(f"{director}: {count} filmes")

# Contagem de interações entre os top 100 diretores (co-direção)
interactions = defaultdict(int)

# Filtra os nomes dos top 100 diretores
top_director_names = set(director for director, _ in top_directors)

# Conta as interações (quando dois ou mais diretores aparecem no mesmo filme)
for dcell in data['director'].dropna():
    directors_in_movie = [d for d in [s.strip() for s in str(dcell).split(',') if s.strip()] if d in top_director_names]
    for pair in combinations(directors_in_movie, 2):
        interactions[tuple(sorted(pair))] += 1

# Exibe as interações mais fortes entre os top diretores
print("Interações mais fortes entre os top 100 diretores:")
for pair, count in sorted(interactions.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{pair}: {count} filmes")

# Geração dos arquivos CSV para o Flourish
# Cria o diretório para os resultados, se não existir
results_dir = "results/q2"
os.makedirs(results_dir, exist_ok=True)

# Atualiza os caminhos dos arquivos CSV
links_file = os.path.join(results_dir, "links.csv")
points_file = os.path.join(results_dir, "points.csv")

# Cria o arquivo links.csv (diretores)
with open(links_file, 'w') as f:
    f.write("Source,Target,Movies_Count\n")
    for (source, target), count in interactions.items():
        f.write(f"{source},{target},{count}\n")

# Obtém os grupos por diretor (país / Internacional / S/P)
director_groups = compute_director_groups(data)

# Atualiza o arquivo points.csv com os grupos corretos
print("Atualizando o arquivo points.csv com os grupos dos diretores...")
with open(points_file, 'w') as f:
    f.write("Director,Group,Movies_Count\n")
    for director, count in top_directors:
        group = director_groups.get(director, "S/P")  # Default para "S/P" se o diretor não tiver dados
        f.write(f"{director},{group},{count}\n")

# Resumo e validação
print("\nResumo do processamento:")
print(f"Número total de diretores únicos: {len(director_movie_count)}")
print(f"Número de diretores selecionados (top {TOP_N}): {len(top_directors)}")
print(f"Número total de interações registradas: {len(interactions)}")
print(f"Arquivos gerados:\n- {links_file}\n- {points_file}")
