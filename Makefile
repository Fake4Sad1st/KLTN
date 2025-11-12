PY := python3
GEN := $(PWD)/graph_gen/gen.py

.PHONY: path cycle grid complete star kbip tree gnp trisnake cnsnake c4snake c6snake book friendship ladder bintree

path:
	$(PY) $(GEN) path --n $(n) --output $(out)

cycle:
	$(PY) $(GEN) cycle --n $(n) --output $(out)

grid:
	$(PY) $(GEN) grid --rows $(rows) --cols $(cols) --output $(out)

complete:
	$(PY) $(GEN) complete --n $(n) --output $(out)

star:
	$(PY) $(GEN) star --n $(n) --center $(center) --output $(out)

kbip:
	$(PY) $(GEN) kbip --n1 $(n1) --n2 $(n2) --output $(out)

tree:
	$(PY) $(GEN) tree --n $(n) --seed $(seed) --output $(out)

gnp:
	$(PY) $(GEN) gnp --n $(n) --p $(p) --seed $(seed) --output $(out)

trisnake:
	$(PY) $(GEN) trisnake --k $(k) --output $(out)

cnsnake:
	$(PY) $(GEN) cnsnake --k $(k) --n $(n) --output $(out)

c4snake:
	$(PY) $(GEN) c4snake --k $(k) --output $(out)

c6snake:
	$(PY) $(GEN) c6snake --k $(k) --output $(out)

book:
	$(PY) $(GEN) book --k $(k) --n 2 --output $(out)

friendship:
	$(PY) $(GEN) friendship --k $(k) --output $(out)

ladder:
	$(PY) $(GEN) ladder --k $(k) --output $(out)

bintree:
	$(PY) $(GEN) bintree --k $(k) --output $(out)

# Graph k-labeling
.PHONY: label

label:
	$(PY) $(PWD)/src/graph_k_labeling.py --algo $(algo) --input $(input)