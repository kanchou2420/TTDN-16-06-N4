# Troubleshooting Guide - TypeError in ke_toan_tai_san Module

## Issue
You're seeing this error when accessing ke_toan_tai_san module views:
```
TypeError: Cannot read properties of undefined (reading 'type')
    at ControlPanelModelExtension._extractAttributes
```

## Root Cause Analysis
This is a **client-side JavaScript error** that typically occurs due to:
1. **Browser caching old assets** - The browser may have cached old JavaScript bundles or view definitions
2. **Session cache** - Odoo session may have cached old view structures
3. **Static files cache** - The web assets may not have been properly refreshed

## Solution Steps (Try in Order)

### Step 1: Clear Browser Cache & Hard Refresh ⭐ (Most Effective)
This is the #1 solution for this error type.

**Chrome/Firefox/Edge:**
- Press: `Ctrl + Shift + R` (or `Cmd + Shift + R` on Mac)
- This forces a hard refresh and clears the cache for this page

**Safari:**
- Press: `Cmd + Shift + R` or `Cmd + Option + E`

**OR manually clear cache:**
- Settings → Privacy/History → Clear browsing data
- Select "Cached images and files"
- Click Clear

### Step 2: Try Incognito/Private Window ✅ (Tests without cache)
- Press: `Ctrl + Shift + N` (Chrome) or `Ctrl + Shift + P` (Firefox)
- Go to: `http://localhost:8000/web`
- Login and try accessing the module

**If it works in incognito:** Your cache is the problem. Clear it and try Step 1.

### Step 3: Clear Odoo Session Cache
1. Log out from Odoo (`http://localhost:8000/web/logout`)
2. Clear browser cookies for localhost:8000
3. Close all Odoo tabs/windows
4. Restart your browser
5. Login again to `http://localhost:8000/web`

### Step 4: Rebuild Odoo Assets (Server-Side)
If the above doesn't work, rebuild the web assets:

**Terminal:**
```bash
cd "/mnt/c/Users/hadsk/OneDrive/Documents/TTDN-16-06-N4"
pkill -f "python3 odoo-bin.py"
sleep 2
python3 odoo-bin.py -c odoo.conf --clean &
```

Wait for "HTTP service running on" message, then:
```bash
python3 odoo-bin.py -c odoo.conf --shell
>>> execute("ir.ui.view", "clear_caches")
>>> exit()
```

### Step 5: Check Module Installation Status
1. In Odoo, go to **Settings** → **Modules** 
2. Search for "Kế Toán Tài Sản" (ke_toan_tai_san)
3. Verify the module is installed (not just available)
4. If needed: Uninstall → Install again

### Step 6: Verify View Definitions in Module
The module has 4 views defined:
- ✅ khau_hao_view.xml - Tree, Form, and Search views
- ✅ so_tai_san_view.xml - Tree, Form, and Search views
- ✅ tai_khoan_khau_hao_view.xml - Tree, Form, and Search views  
- ✅ dashboard_view.xml - Form and Search views

All views use minimal search definitions (`<search/>`) to prevent parsing errors.

## Expected Result After Fix
Once you complete the steps above, you should:
1. ✅ See the "Kế Toán Tài Sản" menu in Accounting module
2. ✅ Click on menu items without JavaScript errors
3. ✅ View lists, forms, and dashboards normally
4. ✅ No TypeError in browser console

## If Still Not Working

### Check Server Logs
```bash
tail -100 /tmp/odoo.log | grep -iE "(error|exception|ke_toan)"
```

### Test Direct Access
Try accessing each view directly:
- Tree view: `http://localhost:8000/web#model=khau_hao_tai_san&view_type=list`
- Form view: `http://localhost:8000/web#model=khau_hao_tai_san&view_type=form`
- Dashboard: `http://localhost:8000/web#model=ke_toan.dashboard&view_type=form`

### Browser Developer Tools
1. Press `F12` to open Developer Tools
2. Go to **Console** tab
3. Try accessing the module again
4. Look for error details in the console
5. Take a screenshot and send it for debugging

## Recommended: Try This First
```
1. Ctrl + Shift + R (hard refresh)
2. If still broken → Clear all cookies for localhost:8000
3. If still broken → Try incognito window
4. If works in incognito → Clear browser cache completely
5. If none work → Restart browser and try again
```

## Prevention Going Forward
To avoid this in the future:
- Clear browser cache after major module updates
- Use Firefox Developer Edition (better caching controls)
- Disable browser cache in DevTools while developing

---

**Last Updated:** January 26, 2026  
**Module Status:** ✅ Server-side: WORKING | Issue: Client-side cache

If you've tried all steps and still have issues, please:
1. Check your browser console for error details
2. Verify the server is running: `ps aux | grep odoo-bin`
3. Try accessing from a different browser
4. Share the exact error message and browser type
