from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import ParameterVector

def create_ansatz(num_qubits=4, compression_level=2, param_prefix='θ'):
    """
    Adaptive RX+RZ+CRX ansatz.
    - Number of layers = num_qubits - compression_level + 1
    - Each layer applies RX+RZ to active qubits and CRX entanglers
    - Active qubits reduce per layer to match compression_level
    """
    if num_qubits != 4:
        raise ValueError("This ansatz is fixed for 4 qubits.")

    total_qubits = num_qubits * 2 + 1
    qc = QuantumCircuit(total_qubits)

    # Define entangling CRX pairs
    crx_pairs = [(3,0),(2,3),(1,2),(0,1)]

    # Number of layers = num_qubits - compression_level + 1
    num_layers = num_qubits - compression_level + 1

    # Total parameters = 2 per active qubit per layer + extra for CRX per layer
    num_parameters = 2 * sum(num_qubits - layer for layer in range(num_layers)) * 1  # RX+RZ
    # For simplicity, add extra CRX params per layer
    num_parameters += 4 * num_layers  # 4 CRX per layer
    params = ParameterVector(param_prefix, num_parameters)

    param_index = 0
    for layer in range(num_layers):
        active_qubits = num_qubits - layer

        # RX + RZ on active qubits
        for q in range(active_qubits):
            qc.rx(params[param_index], q)
            param_index += 1
            qc.rz(params[param_index], q)
            param_index += 1

        # CRX entanglers on active qubits (use only qubits that exist)
        for ctrl, targ in crx_pairs:
            if ctrl < active_qubits and targ < active_qubits:
                qc.crx(params[param_index % num_parameters], ctrl, targ)
                param_index += 1

    return qc, params

def create_reset_circuit(num_qubits, compression_level):
    """
    Create a circuit that resets qubits compression_level to num_qubits-1.

    Args:
    num_qubits (int): Total number of qubits in the original space.
    compression_level (int): Number of qubits to compress to.

    Returns:
    QuantumCircuit: Circuit with reset operations.
    """
    total_qubits = num_qubits * 2 + 1
    reset_circuit = QuantumCircuit(total_qubits)
    for qubit in range(compression_level, num_qubits):
        reset_circuit.reset(qubit)
    return reset_circuit

def create_encoder_decoder_circuit(num_qubits, compression_level, decoder_option):
    """
    Create a complete encoder-decoder circuit based on the specified option and compression level.

    Args:
    num_qubits (int): Total number of qubits in the original space.
    compression_level (int): Number of qubits to compress to (1 <= compression_level <= num_qubits).
    decoder_option (int): 1 for Qiskit's .inverse(), 2 for manual decoder.

    Returns:
    QuantumCircuit: The complete encoder-decoder circuit with parameterized gates.
    ParameterVector: The parameters for the encoder RX and RZ gates.
    ParameterVector: The parameters for the decoder RX and RZ gates (None for option 1).
    """
    if compression_level < 1 or compression_level > num_qubits:
        raise ValueError(f"Compression level must be between 1 and {num_qubits}")

    encoder, encoder_params = create_ansatz(num_qubits, compression_level, param_prefix='θ_enc')
    reset_circuit = create_reset_circuit(num_qubits, compression_level)

    if decoder_option == 1:
        decoder = encoder.inverse()
        complete_circuit = encoder.compose(reset_circuit).compose(decoder)
        return complete_circuit, encoder_params, None

    elif decoder_option == 2:
        decoder, decoder_params = create_ansatz(num_qubits, compression_level, param_prefix='θ_dec')
        decoder = decoder.reverse_ops()

        complete_circuit = encoder.compose(reset_circuit).compose(decoder)
        return complete_circuit, encoder_params, decoder_params

    else:
        raise ValueError("Invalid decoder option. Choose 1 for Qiskit's .inverse() or 2 for manual decoder.")

def update_circuit_parameters(circuit, encoder_params, decoder_params, new_angles):
    """
    Update the circuit with new angles for encoder and decoder.

    Args:
    circuit (QuantumCircuit): The parameterized encoder-decoder circuit.
    encoder_params (ParameterVector): The encoder parameters.
    decoder_params (ParameterVector or None): The decoder parameters or None.
    new_angles (list): New angles for both encoder and decoder.

    Returns:
    QuantumCircuit: The updated circuit with new angles.
    """
    param_dict = {}

    num_encoder_params = len(encoder_params)
    param_dict.update(dict(zip(encoder_params, new_angles[:num_encoder_params])))

    if decoder_params is not None:
        param_dict.update(dict(zip(decoder_params, new_angles[num_encoder_params:])))
    
    bound_circuit = circuit.assign_parameters(param_dict)
    return bound_circuit
