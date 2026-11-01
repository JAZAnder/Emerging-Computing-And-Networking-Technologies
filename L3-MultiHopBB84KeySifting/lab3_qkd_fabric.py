cd ./import sys
import time
import numpy as np
from qunetsim.components import Host, Network
from qunetsim.objects import Qubit

# Global Simulation Parameters
NUM_BITS = 200
SAMPLE_RATIO = 0.25
QBER_THRESHOLD = 0.15
WAIT_TIME = .02

DEBUG = False


# Global arrays
alice_bits = []
alice_bases = []
bob_bits = []
bob_bases = []
rng = np.random.default_rng()

def alice_protocol(alice, next_hop):
    
    for i in range(NUM_BITS):
        bit = int(rng.integers(0, 2))
        basis = int(rng.integers(0, 2))

        alice_bits.append(bit)
        alice_bases.append(basis)

        qubit = Qubit(alice)

        value = "0"
        if bit == 1:
            value = "1"
            qubit.X()
        if basis == 1:
            qubit.H()
            gate = "Hadamard"
        else:
            gate = "None"

        if DEBUG:
            print(f"[Run#{str(i+1):>2}]:[{alice.host_id}] Transmitting qubit\t gate: {gate:<8} \t value:{value}")

        alice.send_qubit(next_hop, qubit, await_ack=False)
        time.sleep(WAIT_TIME)


def intermediate_forwarder(node, prev_hop, next_hop, eve_active=False):
    for i in range(NUM_BITS):
        qubit = node.get_data_qubit(prev_hop, wait=(WAIT_TIME*500))
        if qubit is None:
            continue

        # Simulate Eve 
        if eve_active:
            eve_basis = int(rng.integers(0, 2))
            if eve_basis == 1:
                qubit.H()
                gate = "Hadamard"
            else: 
                gate = "None"
            
            eve_bit = qubit.measure()

            if DEBUG:
                print(f"[Run#{str(i+1):>2}]:[{"EVE":<5}] Reading qubit\t gate: {gate:<8} \t value:{eve_bit}\t")

            qubit = Qubit(node)
            if eve_bit == 1:
                qubit.X()
            if eve_basis == 1:
                qubit.H()
        #End Eve
        if DEBUG:
            print(f"[Run#{str(i+1):>2}]:[{node.host_id:<5}] Forwarding qubit\t gate: {"UNKNOWN":<8} \t value:UNKNOWN\t")

        node.send_qubit(next_hop, qubit, await_ack=False)


def bob_protocol(bob, prev_hop):
    rng = np.random.default_rng()
    for i in range(NUM_BITS):
        qubit = bob.get_data_qubit(prev_hop, wait=WAIT_TIME*500)
        if qubit is not None:
            basis = int(rng.integers(0, 2))
            bob_bases.append(basis)

            gate = "None"
            if basis == 1:
                qubit.H()
                gate = "Hadamard"

            bit = qubit.measure()
            if DEBUG:
                print(f"[Run#{str(i+1):>2}]:[{bob.host_id:<5}] Received the qubit\t gate: {gate:<8} \t value:{bit}\n")
            bob_bits.append(bit)
        else:
            # Placeholder in case of packet timeout
            bob_bases.append(-1)
            bob_bits.append(-1)


def privacy_amplification(candidate_key):
    amplified_key = []
    for i in range(0, len(candidate_key) - 1, 2):
        #XOR 1 & 2 -> party bit
        parity_bit = int(candidate_key[i] ^ candidate_key[i + 1])
        amplified_key.append(parity_bit)
    return amplified_key


