# ---------- Standard-Ziel ----------
.PHONY: all
all: lva abs          # führt beide Teilziele nacheinander aus

# ---------- LVA-Daten laden ----------
# ---------- LVA-Daten laden ----------
lva:
	jupyter nbconvert --to notebook --execute notebooks/bfs_daten/02a_clean_lva.ipynb --output-dir tmp
	jupyter nbconvert --to notebook --execute notebooks/bfs_daten/04a_load_facts_lva.ipynb --output-dir tmp



# ---------- Abschlussquoten laden ----------
abs:
	jupyter nbconvert --to notebook --execute notebooks/bfs_daten/02b_clean_abschluss.ipynb --output-dir tmp
	jupyter nbconvert --to notebook --execute notebooks/bfs_daten/04b_load_facts_abschluss.ipynb --output-dir tmp


