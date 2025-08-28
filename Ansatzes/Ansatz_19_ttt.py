from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import ParameterVector

# --- Functions ---

def create_ansatz(num_qubits=4, param_prefix='θ'):
    """
    Triple application of Circuit 19:
    Layer 1: RX + RZ + CRX
    Layer 2: RX + RZ + CRX
    Layer 3: RX + RZ + CRX
    Total params = 12 * 3 = 36
    """
    if num_qubits != 4:
        raise ValueError("This ansatz is fixed for 4 qubits.")

    total_qubits = num_qubits * 2 + 1
    total_params = 36  # 12 parameters per layer * 3 layers
    params = ParameterVector(param_prefix, total_params)

    q = QuantumRegister(total_qubits, 'q')
    qc = QuantumCircuit(q)

    # Define entangling pairs (same as A19)
    crx_pairs = [(3,0),(2,3),(1,2),(0,1)]

    # --- Layer 1 ---
    for i in range(num_qubits):
        qc.rx(params[i], q[i])
        qc.rz(params[4 + i], q[i])
    for idx, (ctrl, targ) in enumerate(crx_pairs):
        qc.crx(params[8 + idx], q[ctrl], q[targ])

    # --- Layer 2 ---
    for i in range(num_qubits):
        qc.rx(params[12 + i], q[i])
        qc.rz(params[16 + i], q[i])
    for idx, (ctrl, targ) in enumerate(crx_pairs):
        qc.crx(params[20 + idx], q[ctrl], q[targ])

    # --- Layer 3 ---
    for i in range(num_qubits):
        qc.rx(params[24 + i], q[i])
        qc.rz(params[28 + i], q[i])
    for idx, (ctrl, targ) in enumerate(crx_pairs):
        qc.crx(params[32 + idx], q[ctrl], q[targ])

    return qc, params



def create_reset_circuit(num_qubits, compression_level):
    total_qubits = num_qubits * 2 + 1
    reset_circuit = QuantumCircuit(total_qubits)
    for qubit in range(compression_level, num_qubits):
        reset_circuit.reset(qubit)
    return reset_circuit


def create_encoder_decoder_circuit(num_qubits, compression_level, decoder_option):
    encoder, encoder_params = create_ansatz(num_qubits, param_prefix='θ_enc')
    reset_circuit = create_reset_circuit(num_qubits, compression_level)

    if decoder_option == 1:
        decoder = encoder.inverse()
        complete_circuit = encoder.compose(reset_circuit).compose(decoder)
        return complete_circuit, encoder_params, None

    elif decoder_option == 2:
        decoder, decoder_params = create_ansatz(num_qubits, param_prefix='θ_dec')
        decoder = decoder.reverse_ops()
        complete_circuit = encoder.compose(reset_circuit).compose(decoder)
        return complete_circuit, encoder_params, decoder_params

    else:
        raise ValueError("Invalid decoder option. Choose 1 for inverse() or 2 for manual decoder.")


def update_circuit_parameters(circuit, encoder_params, decoder_params, new_angles):
    param_dict = {}
    encoder_flat = list(encoder_params)
    num_encoder_params = len(encoder_flat)
    param_dict.update(dict(zip(encoder_flat, new_angles[:num_encoder_params])))

    if decoder_params is not None:
        decoder_flat = list(decoder_params)
        param_dict.update(dict(zip(decoder_flat, new_angles[num_encoder_params:])))

    bound_circuit = circuit.assign_parameters(param_dict)
    return bound_circuit

