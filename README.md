# OpenICU.debug-mimic-iv-meds-etl

## Patches

This folder contains modified copies of the used python libraryies (more specific only the modified files) in OpenICU, MEDS, ...

These files are to be copy-pasted by the /patches/main.ipynb into the .venv/lib/... files (to be overwritten).

Reason for that is, that the devcontainer reinitalises the libraries in the environment and delets changes made by hand. That is why this patch folder is created. In this patch folder all these changes are copied in and modified before the overwrite state. 