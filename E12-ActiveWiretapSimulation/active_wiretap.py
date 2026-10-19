import numpy as np
from qunetsim.components import Host, Network
from qunetsim.objects import Qubit
import time

NUM_BITS = 100
rng = np.random.default_rng()

# Global tracking structures for sifting and QBER analysis
alice_bits = []
alice_bases = []
bob_bits = []
bob_bases = []

def alice_protocol(alice, receiver_id):
    for i in range(NUM_BITS):
        bit = int(rng.integers(0, 2))
        basis = int(rng.integers(0, 2))
        
        alice_bits.append(bit)
        alice_bases.append(basis)

        qubit = Qubit(alice)
        gate = "["
        value = "0"
        if bit == 1:
            value = "1"
            qubit.X()
        if basis == 1:
            gate = "Hadamard"
        else:
            gate = "None"

        # Send qubit to Eve (acting as the middleman)
        print(f"[Run#{str(i+1):>2}]:[{alice.host_id}] Transmitting qubit\t gate: {gate:<8} \t value:{value}")
        alice.send_qubit(receiver_id, qubit, await_ack=True)
        time.sleep(.125)

def eve_protocol(eve, sender_id, receiver_id):
    for i in range(NUM_BITS):
        qubit = eve.get_data_qubit(sender_id, wait=10)
        if qubit is None:
            continue

        eve_basis = int(rng.integers(0, 2))
        gate = ""
        if eve_basis == 1:
            qubit.H()
            gate = "Hadamard"
        else:
            gate = "None"

        eve_measured_bit = qubit.measure()

        # Eve re-prepares a new qubit matching her measurement outcome
        fwd_qubit = Qubit(eve)
        if eve_measured_bit == 1:
            fwd_qubit.X()
        if eve_basis == 1:
            fwd_qubit.H()

        # Forward the altered qubit state to Bob
        print(f"[Run#{str(i+1):>2}]:[{eve.host_id:<5}] Forwarding qubit\t gate: {gate:<8} \t value:{eve_measured_bit}\t")
        eve.send_qubit(receiver_id, fwd_qubit, await_ack=True)

def bob_protocol(bob, sender_id):
    for i in range(NUM_BITS):
        qubit = bob.get_data_qubit(sender_id, wait=10)
        if qubit is None:
            continue

        basis = int(rng.integers(0, 2))
        bob_bases.append(basis)

        gate = "None"
        if basis == 1:
            qubit.H()
            gate = "Hadamard"

        bit = qubit.measure()
        print(f"[Run#{str(i+1):>2}]:[{bob.host_id:<5}] Received the qubit\t gate: {gate:<8} \t value:{bit}\n")
        bob_bits.append(bit)

def main():
    network = Network.get_instance()
    nodes = ["Alice", "Eve", "Bob"]
    network.start(nodes)

    #Alice -> Eve
    alice = Host("Alice")
    alice.add_connection("Eve")
    alice.start()

    #Eve -> Alice
    eve = Host("Eve")
    eve.add_connection("Alice")
    #Eve -> Bob
    eve.add_connection("Bob")
    eve.start()

    #Bob -> eve`
    bob = Host("Bob")
    bob.add_connection("Eve")
    bob.start()

    network.add_host(alice)
    network.add_host(eve)
    network.add_host(bob)

    # Assign Threads
    t_alice = alice.run_protocol(alice_protocol, (eve.host_id,))
    t_eve = eve.run_protocol(eve_protocol, (alice.host_id, bob.host_id))
    t_bob = bob.run_protocol(bob_protocol, (eve.host_id,))

    t_alice.join()
    t_eve.join()
    t_bob.join()

    #Convert to numpy arrays
    alice_arr_bases = np.array(alice_bases)
    bob_arr_bases = np.array(bob_bases)
    alice_arr_bits = np.array(alice_bits)
    bob_arr_bits = np.array(bob_bits)

    #Find mataching indexes
    sifted_indices = np.where(alice_arr_bases == bob_arr_bases)[0]

    #Filter out matching indexes
    sifted_alice_bits = alice_arr_bits[sifted_indices]
    sifted_bob_bits = bob_arr_bits[sifted_indices]

    #Calculate Quantum Bit Error Rate
    corrupted_bits = np.sum(sifted_alice_bits != sifted_bob_bits)
    total_sifted = len(sifted_indices)
    qber = (corrupted_bits / total_sifted) * 100 if total_sifted > 0 else 0.0


    print("============================================================\n")
    print("              Active Wiretap Simulation SIMULATION          ")
    print("============================================================\n")
    print(f" Total Transmitted Qubits       : {NUM_BITS}")
    print(f" Sifted Bits (Matching Bases)   : {total_sifted} / {NUM_BITS} ({total_sifted / NUM_BITS * 100:.1f}%)")
    print(f" Corrupted Sifted Bits          : {corrupted_bits}")
    print(f" Calculated QBER                : {qber:.2f}%")
    print("============================================================\n")

    network.stop(stop_hosts=True)

if __name__ == "__main__":
    main()