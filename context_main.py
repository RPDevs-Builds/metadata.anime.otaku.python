import os
import sys
import xbmc
import xbmcgui
from pathlib import Path
import otaku_renamer

def main():
    # Get the selected folder path
    target_path = xbmc.getInfoLabel('ListItem.FolderPath') or xbmc.getInfoLabel('ListItem.FileNameAndPath')
    
    if not target_path:
        xbmcgui.Dialog().ok("Otaku Renamer", "No folder selected.")
        return
        
    if target_path.startswith('file://'):
        target_path = target_path[7:]
        
    # Clean up trailing slashes
    target_path = target_path.rstrip('\\/')
    
    path = Path(target_path)
    if not path.exists():
        xbmcgui.Dialog().ok("Otaku Renamer", f"Path does not exist:\n{target_path}")
        return

    dialog = xbmcgui.Dialog()
    
    # Confirm execution
    confirm = dialog.yesno(
        "Otaku Anime Renamer",
        f"Are you sure you want to mass-rename the episodes in:\n[B]{target_path}[/B]\n\nThis will apply S01E01 formatting using the Otaku Database and CANNOT be undone."
    )
    
    if not confirm:
        return
        
    # Show progress dialog
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Otaku Anime Renamer', 'Analyzing directories...')
    pDialog.update(10)
    
    try:
        # Determine if this is a single show directory or a parent library directory
        # Check if there are any video files in the root of the target directory
        has_videos = any(f.suffix.lower() in ['.mkv', '.mp4', '.avi'] for f in path.iterdir() if f.is_file())
        
        if has_videos:
            pDialog.update(30, f"Processing show directory: {path.name}")
            otaku_renamer.process_directory(path, dry_run=False)
        else:
            # It's a parent library folder containing multiple show directories
            subdirs = [d for d in path.iterdir() if d.is_dir()]
            total_dirs = len(subdirs)
            
            if total_dirs == 0:
                pDialog.close()
                dialog.ok("Otaku Renamer", "No directories or video files found to process.")
                return
                
            for idx, subdir in enumerate(subdirs):
                percent = int(30 + (idx / total_dirs) * 60)
                pDialog.update(percent, f"Processing ({idx+1}/{total_dirs}): {subdir.name}")
                otaku_renamer.process_directory(subdir, dry_run=False)
                
        pDialog.update(100, 'Renaming complete!')
        xbmc.sleep(1000)
        dialog.ok("Otaku Renamer", "Renaming complete!\n\nIf any files were skipped, check the Kodi Log for details. Please re-scan this folder to add it to your library.")
    except Exception as e:
        dialog.ok("Otaku Renamer Error", f"An error occurred:\n{str(e)}")
    finally:
        pDialog.close()

if __name__ == '__main__':
    main()
