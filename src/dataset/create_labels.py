import os
import json
import csv

if __name__ == "__main__":
    dir_path = "./part000"
    output_csv = "./dataset.csv"

    all_files = os.listdir(dir_path)
    
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["file_name", "lat", "lon"])
        
        for file_name in all_files:
            if file_name.lower().endswith(".json"):
                continue
            
            image_extensions = (".png")
            if file_name.lower().endswith(image_extensions):
                base_name, _ = os.path.splitext(file_name)
                
                json_file_name = base_name + ".json"
                
                if json_file_name in all_files:
                    json_path = os.path.join(dir_path, json_file_name)
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                        lat = data.get("lat")
                        lon = data.get("lon")
                        
                        if lat is not None and lon is not None:
                            writer.writerow([file_name, lat, lon])
                        else:
                            print(f"Warning: 'lat' or 'lon' not found in {json_file_name}")
                else:
                    print(f"Warning: No matching JSON for image {file_name}")
    
    print(f"CSV file has been created: {output_csv}")