from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

def create_ansatz(num_qubits=4, compression_level=2, param_prefix='θ'):
    """
    Adaptive RX+RZ+CRX ansatz with correct parameter counting.
    - Number of layers = num_qubits - compression_level + 1
    - Each layer applies RX+RZ to active qubits and CRX entanglers
    - Active qubits reduce per layer to match compression_level
    """
    if num_qubits != 4:
        raise ValueError("This ansatz is fixed for 4 qubits.")

    total_qubits = num_qubits * 2 + 1
    qc = QuantumCircuit(total_qubits)

    # Define entangling CRX candidate pairs (control, target) in original ordering
    crx_pairs = [(3,0), (2,3), (1,2), (0,1)]

    # Number of layers = num_qubits - compression_level + 1
    num_layers = num_qubits - compression_level + 1

    # Compute exact number of parameters by iterating layers and counting RX/RZ + actual CRX used
    num_parameters = 0
    for layer in range(num_layers):
        active_qubits = num_qubits - layer
        # RX + RZ per active qubit
        num_parameters += 2 * active_qubits
        # count how many crx pairs will be applied given active_qubits
        num_crx_this_layer = sum(1 for ctrl, targ in crx_pairs if ctrl < active_qubits and targ < active_qubits)
        num_parameters += num_crx_this_layer

    params = ParameterVector(param_prefix, num_parameters)

    # Now actually populate circuit using params sequentially
    param_index = 0
    for layer in range(num_layers):
        active_qubits = num_qubits - layer

        # RX + RZ on active qubits
        for q in range(active_qubits):
            qc.rx(params[param_index], q)
            param_index += 1
            qc.rz(params[param_index], q)
            param_index += 1

        # CRX entanglers on active qubits (only if both indices are < active_qubits)
        for ctrl, targ in crx_pairs:
            if ctrl < active_qubits and targ < active_qubits:
                qc.crx(params[param_index], ctrl, targ)
                param_index += 1

    # param_index should equal num_parameters
    assert param_index == num_parameters, f"Parameter indexing mismatch: {param_index} vs {num_parameters}"

    return qc, params


def create_reset_circuit(num_qubits, compression_level):
    total_qubits = num_qubits * 2 + 1
    reset_circuit = QuantumCircuit(total_qubits)
    for qubit in range(compression_level, num_qubits):
        reset_circuit.reset(qubit)
    return reset_circuit


def create_encoder_decoder_circuit(num_qubits, compression_level, decoder_option):
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
        # If you intended a different reversal of operations, adjust here:
        decoder = decoder.reverse_ops()
        complete_circuit = encoder.compose(reset_circuit).compose(decoder)
        return complete_circuit, encoder_params, decoder_params

    else:
        raise ValueError("Invalid decoder option. Choose 1 for Qiskit's .inverse() or 2 for manual decoder.")


def update_circuit_parameters(circuit, encoder_params, decoder_params, new_angles):
    """
    Update the circuit with new angles for encoder and decoder.
    This version only binds parameters that actually appear in `circuit.parameters`.
    """
    param_dict = {}

    num_encoder_params = len(encoder_params)
    enc_angles = new_angles[:num_encoder_params]
    param_dict.update(dict(zip(encoder_params, enc_angles)))

    if decoder_params is not None:
        dec_angles = new_angles[num_encoder_params:num_encoder_params + len(decoder_params)]
        param_dict.update(dict(zip(decoder_params, dec_angles)))

    # Filter param_dict to only include parameters present in the circuit
    circuit_params_set = set(circuit.parameters)
    filtered_param_dict = {p: v for p, v in param_dict.items() if p in circuit_params_set}

    # Optionally report which parameters were dropped (useful for debugging)
    dropped = [p for p in param_dict.keys() if p not in circuit_params_set]
    if dropped:
        print(f"Warning: {len(dropped)} parameters in param_dict were not present in circuit and were ignored: {dropped}")

    bound_circuit = circuit.assign_parameters(filtered_param_dict)
    return bound_circuit

