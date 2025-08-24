from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import ParameterVector

# --- Functions ---

def create_ansatz_A19_double(num_qubits=4, param_prefix='θ'):
    """
    Double application of Circuit 19:
    Layer 1: RX + RZ + CRX
    Layer 2: RX + RZ + CRX
    Total params = 16 (4 RX + 4 RZ + 4 CRX) * 2 = 24
    """
    if num_qubits != 4:
        raise ValueError("This ansatz is fixed for 4 qubits.")

    total_qubits = num_qubits * 2 + 1
    total_params = 24
    params = ParameterVector(param_prefix, total_params)

    q = QuantumRegister(total_qubits, 'q')
    qc = QuantumCircuit(q)

    # Define entangling pairs (same as A19)
    crx_pairs = [(3,0),(2,3),(1,2),(0,1)]

    # --- Layer 1 ---
    for i in range(num_qubits):
        qc.rx(params[i], q[i])           # RX
        qc.rz(params[4 + i], q[i])       # RZ
    for idx, (ctrl, targ) in enumerate(crx_pairs):
        qc.crx(params[8 + idx], q[ctrl], q[targ])

    # --- Layer 2 ---
    for i in range(num_qubits):
        qc.rx(params[12 + i], q[i])      # RX
        qc.rz(params[16 + i], q[i])      # RZ
    for idx, (ctrl, targ) in enumerate(crx_pairs):
        qc.crx(params[20 + idx], q[ctrl], q[targ])

    return qc, params


def create_reset_circuit(num_qubits, compression_level):
    total_qubits = num_qubits * 2 + 1
    reset_circuit = QuantumCircuit(total_qubits)
    for qubit in range(compression_level, num_qubits):
        reset_circuit.reset(qubit)
    return reset_circuit


def create_encoder_decoder_circuit(num_qubits, compression_level, decoder_option):
    encoder, encoder_params = create_ansatz_A19_double(num_qubits, param_prefix='θ_enc')
    reset_circuit = create_reset_circuit(num_qubits, compression_level)

    if decoder_option == 1:
        decoder = encoder.inverse()
        complete_circuit = encoder.compose(reset_circuit).compose(decoder)
        return complete_circuit, encoder_params, None

    elif decoder_option == 2:
        decoder, decoder_params = create_ansatz_A19_double(num_qubits, param_prefix='θ_dec')
        decoder = decoder.reverse_ops()
        complete_circuit = encoder.compose(reset_circuit).compose(decoder)
        return complete_circuit, encoder_params, decoder_params

    else:
        raise ValueError("Invalid decoder option. Choose 1 for inverse() or 2 for manual decoder.")
