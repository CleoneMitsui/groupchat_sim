from datetime import datetime
import random

# fallback id generator
def generate_participant_id():
    now_str = datetime.now().strftime("%Y%m%d%H%M%S")
    rand_suffix = random.randint(1000, 9999)
    return f"{now_str}_{rand_suffix}"
