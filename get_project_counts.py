
import pandas as pd
import networkx as nx
from pathlib import Path

# Project folder
BASE_DIR = Path(__file__).resolve().parent

# CSV file paths
DATA_PATH = BASE_DIR / "dataset" / "cleaned" / "blood_banks_cleaned.csv"
NODES_PATH = BASE_DIR / "results" / "bloodlink_network_nodes.csv"
EDGES_PATH = BASE_DIR / "results" / "bloodlink_network_edges.csv"

# Load CSV files
data = pd.read_csv(DATA_PATH)
nodes = pd.read_csv(NODES_PATH)
edges = pd.read_csv(EDGES_PATH)

# Clean IDs so they match the app's graph construction
nodes["bank_id"] = nodes["bank_id"].fillna("").astype(str).str.strip()
edges["source"] = edges["source"].astype(str).str.strip()
edges["target"] = edges["target"].astype(str).str.strip()

# Remove duplicate or empty node IDs
nodes = nodes[nodes["bank_id"] != ""].drop_duplicates(
    subset="bank_id"
)

# Build the graph in the same way as the application
graph = nx.Graph()

for _, row in nodes.iterrows():
    graph.add_node(row["bank_id"])

for _, row in edges.iterrows():
    if row["source"] in graph and row["target"] in graph:
        graph.add_edge(row["source"], row["target"])

# Directory statistics
total_banks = len(data)

total_states = (
    data["state"].fillna("").astype(str).str.strip()
    .replace("", pd.NA).nunique()
)

total_districts = (
    data["district"].fillna("").astype(str).str.strip()
    .replace("", pd.NA).nunique()
)

if {"lat", "lon"}.issubset(data.columns):
    valid_coordinates = (
        pd.to_numeric(data["lat"], errors="coerce").notna()
        & pd.to_numeric(data["lon"], errors="coerce").notna()
    )
    geocoded_records = int(valid_coordinates.sum())
else:
    geocoded_records = 0

# Network statistics
network_nodes = graph.number_of_nodes()
network_edges = graph.number_of_edges()
connected_components = nx.number_connected_components(graph)
isolated_banks = len(list(nx.isolates(graph)))

# Display results
print("\n========== BLOODLINK PROJECT STATISTICS ==========")
print(f"Total directory records       : {total_banks}")
print(f"States / UTs                  : {total_states}")
print(f"Districts                     : {total_districts}")
print(f"Records with coordinates     : {geocoded_records}")

print("\n========== NETWORK STATISTICS ==========")
print(f"Network nodes                 : {network_nodes}")
print(f"Network edges                 : {network_edges}")
print(f"Connected components          : {connected_components}")
print(f"Isolated banks                 : {isolated_banks}")
print("==================================================")
