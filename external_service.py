import random
import time

def verify_background(applicant_name: str, max_retries: int = 3):
    """
    Simulates calling an external background check API.
    It has a 40% chance of failing to simulate network issues.
    """
    print(f"\n--- Calling External API for {applicant_name} ---")
    
    for attempt in range(1, max_retries + 1):
        # random.random() returns a float between 0.0 and 1.0
        if random.random() < 0.4: 
            print(f"[Attempt {attempt}/{max_retries}] External API timed out. Retrying...")
            time.sleep(1) # Wait 1 second before retrying
        else:
            print(f"[Attempt {attempt}/{max_retries}] External API success!")
            return True # Success!
            
    # If the loop finishes without returning True, it means all retries failed
    raise Exception("External API completely completely failed after retries.")