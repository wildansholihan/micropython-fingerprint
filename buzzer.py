import time
import pwmio
import board

def beep(times, sleep_duration):
    """
    Makes the buzzer beep a specified number of times.

    :param times: Number of times the buzzer should beep
    """
    # Set up the pin for the buzzer with PWM
    buzzer = pwmio.PWMOut(board.GP15, duty_cycle=0, frequency=440, variable_frequency=True)

    for _ in range(times):
        buzzer.duty_cycle = 65536 // 2  # Set duty cycle to 50% (buzzer on)
        time.sleep(sleep_duration)                 # Beep for 0.5 seconds
        buzzer.duty_cycle = 0           # Set duty cycle to 0% (buzzer off)
        time.sleep(sleep_duration)                 # Pause for 0.5 seconds

    # Deinitialize the PWM to free up resources
    buzzer.deinit()
