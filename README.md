# OpenICU.debug-mimic-iv-meds-etl

## Overview

This repository contains a debug and extension setup for the **MIMIC-IV → MEDS → OpenICU pipeline**.

It includes:
- Execution commands for the MEDS pipeline
- A patching mechanism for modified library code
- Documentation of pipeline stages and intermediate steps

---

## Patches

The `patches/` folder contains **modified copies of selected Python library files** (e.g., from MEDS, OpenICU, etc.).

### Purpose

The development environment (devcontainer) **reinitializes dependencies**, which:
- overwrites installed libraries
- removes any manual modifications

To persist changes:
- modified files are stored in `patches/`
- they are reapplied automatically via `/patches/main.ipynb`

### Workflow

1. Modify library files locally  
2. Copy them into `patches/`  
3. Adjust as needed  
4. Run `/patches/main.ipynb` to overwrite `.venv/lib/...`  

---

## Commands

### First-time run (with download)

```bash
MEDS_extract-MIMIC_IV root_output_dir=output do_demo=True do_download=True do_overwrite=True
```

```bash
MEDS_extract-MIMIC_IV root_output_dir=output do_demo=True do_download=False do_overwrite=True
```

## Pipeline Stages

The MEDS pipeline consists of multiple transformation stages:

### 1. Pre-MEDS (Extraction Phase)
Initial preprocessing of raw MIMIC-IV data.

### 2. Sharding
- Splits large datasets into smaller partitions  
- Improves scalability and parallel processing  

### 3. Split and Shard Subjects
- Splits patients into:
  - training  
  - tuning  
  - held-out  
- Each split is sharded independently  

### 4. Convert to Sharded Events
- Converts raw data into MEDS-compatible event format  
- Output remains sharded  

### 5. Merge to MEDS Cohort
- Combines event shards into a structured cohort  
- Still separated by data split (train/tuning/held-out)  

### 6. Extract Code Metadata
- Extracts metadata for all codes used in the dataset  
- Produces metadata tables  

### 7. Finalize MEDS Metadata
- Merges metadata across splits  
- Produces unified metadata representation  

### 8. Finalize MEDS Data
- Final processing of cohort data  
- Ensures consistency and correct typing  