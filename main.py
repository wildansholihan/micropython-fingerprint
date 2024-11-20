from oled import OLEDDisplay
from fingerprint_match import match_fingerprint
from fingerprint_enroll import enroll_fingerprint
from fingerprint_remove import remove_fingerprint, delete_all_fingerprints_iteratively
import time

oled_display = OLEDDisplay()

def main_menu():
    while True:
        oled_display.clear()
        oled_display.display_text("Select Menu:", 0, 2)
        oled_display.display_text("1. Enroll", 0, 17)
        oled_display.display_text("2. Match", 0, 30)
        oled_display.display_text("3. Remove ", 0, 43)
        oled_display.display_text("4. Remove All", 0, 56)
        
        print("\nFingerprint System Menu:")
        print("1. Enroll Fingerprint")
        print("2. Match Fingerprint")
        print("3. Remove Fingerprint")
        print("4. Clear All Data")
        choice = input("Enter your choice: ")

        if choice == "1":
            oled_display.clear()
            oled_display.display_text("Enter user id:", 0, 7)
            finger_id = input("Enter user id: ")  # Example finger ID, adjust as needed
            print("Starting fingerprint enrollment...")
            
            success = enroll_fingerprint(int(finger_id))
            
            if success:
                oled_display.clear();
                oled_display.display_text("Enrollment success", 0, 7)  # Baris pertama
                oled_display.display_text(f"ID: {finger_id}", 0, 20)   # Baris kedua (atur y lebih besar
                print(f"Fingerprint enrollment and storage successful for ID: {finger_id}")
            else:
                print(f"Fingerprint enrollment or storage failed for ID: {finger_id}")
            
            time.sleep(2)

        elif choice == "2":
            print("Starting fingerprint matching...")
            matched_id = match_fingerprint()
            print(matched_id)
            if matched_id is not None:
                text = f"ID {matched_id}";
                try:
                    oled_display.clear();
                    oled_display.display_text("User found", 0, 7)
                    oled_display.display_text(text, 0, 20)
                except Exception as e:
                    print(f"Error oled: {e}")
                    
            else:
                oled_display.clear();
                oled_display.display_text("User not found", 0, 7)
            time.sleep(2)

        elif choice == "3":
            finger_id = input("Enter user id: ")
            success = remove_fingerprint(int(finger_id))
            if success:
                print(f"Fingerprint remove successful for ID: {finger_id}")
            else:
                print(f"Fingerprint remove failed for ID: {finger_id}")

        elif choice == "4":
            success = delete_all_fingerprints_iteratively(1,127)
            if success:
                print(f"Fingerprint clear all successful")
            else:
                print(f"Fingerprint clear all is failed")
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()