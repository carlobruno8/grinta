# Git Commit Guide for Cursor

This guide walks you through making your first commit in Cursor.

## Step 1: Review What Will Be Committed

First, let's see what files have changed:

```bash
git status
```

You should see:
- **Modified**: `README.md` (updated with project info)
- **New files**: `.gitignore`, `TESTING.md`, `docs/`, `ingestion/`, `tests/`, `requirements.txt`
- **Ignored**: Data files (`data/raw/*.json`, `data/processed/*.parquet`) should NOT appear

## Step 2: Stage Files for Commit

In Cursor, you can stage files in two ways:

### Option A: Stage All Changes (Recommended for this commit)
1. Open the **Source Control** panel (click the branch icon in the left sidebar, or `Cmd+Shift+G`)
2. You'll see all changed files listed
3. Click the **"+"** button next to "Changes" to stage all files
   - Or click the **"+"** next to individual files to stage them one by one

### Option B: Use Terminal (Alternative)
```bash
# Stage all changes
git add .

# Or stage specific files
git add README.md .gitignore TESTING.md docs/ ingestion/ tests/ requirements.txt
```

## Step 3: Verify What's Staged

Check what will be committed:

```bash
git status
```

You should see files under "Changes to be committed" (green).

**Important**: Make sure `data/raw/*.json` and `data/processed/*.parquet` are NOT listed (they should be ignored).

## Step 4: Write Commit Message

In Cursor's Source Control panel:
1. Type your commit message in the text box at the top
2. Use a clear, descriptive message

**Recommended commit message:**
```
feat: Add StatsBomb ingestion pipeline with full test suite

- Implement modular ingestion pipeline (loaders, storage, normalizers)
- Add comprehensive test suite (unit, component, integration)
- Add documentation (README, TESTING, INSTALL guides)
- Configure .gitignore for data files and test artifacts
- Support StatsBomb Open Data with configurable competition/season
```

Or shorter version:
```
feat: Add StatsBomb ingestion pipeline

Complete ingestion pipeline with loaders, storage, normalizers, and full test suite.
```

## Step 5: Commit

1. Click the **"✓ Commit"** button (or press `Cmd+Enter`)
2. If prompted, confirm the commit

## Step 6: Push to GitHub (Optional)

If you want to push to GitHub:

1. Click the **"..."** menu in Source Control panel
2. Select **"Push"** (or **"Push to..."** if you need to set upstream)
3. Or use terminal: `git push origin main`

## What Gets Committed

✅ **Will be committed:**
- All code (`ingestion/`, `tests/`)
- Documentation (`README.md`, `TESTING.md`, `docs/`)
- Configuration (`.gitignore`, `requirements.txt`)
- Empty data directories with `.gitkeep` files

❌ **Will NOT be committed** (ignored):
- Actual data files (`data/raw/*.json`, `data/processed/*.parquet`)
- Python cache (`__pycache__/`)
- Environment files (`.env`)
- Test artifacts (`.pytest_cache/`)

## Troubleshooting

### "Nothing to commit"
- Make sure you've staged files (clicked the "+" button)
- Check `git status` to see if files are under "Changes to be committed"

### "Data files showing up"
- Check `.gitignore` is in the root directory
- Verify patterns match: `data/raw/*.json` and `data/processed/*.parquet`
- Run `git check-ignore data/raw/events_22912.json` to verify it's ignored

### "Commit button grayed out"
- Make sure you've typed a commit message
- Ensure files are staged (green in Source Control panel)

## Next Steps After Commit

1. **Verify commit**: `git log` to see your commit
2. **Push to GitHub**: Share your work
3. **Continue development**: Move to next phase (features/, reasoning/, app/)
