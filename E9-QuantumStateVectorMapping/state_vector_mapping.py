import numpy as np

def generate_quantum_states(num_bits):
    rng = np.random.default_rng()
    
    #generate random ints (0 or 1)
    data_bits = rng.integers(0, 2, size=num_bits)
    
    #generate randomized basis selections: Rectilinear or Diagonal
    bases = rng.choice(['Rectilinear', 'Diagonal'], size=num_bits)
    
    return data_bits, bases

def main():
    num_bits = 32
    data_bits, bases = generate_quantum_states(num_bits)
    
    # Print array vectors side-by-side
    print(f"{'Index':<6} | {'Bit':<5} | {'Basis Selection'}")
    print("--------------------------------")
    for i in range(num_bits):
        print(f"{i:<6} | {data_bits[i]:<5} | {bases[i]}")

    print("--------------------------------")

if __name__ == "__main__":
    main()