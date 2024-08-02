def generate_all_otp_combinations():
    return [f"{i:04}" for i in range(10000)]

def write_otp_to_file(file_path, otp_list):
    with open(file_path, 'w') as file:
        file.write(f"Total OTP combinations: {len(otp_list)}\n\n")
        for otp in otp_list:
            file.write(f"{otp}\n")

# Generate all possible 4-digit OTP combinations
all_otps = generate_all_otp_combinations()

# Define the file path
file_path = 'otp_combinations.txt'

# Write all OTP combinations to the file
write_otp_to_file(file_path, all_otps)
