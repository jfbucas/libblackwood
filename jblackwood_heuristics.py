
heuristic_array_a = [0] * 256  # Equivalent to new int[256] in C#

# Set max_heuristic_index
max_heuristic_index = 152

# Populate the heuristic array
for i in range(256):
    if i <= 10:
        heuristic_array_a[i] = 0
    elif i <= 26:
        heuristic_array_a[i] = int((i - 12) * 2.2857)
    elif i <= 56:
        heuristic_array_a[i] = int(((i - 26) * 1.3333) + 32)
    elif i <= 96:
        heuristic_array_a[i] = int(((i - 56) * 0.65) + 72)
    elif i <= max_heuristic_index:
        heuristic_array_a[i] = int(((i - 96) / 2.9473) + 98)



# Initialize the heuristic array
heuristic_array_b = [0] * 256  # Equivalent to new int[256] in C#

# Set max_heuristic_index
max_heuristic_index = 152

# Populate the heuristic array
for i in range(256):
    if i <= 18:
        heuristic_array_b[i] = 0
    elif i <= 26:
        heuristic_array_b[i] = int((i - 18) * 3.375)
    elif i <= 56:
        heuristic_array_b[i] = int(((i - 26) * 1.43333) + 27)
    elif i <= 96:
        heuristic_array_b[i] = int(((i - 56) * 0.70) + 70)
    elif i <= max_heuristic_index:
        heuristic_array_b[i] = int(((i - 96) / 2.9473) + 98)



# Initialize the heuristic array
heuristic_array_c = [0] * 256  # Equivalent to new int[256] in C#

# Define max_heuristic_index (ensure this is set appropriately elsewhere in your code)
max_heuristic_index = 156  # Example value; adjust as needed

# Populate the heuristic array
for i in range(256):
    if i <= 16:
        heuristic_array_c[i] = 0
    elif i <= 26:
        heuristic_array_c[i] = int((i - 16) * 3.1)
    elif i <= 56:
        heuristic_array_c[i] = int(((i - 26) * 1.43333) + 31)
    elif i <= 96:
        heuristic_array_c[i] = int(((i - 56) * 0.65) + 74)
    elif i <= max_heuristic_index:
        heuristic_array_c[i] = int(((i - 96) / 3.75) + 100)



# Initialize the heuristic array
heuristic_array_z = [0] * 256  # Equivalent to new int[256] in C#

# Define max_heuristic_index (this needs to be set to an appropriate value)
max_heuristic_index_z = 160  # Replace this with the actual value if different

for i in range(256):
    if i <= 16:
        heuristic_array_z[i] = 0
    elif i <= 26:
        heuristic_array_z[i] = int((i - 16) * 2.8)
    elif i <= 56:
        heuristic_array_z[i] = int(((i - 26) * 1.43333) + 28)
    elif i <= 76:
        heuristic_array_z[i] = int(((i - 56) * 0.9) + 71)
    elif i <= 102:
        heuristic_array_z[i] = int(((i - 76) * 0.6538) + 89)
    elif i <= max_heuristic_index:
        heuristic_array_z[i] = int(((i - 102) / 4.4615) + 106)

for i in range(256):
	print(i, heuristic_array_a[i], heuristic_array_b[i], heuristic_array_c[i], heuristic_array_z[i])