def execute_qkd_session(eve_active=False):
    #Fresh start
    alice_bits.clear()
    alice_bases.clear()
    bob_bits.clear()
    bob_bases.clear()

    network = Network.get_instance()
    network.stop(stop_hosts=True)
    time.sleep(0.2)

    nodes = ["Alice", "Node1", "Node2", "Node3", "Bob"]
    network.start(nodes)

    #Hosts
    alice = Host("Alice")
    node1 = Host("Node1")
    node2 = Host("Node2")
    node3 = Host("Node3")
    bob = Host("Bob")

    #Connections
    alice.add_connection("Node1")
    node1.add_connection("Alice")
    node1.add_connection("Node2")
    node2.add_connection("Node1")
    node2.add_connection("Node3")
    node3.add_connection("Node2")
    node3.add_connection("Bob")
    bob.add_connection("Node3")

    for h in [alice, node1, node2, node3, bob]:
        h.start()
        network.add_host(h)

    network.start()
    start_time = time.time()

    # Launch protocols
    t_alice = alice.run_protocol(alice_protocol, (node1.host_id,))
    t_node1 = node1.run_protocol(intermediate_forwarder, (alice.host_id, node2.host_id, False))
    t_node2 = node2.run_protocol(intermediate_forwarder, ("Node1", "Node3", eve_active))
    t_node3 = node3.run_protocol(intermediate_forwarder, ("Node2", "Bob", False))
    t_bob = bob.run_protocol(bob_protocol, (node3.host_id,))

    t_alice.join()
    t_node1.join()
    t_node2.join()
    t_node3.join()
    t_bob.join()

    elapsed_time = time.time() - start_time
    network.stop(stop_hosts=True)

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

    # Get sample indexes
    sample_size = int(len(sifted_indices) * SAMPLE_RATIO)
    sample_sub_indices = rng.choice(len(sifted_indices), size=sample_size, replace=False)

    sample_errors = sum(
        1 for idx in sample_sub_indices if sifted_alice_bits[idx] != sifted_bob_bits[idx]
    )

    qber = (sample_errors / sample_size) if sample_size > 0 else 0.0


    #Remove sampled bits
    candidate_indices = [
        i for i in range(len(sifted_indices)) 
            if i not in sample_sub_indices
        ]
    cand_alice = [sifted_alice_bits[i] for i in candidate_indices]
    cand_bob = [sifted_bob_bits[i] for i in candidate_indices]


    print("\n" + "=" * 70)
    print(f" LAB 3 QKD FABRIC SESSION | EVE ACTIVE: {eve_active} ")
    print("=" * 70)
    print(f" Total Transmitted Qubits   : {NUM_BITS}")
    print(f" Transmission Time          : {elapsed_time:.2f} seconds")
    print(f" Sifted Key Length          : {len(sifted_indices)} bits ({len(sifted_indices)/NUM_BITS*100:.1f}%)")
    print(f" Sacrificed Sample Size     : {sample_size} bits")
    print(f" Sample Bit Mismatches      : {sample_errors}")
    print(f" Calculated QBER            : {qber * 100:.2f}%")
    print(f" QBER Security Threshold    : {QBER_THRESHOLD * 100:.1f}%")
    print("-" * 70)

    if qber >= QBER_THRESHOLD:
        print(" [ALERT] SECURITY COMPROMISE DETECTED!")
        print(f" QBER ({qber*100:.2f}%) EXCEEDS SAFETY THRESHOLD ({QBER_THRESHOLD*100:.1f}%).")
        print(" ACTION: ABORTING KEY SESSION")
        print("=" * 70)
        return
    else:
        print(" [SECURE] CHANNEL INTEGRITY VERIFIED.")
        print(f" QBER ({qber*100:.2f}%) IS WITHIN PERMISSIBLE LIMITS.")

        final_key_alice = privacy_amplification(cand_alice)
        final_key_bob = privacy_amplification(cand_bob)
        
        key_matches = (final_key_alice == final_key_bob)

        print(" Executing Privacy Amplification (Block Parity Compression)...")
        print(f" Candidate Key Length       : {len(cand_alice)} bits")
        print(f" Final Secure Key Length    : {len(final_key_alice)} bits")
        print(f" Keys Synchronized (A == B) : {key_matches}")
        print(f" Sample Final Key (Alice)   : {final_key_alice[:16]}")
        print("=" * 70)
        return


if __name__ == "__main__":
    print("\n--- RUNNING SCENARIO 1: EVE INACTIVE (NORMAL FABRIC OPERATION) ---")
    execute_qkd_session(eve_active=False)

    time.sleep(1.0)

    print("\n--- RUNNING SCENARIO 2: EVE ACTIVE (INTERCEPT-RESEND ON NODE2-NODE3) ---")
    execute_qkd_session(eve_active=True)