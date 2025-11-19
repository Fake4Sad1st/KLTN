PY := python3
GEN := $(PWD)/graph_gen/gen.py

.PHONY: path cycle grid complete star kbip tree gnp trisnake cnsnake c4snake c6snake book friendship ladder bintree

path:
	$(PY) $(GEN) path --n $(n) --output $(out)

cycle:
	$(PY) $(GEN) cycle --n $(n) --output $(out)

ladder:
	$(PY) $(GEN) ladder --k $(k) --output $(out)

book:
	$(PY) $(GEN) book --k $(k) --n 2 --output $(out)

friendship:
	$(PY) $(GEN) friendship --k $(k) --output $(out)

trisnake:
	$(PY) $(GEN) trisnake --k $(k) --output $(out)

c4snake:
	$(PY) $(GEN) c4snake --k $(k) --output $(out)

c6snake:
	$(PY) $(GEN) c6snake --k $(k) --output $(out)

bintree:
	$(PY) $(GEN) bintree --k $(k) --output $(out)

# Graph k-labeling
.PHONY: label

label:
	$(PY) $(PWD)/src/graph_k_labeling.py --algo $(algo) --input $(input) --delta $(delta)