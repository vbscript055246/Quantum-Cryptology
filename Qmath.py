import cirq
from typing import Callable, Iterable, List, Optional, Sequence, Union
import fractions


class Add(cirq.ArithmeticGate):
    def __init__(
        self,
        target_register: '[int, Sequence[int]]',
        input_register: 'Union[int, Sequence[int]]',
    ):
        self.target_register = target_register
        self.input_register = input_register

    def registers(self) -> 'Sequence[Union[int, Sequence[int]]]':
        return self.target_register, self.input_register

    def with_registers(
        self, *new_registers: 'Union[int, Sequence[int]]'
    ) -> 'TSelfGate':
        return Add(*new_registers)

    def apply(self, *register_values: int) -> 'Union[int, Iterable[int]]':
        return sum(register_values)


class ModularExp(cirq.ArithmeticGate):
    """Quantum modular exponentiation.

    This class represents the unitary which multiplies base raised to exponent
    into the target modulo the given modulus. More precisely, it represents the
    unitary V which computes modular exponentiation x**e mod n:

        V|y⟩|e⟩ = |y * x**e mod n⟩ |e⟩     0 <= y < n
        V|y⟩|e⟩ = |y⟩ |e⟩                  n <= y

    where y is the target register, e is the exponent register, x is the base
    and n is the modulus. Consequently,

        V|y⟩|e⟩ = (U**e|y)|e⟩

    where U is the unitary defined as

        U|y⟩ = |y * x mod n⟩      0 <= y < n
        U|y⟩ = |y⟩                n <= y
    """
    def __init__(
        self,
        target: Sequence[int],
        exponent: Union[int, Sequence[int]],
        base: int,
        modulus: int
    ) -> None:
        if len(target) < modulus.bit_length():
            raise ValueError(
                f'Register with {len(target)} qubits is too small for modulus'
                f' {modulus}'
            )
        self.target = target
        self.exponent = exponent
        self.base = base
        self.modulus = modulus

    def registers(self) -> Sequence[Union[int, Sequence[int]]]:
        return self.target, self.exponent, self.base, self.modulus

    def with_registers(
        self, *new_registers: Union[int, Sequence[int]]
    ) -> 'ModularExp':
        """Returns a new ModularExp object with new registers."""
        if len(new_registers) != 4:
            raise ValueError(
                f'Expected 4 registers (target, exponent, base, '
                f'modulus), but got {len(new_registers)}'
            )
        target, exponent, base, modulus = new_registers
        if not isinstance(target, Sequence):
            raise ValueError(
                f'Target must be a qubit register, got {type(target)}'
            )
        if not isinstance(base, int):
            raise ValueError(
                f'Base must be a classical constant, got {type(base)}'
            )
        if not isinstance(modulus, int):
            raise ValueError(
              f'Modulus must be a classical constant, got {type(modulus)}'
            )
        return ModularExp(target, exponent, base, modulus)

    def apply(self, *register_values: int) -> int:
        """Applies modular exponentiation to the registers.

        Four values should be passed in.  They are, in order:
          - the target
          - the exponent
          - the base
          - the modulus

        Note that the target and exponent should be qubit
        registers, while the base and modulus should be
        constant parameters that control the resulting unitary.
        """
        assert len(register_values) == 4
        target, exponent, base, modulus = register_values
        if target >= modulus:
            return target
        return (target * base**exponent) % modulus

    def _circuit_diagram_info_(
      self, args: cirq.CircuitDiagramInfoArgs
    ) -> cirq.CircuitDiagramInfo:
        """Returns a 'CircuitDiagramInfo' object for printing circuits.

        This function just returns information on how to print this operation
        out in a circuit diagram so that the registers are labeled
        appropriately as exponent ('e') and target ('t').
        """
        assert args.known_qubits is not None
        wire_symbols = [f't{i}' for i in range(len(self.target))]
        e_str = str(self.exponent)
        if isinstance(self.exponent, Sequence):
            e_str = 'e'
            wire_symbols += [f'e{i}' for i in range(len(self.exponent))]
        wire_symbols[0] = f'ModularExp(t*{self.base}**{e_str} % {self.modulus})'
        return cirq.CircuitDiagramInfo(wire_symbols=tuple(wire_symbols))


def process_measurement(result: cirq.Result, x: int, n: int) -> Optional[int]:
    """Interprets the output of the order finding circuit.

    Specifically, it determines s/r such that exp(2πis/r) is an eigenvalue
    of the unitary

        U|y⟩ = |xy mod n⟩  0 <= y < n
        U|y⟩ = |y⟩         n <= y

    then computes r (by continued fractions) if possible, and returns it.

    Args:
        result: result obtained by sampling the output of the
            circuit built by make_order_finding_circuit

    Returns:
        r, the order of x modulo n or None.
    """
    # Read the output integer of the exponent register.
    exponent_as_integer = result.data["exponent"][0]
    exponent_num_bits = result.measurements["exponent"].shape[1]
    eigenphase = float(exponent_as_integer / 2**exponent_num_bits)

    # Run the continued fractions algorithm to determine f = s / r.
    f = fractions.Fraction.from_float(eigenphase).limit_denominator(n)

    print(f"\nFraction: {f}")

    # If the numerator is zero, the order finder failed.
    if f.numerator == 0:
        return None

    # Else, return the denominator if it is valid.
    r = f.denominator
    if x**r % n != 1:
        return None
    return r