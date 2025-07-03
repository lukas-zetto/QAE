from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import ParameterVector

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import ParameterVector

def create_ansatz(num_qubits=4, param_prefix='θ'):
    """
    Create fixed ansatz with 4 RX, 4 RZ, 4 CRX parameters, returned as a single ParameterVector.
    
    Returns:
    - qc: QuantumCircuit
    - params: ParameterVector with length 12 (all parameters flattened)
    """
    if num_qubits != 4:
        raise ValueError("This ansatz is fixed for 4 qubits.")

    total_params = 12  # 4 RX + 4 RZ + 4 CRX
    params = ParameterVector(param_prefix, total_params)
    
    q = QuantumRegister(num_qubits, 'q')
    qc = QuantumCircuit(q)

    # Assign params to RX, RZ, CRX
    # RX: params[0..3]
    for i in range(num_qubits):
        qc.rx(params[i], q[i])
    # RZ: params[4..7]
    for i in range(num_qubits):
        qc.rz(params[4 + i], q[i])
    # CRX: params[8..11]
    crx_pairs = [
        (3, 0),
        (2, 3),
        (1, 2),
        (0, 1)
    ]
    for idx, (ctrl, targ) in enumerate(crx_pairs):
        qc.crx(params[8 + idx], q[ctrl], q[targ])

    return qc, params


def create_reset_circuit(num_qubits, compression_level):
    """
    Create a circuit that resets qubits from compression_level to num_qubits - 1.
    """
    reset_circuit = QuantumCircuit(num_qubits)
    for qubit in range(compression_level, num_qubits):
        reset_circuit.reset(qubit)
    return reset_circuit

def create_encoder_decoder_circuit(num_qubits, compression_level, decoder_option):
    """
    Create a complete encoder-decoder circuit using the structured ansatz.
    """
    if compression_level < 1 or compression_level > num_qubits:
        raise ValueError(f"Compression level must be between 1 and {num_qubits}")

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
    else:
        decoder_flat = []

    bound_circuit = circuit.assign_parameters(param_dict)

    return bound_circuit


    # """
    # Update the circuit with new angles for encoder and decoder.
    # """
    # param_dict = {}

    # encoder_flat = []
    # for vec in encoder_params.values():
    #     encoder_flat.extend(vec)
    # num_encoder_params = len(encoder_flat)
    # param_dict.update(dict(zip(encoder_flat, new_angles[:num_encoder_params])))

    # if decoder_params is not None:
    #     decoder_flat = []
    #     for vec in decoder_params.values():
    #         decoder_flat.extend(vec)
    #     param_dict.update(dict(zip(decoder_flat, new_angles[num_encoder_params:])))

    # bound_circuit = circuit.assign_parameters(param_dict)
    # return bound_circuit
