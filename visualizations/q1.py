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

# Função corrigida para computar os países associados a cada ator
def compute_actor_countries(data):
    """
    Computa os países dos filmes em que cada ator trabalhou e determina o grupo.

    Args:
        data (DataFrame): DataFrame contendo as colunas 'cast' e 'country'.

    Returns:
        dict: Um dicionário onde as chaves são os nomes dos atores e os valores são os grupos.
    """
    actor_countries = defaultdict(set)

    # Para cada linha do DataFrame
    for _, row in data.iterrows():
        if pd.notna(row['cast']) and pd.notna(row['country']):
            countries = row['country'].split(', ')
            for actor in row['cast'].split(', '):
                actor_countries[actor].update(countries)

    # Determina o grupo de cada ator
    actor_groups = {}
    for actor, countries in actor_countries.items():
        if len(countries) == 1:
            actor_groups[actor] = list(countries)[0]  # Único país
        elif len(countries) > 1:
            actor_groups[actor] = "Internacional"  # Mais de um país
        else:
            actor_groups[actor] = "S/P"  # Sem país

    return actor_groups

# Extração e limpeza dos atores
print("Extraindo e limpando os dados da coluna 'cast'...")
actors = defaultdict(int)

for cast in data['cast'].dropna():
    for actor in cast.split(', '):
        actors[actor] += 1

# Contagem de filmes por ator
actor_movie_count = {actor: count for actor, count in actors.items()}

# Exibe o número total de atores únicos
print(f"Número total de atores únicos na base: {len(actor_movie_count)}")

# Seleção dos top 100 atores (configurável)
TOP_N = 100

top_actors = sorted(actor_movie_count.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

# Exibe os top 100 atores
print(f"Top {TOP_N} atores selecionados:")
for actor, count in top_actors:
    print(f"{actor}: {count} filmes")

# Contagem de interações entre os top 100 atores
interactions = defaultdict(int)

# Filtra os nomes dos top 100 atores
top_actor_names = set(actor for actor, _ in top_actors)

# Conta as interações nos filmes
for cast in data['cast'].dropna():
    actors_in_movie = [actor for actor in cast.split(', ') if actor in top_actor_names]
    for pair in combinations(actors_in_movie, 2):
        interactions[tuple(sorted(pair))] += 1

# Exibe as interações mais fortes
print("Interações mais fortes entre os top 100 atores:")
for pair, count in sorted(interactions.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{pair}: {count} filmes")

# Geração dos arquivos CSV para o Flourish
# Cria o diretório para os resultados, se não existir
results_dir = "results/q1"
os.makedirs(results_dir, exist_ok=True)

# Atualiza os caminhos dos arquivos CSV
links_file = os.path.join(results_dir, "links.csv")
points_file = os.path.join(results_dir, "points.csv")

# Cria o arquivo links.csv
with open(links_file, 'w') as f:
    f.write("Source,Target,Movies_Count\n")
    for (source, target), count in interactions.items():
        f.write(f"{source},{target},{count}\n")

# Certifica-se de que actor_groups é definido corretamente antes de ser usado
actor_countries = compute_actor_countries(data)

# Atualiza o arquivo points.csv com os grupos corretos
print("Atualizando o arquivo points.csv com os grupos dos atores...")
with open(points_file, 'w') as f:
    f.write("Actor,Group,Movies_Count\n")
    for actor, count in top_actors:
        group = actor_countries.get(actor, "S/P")  # Default para "S/P" se o ator não tiver dados
        f.write(f"{actor},{group},{count}\n")

# Resumo e validação
print("\nResumo do processamento:")
print(f"Número total de atores únicos: {len(actor_movie_count)}")
print(f"Número de atores selecionados (top {TOP_N}): {len(top_actors)}")
print(f"Número total de interações registradas: {len(interactions)}")
print(f"Arquivos gerados:\n- {links_file}\n- {points_file}")
