# file-size-editor

### example run:

```bash
python ./main.py sample_200mb.json .
```

this will take the sample_200mb.json file, and write the 40MB chunked files into the current directory.
ex: chunk_001.json

---

### further customized execution example:

```bash
python ./main.py sample_200mb.json . --prefix test --max-size 20
```

this will take the sample_200mb.json file, and write 20MB chunked files into the current directory.
ex: test_001.json
