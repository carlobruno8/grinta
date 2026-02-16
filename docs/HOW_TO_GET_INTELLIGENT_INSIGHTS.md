# How to Get More Intelligent Insights from Grinta

## The Problem You Had

Your reasoning output was **valid but boring**:
- "Team A had 55% possession" ← You already knew this
- "Team B took 12 shots" ← Basic stat
- "Average position was 58.2" ← Not actionable

What you wanted:
- "Liverpool pressured Man City's uncomfortable right back" ← Tactical insight!
- "Arsenal exploited the left flank where City's fullback was isolated" ← Real analysis!

## What Was Fixed

### Two Strategic Improvements

#### 1. Enhanced System Prompt (Immediate Impact)
The LLM now understands it should:
- **Extract tactical insights**, not just report stats
- **Compare and contrast** metrics to find patterns
- **Identify mismatches** (e.g., high possession but low shots)
- **Reveal vulnerabilities** (e.g., one flank targeted more than others)

**Result**: Even with the same metrics, outputs are now more insightful.

#### 2. New Spatial Intelligence Metrics (Unlock Tactical Analysis)
Added three categories of tactical metrics:

**A. Spatial Attack Distribution**
- Which flank did teams attack through? (left/center/right %)
- Where was attacking action concentrated?

**Example insight**: "Liverpool targeted the right flank with 68% of attacks, overwhelming City's left back"

