import numpy as np

def sift_bases(alice_bases, bob_bases):
    
    if len(alice_bases) != len(bob_bases):
        raise ValueError("Alice and Bob must have same number of entries")
    
    matching_bases = []

    for i in range(len(alice_bases)):
        if alice_bases[i] == bob_bases[i]:
            matching_bases.append(i)
    
    return matching_bases

def main():
    rng = np.random.default_rng()
    bases_size=32
    alice_bases = rng.choice(['Rectilinear', 'Diagonal'], size=bases_size)
    bob_bases = rng.choice(['Rectilinear', 'Diagonal'], size=bases_size)
    
    # Perform sifting
    sifted_bases = sift_bases(alice_bases, bob_bases)


    
    print("\n\n                         BASIS SIFTING RESULTS                          ")
    print("========================================================================")
    print(f"{'':<6} {'Idx':<4} | {'Alice Basis':<14} | {'Bob Basis':<14} | {'Match Status'}")
    print("------------------------------------------------------------------------")
    
    for idx in range(len(alice_bases)):
        status = "DISCARD"
        if idx in sifted_bases:
            status = "KEEP"
        print(f"{'':<6} {idx:<4} | {alice_bases[idx]:<14} | {bob_bases[idx]:<14} | {status}")
        
    print("------------------------------------------------------------------------")
    print("FILTERED MATCHING INDICES:")
    print(sifted_bases)
    print(f"Summary: {len(sifted_bases)} / {len(alice_bases)} bases matched "
          f"({(len(sifted_bases)/len(alice_bases))*100:.1f}% match).")
    print("========================================================================")

if __name__ == "__main__":
    main()