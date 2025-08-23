# quantum_autoencoder_fixed_ansatz_with_ancilla_v2.ipynb
# Jupyter notebook to create and draw the 4-qubit fixed ansatz encoder-decoder quantum circuit with ancilla qubits and two RX-RZ layers

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import ParameterVector

# --- Functions ---

def create_ansatz(num_qubits=4, param_prefix='θ'):
    """
    Fixed ansatz with two RX-RZ layers + CRX entanglement on total_qubits = 2*num_qubits + 1.
    Total parameters: 20 (4 RX + 4 RZ + 4 RX + 4 RZ + 4 CRX)
    """
    if num_qubits != 4:
        raise ValueError("This ansatz is fixed for 4 qubits.")

    total_qubits = num_qubits * 2 + 1
    total_params = 20
    params = ParameterVector(param_prefix, total_params)

    q = QuantumRegister(total_qubits, 'q')
    qc = QuantumCircuit(q)

    # Apply layers to original qubits (q_0..q_3)
    for i in range(num_qubits):
        qc.rx(params[i], q[i])           # RX layer 1
        qc.rz(params[4 + i], q[i])       # RZ layer 1
        qc.rx(params[8 + i], q[i])       # RX layer 2
        qc.rz(params[12 + i], q[i])      # RZ layer 2

    # CRX entanglement
    crx_pairs = [(3,0),(2,3),(1,2),(0,1)]
    for idx, (ctrl, targ) in enumerate(crx_pairs):
        qc.crx(params[16 + idx], q[ctrl], q[targ])

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

# --- Create and draw the circuit ---
num_qubits = 4
compression_level = 2
decoder_option = 1

circuit, enc_params, dec_params = create_encoder_decoder_circuit(num_qubits, compression_level, decoder_option)

# Draw circuit in ASCII for Jupyter
print(circuit.draw('text'))