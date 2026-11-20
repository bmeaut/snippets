import sys
import re

def natural_sort_key(s):
    """Provides natural alphanumeric sorting (e.g., Clip 2 before Clip 10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

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

    clip_data = []
    items_to_delete = []

    for item in items:
        mp_item = item.GetMediaPoolItem()
        if mp_item:
            # Capture source and timeline start positions
            clip_data.append({
                'name': item.GetName(),
                'mp_item': mp_item,
                'startFrame': item.GetSourceStartFrame(),
                'endFrame': item.GetSourceEndFrame(),
                'timelineStart': item.GetStart()
            })

            # Add main video clip to deletion list if not already present
            if item not in items_to_delete:
                items_to_delete.append(item)

            # Retrieve and add all linked items (e.g., linked audio clips)
            linked_items = item.GetLinkedItems()
            if linked_items:
                for linked in linked_items:
                    if linked not in items_to_delete:
                        items_to_delete.append(linked)

    if not clip_data:
        print("No valid media items retrieved.")
        return

    # Find the timeline frame where the earliest original clip started
    first_start_frame = min(c['timelineStart'] for c in clip_data)

    # Sort clips in natural alphanumeric order by name
    sorted_clips = sorted(clip_data, key=lambda c: natural_sort_key(c['name']))

    # Delete original timeline clips including all linked audio tracks
    timeline.DeleteClips(items_to_delete, False)

    # Build payload using 'recordFrame' to insert starting at the original frame position
    current_record_frame = first_start_frame
    append_payload = []

    for c in sorted_clips:
        duration = c['endFrame'] - c['startFrame']
        append_payload.append({
            'mediaPoolItem': c['mp_item'],
            'startFrame': c['startFrame'],
            'endFrame': c['endFrame'],
            'recordFrame': current_record_frame
        })
        current_record_frame += duration

    # Re-insert sorted clips precisely at the original start timecode
    media_pool.AppendToTimeline(append_payload)
    print(f"Successfully sorted {len(sorted_clips)} clips with audio starting at timeline frame {first_start_frame}.")

if __name__ == "__main__":
    main()