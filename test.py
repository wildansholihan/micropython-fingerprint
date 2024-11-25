from buzzer import beep
from oled_text import init_display, display_text, display_centered_text, clear_display
from fingerprint import enroll_fingerprint, search_fingerprint, remove_fingerprint, remove_all_fingerprints
import time

# Example: Beep 3 times
display, group = init_display()
display_centered_text(display, group, text="Selamat datang", wrap_at=16)
beep(2, 0.1)
time.sleep(1)

while True:
    clear_display(group)
    display_text(display, group, text="1. Enroll Fingerprint", wrap_at=25)
    print("1. Enroll Fingerprint")
    print("2. Search Fingerprint")
    print("3. Remove Fingerprint")
    print("4. Remove All Fingerprints")
    choice = input("Enter your choice: ")
    
    if choice == "1":
        beep(1, 0.1)
        location = int(input("Enter ID location to save: "))
        enroll_fingerprint(location)
    elif choice == "2":
        beep(2, 0.1)
        search_fingerprint()
    elif choice == "3":
        beep(2, 0.1)
        location = int(input("Enter ID location to remove: "))
        remove_fingerprint(location)
    elif choice == "4":
        beep(2, 0.1)
        remove_all_fingerprints()
    else:
        print("Invalid choice!")



