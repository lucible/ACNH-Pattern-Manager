import os
import struct
import argparse
from typing import List

def extract_utf16_string(data: bytes, offset: int, max_length: int) -> str:
    """Extract a UTF-16 string from binary data, stopping at null character"""
    result: str = ""
    for i in range(0, max_length, 2):
        if offset + i + 1 >= len(data):
            break
        
        # Get the character code (using little-endian byte order)
        char_code: int = struct.unpack('<H', data[offset+i:offset+i+2])[0]
        
        # Stop at null terminator
        if char_code == 0:
            break
        
        result += chr(char_code)
    
    return result.strip()

def rename_nhd_file(file_path: str, dry_run: bool = False) -> bool:
    """Process an NHD file and rename it using town ID, player ID, and pattern name"""
    try:
        with open(file_path, 'rb') as f:
            data: bytes = f.read()
        
        # Extract data from the NHD file
        pattern_name: str = extract_utf16_string(data, 0x10, 40)
        town_id: int = struct.unpack('<I', data[0x38:0x3C])[0]
        player_id: int = struct.unpack('<I', data[0x54:0x58])[0]
        
        # Create the new filename
        base_name: str = f"{town_id}-{player_id}_{pattern_name}"
        
        # Remove invalid characters from filename
        valid_name: str = "".join(c for c in base_name if c not in '\\/:*?"<>|')
        
        # Get directory and extension
        directory: str = os.path.dirname(file_path)
        ext: str = os.path.splitext(file_path)[1]
        
        # Create new filepath
        new_filepath: str = os.path.join(directory, valid_name + ext)
        
        # Handle duplicate filenames
        counter: int = 1
        while os.path.exists(new_filepath):
            new_name: str = f"{valid_name}_{counter}{ext}"
            new_filepath = os.path.join(directory, new_name)
            counter += 1
        
        # Rename the file (or just report what would happen in dry run mode)
        if dry_run:
            print(f"Would rename: {os.path.basename(file_path)} -> {os.path.basename(new_filepath)}")
        else:
            os.rename(file_path, new_filepath)
            print(f"Renamed: {os.path.basename(file_path)} -> {os.path.basename(new_filepath)}")
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main() -> None:
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Rename Animal Crossing NHD pattern files based on their metadata')
    parser.add_argument('path', help='Path to an NHD file or directory containing NHD files')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Show what would be renamed without making changes')
    
    args = parser.parse_args()
    
    path: str = args.path
    dry_run: bool = args.dry_run
    
    if dry_run:
        print("Running in DRY RUN mode - no files will be renamed")
    
    if os.path.isfile(path) and path.lower().endswith('.nhd'):
        rename_nhd_file(path, dry_run)
    
    elif os.path.isdir(path):
        nhd_files: List[str] = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.nhd')]
        
        if not nhd_files:
            print(f"No NHD files found in {path}")
            return
        
        success_count: int = 0
        for file_path in nhd_files:
            if rename_nhd_file(file_path, dry_run):
                success_count += 1
        
        print(f"Processed {success_count} of {len(nhd_files)} NHD files")
    
    else:
        print(f"Invalid path or not an NHD file: {path}")

if __name__ == "__main__":
    main()