**B. Defensive Positioning**
- High press actions (defending in opponent's half)
- Low block actions (defending deep in own third)

**Example insight**: "Arsenal dropped into a low block in the final 10 minutes, inviting City's pressure"

**C. Passing Patterns**
- How wide was passing? (pass width spread)
- How cautious? (backward passes %)

**Example insight**: "City played wider (spread: 22) and more progressive (25% backward passes) vs Liverpool's narrow, cautious approach (spread: 12, 42% backward)"

---

## How to Test the Improvements

### Option 1: Quick Test (No API Required)
```bash
# Test that spatial metrics work correctly
python3 test_spatial.py
```

**Expected output**:
```
✅ Team A attack distribution:
   Left: 13.6%
   Center: 40.9%
   Right: 45.5%

✅ Team A defensive positioning:
   High press actions: 8
   Low block actions: 3

✅ All spatial analysis tests passed!
```

### Option 2: Full Test with Real Match Data
```bash
# 1. Make sure you have API key
export GOOGLE_API_KEY="your-google-api-key"

# 2. Make sure you have processed match data (run ingestion if not)
# export GRINTA_COMPETITION_ID=16
# export GRINTA_SEASON_ID=4
# python3 -m ingestion

# 3. Run reasoning demo
python3 scripts/demo_reasoning.py
```

**What to look for in output**:
- ❌ **Old boring**: "Team A had 55% possession"
- ✅ **New insightful**: "Team A controlled possession (55%) but struggled to convert it to shots (only 6 vs 12 for opponent), revealing inefficient possession against a compact defense"

---

## Example Questions That Now Give Better Insights

### Question 1: "Why did [Team] struggle in the second half?"

**Before (boring)**:
"Team A had 48% possession in the second half compared to 52% for Team B."

**After (insightful)**:
"Team A's possession dropped to 48% and they became more direct (45% backward passes vs 35% first half). Spatially, Team B targeted Team A's right flank (68% of attacks) where defensive actions concentrated (22 of 30), creating a tactical mismatch."

### Question 2: "How did [Team] create their goal?"

**Before (boring)**:
"Team A took 4 shots in the final third."

**After (insightful)**:
"Team A shifted from balanced attacks (33% each flank) to heavily favoring the right (65% of attacks in final 15min), exploiting Team B's tired left back. This spatial overload created 4 shots from that zone, including the goal."

### Question 3: "What were the tactical differences between the teams?"

**Before (boring)**:
"Team A had 58% possession, Team B had 42%."

**After (insightful)**:
"Team A controlled possession (58%) but played narrow (spread: 12.5) and cautious (42% backward passes), while Team B was direct and expansive (spread: 22, 25% backward). Despite less possession, Team B's efficiency (12 shots vs 6) reveals they bypassed Team A's pressure with direct attacking."

---

## What Changed in the Codebase

### Files Modified
1. **`reasoning/prompts.py`** - Enhanced system prompt with tactical analysis guidelines
2. **`reasoning/input_schema.py`** - Added 8 new spatial metric fields
3. **`reasoning/builder.py`** - Integrated spatial metric computation
4. **`features/__init__.py`** - Exported spatial module

### Files Created
1. **`features/spatial.py`** - New spatial analysis module with 3 analysis functions
2. **`test_spatial.py`** - Test suite for spatial metrics
3. **`TACTICAL_INTELLIGENCE_PLAN.md`** - Full roadmap (3 tiers of improvements)
4. **`TACTICAL_INTELLIGENCE_SUMMARY.md`** - Complete technical summary
5. **`HOW_TO_GET_INTELLIGENT_INSIGHTS.md`** - This guide

### New Metrics Available

When you call `generate_explanation()`, each team now has these additional metrics:

```python
# Spatial attack distribution
left_flank_attacks_pct: float      # 0-1 (% of attacks down left)
center_attacks_pct: float          # 0-1 (% through center)
right_flank_attacks_pct: float     # 0-1 (% down right)
attacking_half_actions: int        # Count of attacking actions

# Defensive positioning
high_press_actions: int            # Defensive actions in opponent's half
low_block_actions: int             # Defensive actions in own third

# Passing patterns
pass_width_spread: float           # Std dev of pass y-coords (higher = wider)
back_passes_pct: float             # 0-1 (% of passes backward)
```

---

## How the LLM Uses These Metrics

The enhanced system prompt guides the LLM to:

### 1. Identify Spatial Patterns
**Metrics**: `left/center/right_flank_attacks_pct`

**LLM reasoning**:
- "If one flank has 65% while other has 15% → targeted approach"
- "If all three are ~33% → balanced attack"
- "If distribution changes between periods → tactical adjustment"

### 2. Detect Tactical Mismatches
**Metrics**: `possession_share`, `shot_count`, `attacking_half_actions`

**LLM reasoning**:
- "High possession but low shots → struggled to break down defense"
- "Low possession but high shots → efficient counter-attacking"
- "Many attacking actions but few shots → poor final ball"

### 3. Reveal Defensive Approach
**Metrics**: `high_press_actions`, `low_block_actions`, `avg_position_x`

**LLM reasoning**:
- "High press (20 actions) + high avg_position (62) → aggressive pressing"
- "Low block (35 actions) + low avg_position (42) → defensive posture"
- "Shift from high to low between periods → tactical adjustment"

### 4. Analyze Playing Style
**Metrics**: `pass_width_spread`, `back_passes_pct`

**LLM reasoning**:
- "High spread (22) → playing wide, stretching defense"
- "Low spread (12) → playing narrow, central focus"
- "High backward % (45%) → cautious, patient build-up"
- "Low backward % (20%) → direct, progressive style"

---

## What's Still Missing (Future Improvements)

This implementation covers **Tier 1 & 2** from the tactical intelligence plan.

**Not yet implemented** (but planned):

### Tier 3: Advanced Pattern Detection
- **Counter-attack detection**: Sequences from recovery to shot in <5 seconds
- **Pressing sequences**: Coordinated pressing actions
- **Build-up patterns**: Short vs long, left vs right starts
- **Player-level targeting**: Which defender was targeted most?

See `TACTICAL_INTELLIGENCE_PLAN.md` for full roadmap.

---

## Troubleshooting

### "I'm still getting boring outputs"

**Check 1**: Make sure you're using the updated code
```bash
# Verify spatial module exists
ls features/spatial.py

# Verify it imports correctly
python3 -c "from features import spatial; print('✅ Spatial module loaded')"
```

**Check 2**: Verify spatial metrics are being computed
```bash
# Run test
python3 test_spatial.py

# Should see:
# ✅ Team A attack distribution:
#    Left: 13.6%
#    Center: 40.9%
#    Right: 45.5%
```

**Check 3**: Try upgrading to a more capable model
```bash
# Current: gemini-1.5-flash (fast but less sophisticated)
export GRINTA_LLM_MODEL="gemini-1.5-pro"

# Re-run explanation
python3 scripts/demo_reasoning.py
```

### "Spatial metrics are None/null"

This means the event data doesn't have enough information. Check:

```python
from features.reader import load_match_events
events = load_match_events(your_match_id)

# Check if location data exists
print(events[['x', 'y', 'type_name']].head())

# Make sure there are passes/shots with coordinates
print(events[events['type_name'] == 'Pass'][['x', 'y']].notna().sum())
```

### "Import error: No module named 'google.generativeai'"

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Next Steps

### 1. Test with Your Matches
Run the demo with your competition/season:
```bash
export GRINTA_COMPETITION_ID=16   # Your competition
export GRINTA_SEASON_ID=4          # Your season
python3 -m ingestion               # Get data
python3 scripts/demo_reasoning.py  # Test insights
```

### 2. Compare Before/After
Ask the same question multiple times and compare:
- Which response is more insightful?
- Does it reveal WHY something happened?
- Does it identify tactical patterns?

### 3. Iterate on Prompt
If outputs aren't insightful enough, edit `reasoning/prompts.py`:
- Add more tactical interpretation examples
- Emphasize specific patterns you care about
- Add domain knowledge about your league/teams

### 4. Add More Metrics (Optional)
If you want even more intelligence, implement Tier 3 features:
- See `TACTICAL_INTELLIGENCE_PLAN.md` for ideas
- Start with counter-attack detection (high impact)
- Or tempo analysis (passes per minute)

---

## Summary

You now have:
- ✅ **Enhanced prompting** that encourages tactical thinking
- ✅ **Spatial intelligence** metrics (attack distribution, defensive positioning, passing patterns)
- ✅ **Tactical insights** instead of boring stat reporting
- ✅ **Evidence-based analysis** (no hallucinations)

Your reasoning module went from **reporting what happened** to **explaining WHY it happened** 🎯⚽

---

## Questions?

- Read the full technical summary: `TACTICAL_INTELLIGENCE_SUMMARY.md`
- See the complete roadmap: `TACTICAL_INTELLIGENCE_PLAN.md`
- Check the reasoning module docs: `reasoning/contract.md`
