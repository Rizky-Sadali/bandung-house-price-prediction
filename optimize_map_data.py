import os
import glob
import zipfile

def optimize_map_data():
    raw_dir = os.path.join("data", "raw")
    
    # 1. Identify the Target Files (ID3 - Java)
    target_pattern = "idn_admbnda_adm4_ID3_bps_20200401.*"
    target_files = glob.glob(os.path.join(raw_dir, target_pattern))
    
    if not target_files:
        print("❌ Critical Error: Could not find the ID3 (Java) shapefiles!")
        return

    print(f"Found {len(target_files)} files for Java (Bandung).")

    # 2. Zip ONLY the Target Files
    zip_name = os.path.join(raw_dir, "bandung_map_data.zip")
    print(f"Compressing Java map data into {zip_name}...")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in target_files:
            zipf.write(file, os.path.basename(file))
            
    zip_size = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"✅ Zip created. Size: {zip_size:.2f} MB")
    
    if zip_size > 100:
        print("⚠️ WARNING: Still over 100MB. You might need to split it.")
    else:
        print("✅ PERFECT! This fits on GitHub.")

    # 3. Delete ALL shapefiles (The ones we zipped AND the unused ones)
    # We look for anything starting with 'idn_' and ending in typical shapefile extensions
    all_map_files = glob.glob(os.path.join(raw_dir, "idn_admbnda*"))
    
    print(f"Cleaning up {len(all_map_files)} raw files...")
    for file in all_map_files:
        # Don't delete our new zip if it matches the pattern (it shouldn't, but safety first)
        if file != zip_name:
            os.remove(file)
            
    # Remove previous attempts if they exist
    old_zips = [
        os.path.join(raw_dir, "indonesia_shapefiles.zip"),
        os.path.join(raw_dir, "indonesia_shapefiles.zip.part001"),
        os.path.join(raw_dir, "indonesia_shapefiles.zip.part002")
    ]
    for z in old_zips:
        if os.path.exists(z):
            os.remove(z)
            print(f"Removed old zip artifact: {os.path.basename(z)}")

    print("✅ Cleanup complete. Your data folder is optimized.")

if __name__ == "__main__":
    optimize_map_data()