# UI Troubleshooting Guide

## If UI Changes Don't Appear

The UI changes may not be visible due to browser caching. Here's how to fix it:

### Option 1: Hard Refresh (Recommended)
1. **Chrome/Edge**: Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. **Firefox**: Press `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
3. **Safari**: Press `Cmd + Option + R`

### Option 2: Clear Browser Cache
1. Open browser DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Option 3: Disable Cache in DevTools
1. Open DevTools (F12)
2. Go to Network tab
3. Check "Disable cache"
4. Keep DevTools open while using ComfyUI

### Option 4: Check Console for Errors
1. Open DevTools (F12)
2. Go to Console tab
3. Look for errors starting with `[ManimTimeline]` or `[ManimDataViz]`
4. Report any errors you see

## Verifying UI is Loaded

1. Open browser DevTools (F12)
2. Go to Console tab
3. You should see messages like:
   - `[ManimTimeline] Creating timeline UI...`
   - `[ManimTimeline] Widget found, creating UI elements...`
   - `[ManimTimeline] UI created, loading timeline...`

If you don't see these messages, the UI code may not be loading.

## Timeline Node UI

The timeline node should show:
- **Time ruler** at the top (0-60s with markers)
- **Visual timeline bars** showing scene positions
- **Collapsible detail cards** below for editing scenes
- **"Add Scene" button** in the header

If you only see an empty JSON textarea, the UI didn't initialize. Check the console for errors.

## Data Visualization Node UI

The data visualization node should show:
- **Data input helper** at the top
- **Collapsible "Custom Code" section** (hidden by default)
- All other settings visible

If the custom code section is always visible and large, the UI didn't initialize. Check the console for errors.

## Force Reload Extension

If changes still don't appear:

1. Stop ComfyUI server
2. Delete browser cache for ComfyUI URL
3. Restart ComfyUI server
4. Hard refresh the page (Ctrl+Shift+R)

## Check File is Loaded

1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "index.js"
4. Reload page
5. Check if `web/index.js` is loaded
6. Click on it to see the file content
7. Verify it contains the new code (search for "ManimTimeline" or "timeline-visual")

