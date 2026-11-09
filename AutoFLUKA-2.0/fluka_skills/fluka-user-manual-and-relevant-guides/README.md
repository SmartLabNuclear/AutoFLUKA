# Optional Local FLUKA/FLAIR Reference Folder

This folder is an optional, user-managed location for local FLUKA/FLAIR manuals, lecture notes, and other reference material that the user is legally permitted to use.

## Licensing policy
- AutoFLUKA does **not** ship FLUKA/FLAIR manuals, lecture notes, extracted figures, parsed chunks, or generated knowledge-base files.
- Users are responsible for independently obtaining any FLUKA/FLAIR documentation and confirming that their use follows the applicable licenses and institutional rules.
- Do not commit or redistribute copyrighted FLUKA/FLAIR manuals, lecture slides, extracted text, extracted images, or generated JSONL/vector-cache files unless you have explicit permission.

## How AutoFLUKA uses this folder
- AutoFLUKA can optionally query local JSONL knowledge-base files here when they exist.
- If this folder is empty or missing generated KB files, AutoFLUKA should continue using its built-in skills and normal workflow rules.
- Local KB material is only a private runtime enhancement; it is not required for normal app operation.

## Expected local files
Generated KB files, when present, may use names such as:
- `01_chunks_kb.jsonl` — extracted text chunks
- `02_visuals_kb.jsonl` — extracted figures/diagrams
- `03_metadata_kb.jsonl` — per-document metadata
- `04_processed_pdfs.txt` — ingestion ledger (which source PDFs have been processed)
- `05_pipeline.log` — run log

These three JSONL files are the canonical, provider-agnostic output and should remain local to the user environment. Any other file here that doesn't match this pattern (e.g. a stray `.f` source file) is not pipeline output and is likely an unrelated leftover, safe to remove independently.

## Vector stores are derived, not canonical
A per-provider vector store folder (e.g. `gpt_vector_store/`) may also appear here. It is built from the JSONL files above by whichever chat model/embedding provider is currently initialized — switching providers (e.g. GPT to Gemini, or to a local embedding model) builds its own local vector store fresh from the same JSONLs, not from another provider's store. Only one provider's store existing at a time is normal; a missing one is simply rebuilt on demand.

## Keeping material current across multiple projects
If your reference material changes often, or you want to reuse the same corpus across several AutoFLUKA projects instead of duplicating it into every project's bundled `fluka_skills/`, place it under a directory on your host filesystem instead and point AutoFLUKA at it via the Settings "Skills directory" field (or `AUTOFLUKA_SKILLS_DIR`). On first use, ask the agent to parse it so it registers as discoverable knowledge; re-run parsing whenever the source material changes.

See `SKILL.md` in this folder for how this content is treated by AutoFLUKA's skill system.
