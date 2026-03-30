import json
import os
import pandas as pd

def load_seat_config(config_path):
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return None
    return None

def test_render_logic():
    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, "src", "config", "seats_config.json")
    
    print(f"Testing with config path: {config_path}")
    
    seat_config = load_seat_config(config_path)
    
    if not seat_config:
        print("No seat configuration found.")
        return

    # Convert to DataFrame for display - Logic from students.py
    students_data = []
    try:
        for info in seat_config.get('seats', []):
            seat_id = info.get('id')
            info['seat_id'] = seat_id
            students_data.append(info)
        
        df = pd.DataFrame(students_data)
        print("Successfully created DataFrame:")
        print(df)
    except TypeError as e:
        print(f"Caught expected error if fix was not applied: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")

if __name__ == "__main__":
    test_render_logic()
