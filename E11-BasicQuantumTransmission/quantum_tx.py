from qunetsim.components import Host, Network
from qunetsim.objects import Qubit

NUM_RUNS = 100

def alice_protocol(alice, receiver_id):
    print(f"\n[{alice.host_id}] Starting transmission of {NUM_RUNS} qubits in superposition state |+>...\n")
    
    for i in range(NUM_RUNS):
        qubit = Qubit(alice)
        qubit.H()  # Put into superposition
        print(f"[Run#{str(i+1)}]:[{alice.host_id}] Created qubit and applied Hadamard gate (superposition state |+>).")
        print(f"[Run#{str(i+1)}]:[{alice.host_id}] Transmitting qubit over quantum link to {receiver_id}...")
        alice.send_qubit(receiver_id, qubit, await_ack=True)

        
    print(f"[{alice.host_id}] Finished transmitting all {NUM_RUNS} qubits.")

def bob_protocol(bob, sender_id):
    results = []
    
    for i in range(NUM_RUNS):
        print(f"[Run#{str(i+1)}]:[{bob.host_id}] Listening for incoming quantum transmission from {sender_id}...")
        qubit = bob.get_data_qubit(sender_id, wait=10)
        if qubit is not None:
            # Measure in rectilinear ( computational ) basis
            res = qubit.measure()
            results.append(res)
            print(f"[Run#{str(i+1)}]:[{bob.host_id}] Qubit Received! Collapsed Classical Result: {res}\n")
        else:
            print(f"[Run#{str(i+1)}]:[{bob.host_id}] Timeout error receiving qubit index {i}.")


    zeros = results.count(0)
    ones = results.count(1)
    
    print("\n============================================================")
    print(f"           QUNETSIM STATISTICAL RESULTS         ")
    print("============================================================")
    print(f" Total Qubits Successfully Received : {len(results)} / {NUM_RUNS}")
    print(f" Collapsed Classical '0' Count     : {zeros} ({zeros / len(results) * 100:.1f}%)")
    print(f" Collapsed Classical '1' Count     : {ones} ({ones / len(results) * 100:.1f}%)")
    print("============================================================\n")

def main():
    network = Network.get_instance()
    nodes = ["Alice", "Bob"]
    network.start(nodes)

    alice = Host("Alice")
    alice.add_connection("Bob")
    alice.start()

    bob = Host("Bob")
    bob.add_connection("Alice")
    bob.start()

    network.add_host(alice)
    network.add_host(bob)

    thread_alice = alice.run_protocol(alice_protocol, (bob.host_id,))
    thread_bob = bob.run_protocol(bob_protocol, (alice.host_id,))

    thread_alice.join()
    thread_bob.join()

    network.stop(stop_hosts=True)

if __name__ == "__main__":
    main()