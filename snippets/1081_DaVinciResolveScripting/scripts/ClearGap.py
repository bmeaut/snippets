import sys

def main():
    # Connect to DaVinci Resolve Scripting API
    try:
        resolve_app = resolve
    except NameError:
        import DaVinciResolveScript as dvr_script
        resolve_app = dvr_script.scriptapp("Resolve")

    if not resolve_app:
        print("Error: Could not connect to DaVinci Resolve.")
        return

    project_manager = resolve_app.GetProjectManager()
    project = project_manager.GetCurrentProject()
    if not project:
        print("Error: No open project found.")
        return

    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("Error: No active timeline found.")
        return

    media_pool = project.GetMediaPool()

    # Target Video Track 1
    track_type = "video"
    track_index = 1

    items = timeline.GetItemListInTrack(track_type, track_index)
    if not items:
        print(f"No clips found on {track_type} track {track_index}.")
        return

    # Sort clips chronologically by timeline start frame
    sorted_items = sorted(items, key=lambda x: x.GetStart())

    # Record the timeline start frame of the very first clip
    first_start_frame = sorted_items[0].GetStart()

    clip_data = []
    items_to_delete = []

    for item in sorted_items:
        mp_item = item.GetMediaPoolItem()
        if mp_item:
            clip_data.append({
                'mp_item': mp_item,
                'startFrame': item.GetSourceStartFrame(),
                'endFrame': item.GetSourceEndFrame()
            })

            # Add main video clip to deletion list
            if item not in items_to_delete:
                items_to_delete.append(item)

            # Retrieve and add all linked audio items to deletion list
            linked_items = item.GetLinkedItems()
            if linked_items:
                for linked in linked_items:
                    if linked not in items_to_delete:
                        items_to_delete.append(linked)

    if not clip_data:
        print("No valid media items found.")
        return

    # Delete original timeline clips and linked audio tracks
    timeline.DeleteClips(items_to_delete, False)

    # Build append payload omitting 'recordFrame' for subsequent items
    # Resolve will automatically append each item directly after the previous one with zero gap
    append_payload = []
    for i, c in enumerate(clip_data):
        clip_info = {
            'mediaPoolItem': c['mp_item'],
            'startFrame': c['startFrame'],
            'endFrame': c['endFrame']
        }
        if i == 0:
            clip_info['recordFrame'] = first_start_frame
            
        append_payload.append(clip_info)

    # Re-insert clips back onto timeline
    media_pool.AppendToTimeline(append_payload)
    print(f"Successfully removed all gaps across {len(clip_data)} clips on the timeline.")

if __name__ == "__main__":
    main()