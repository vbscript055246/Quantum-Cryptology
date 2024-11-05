from Qmath import *
from cirq.circuits import InsertStrategy

module_n = 15
exp_x = 7
vector_a = [pow(exp_x, x, module_n) for x in range(module_n)]
print(vector_a)
qbits_num = module_n.bit_length()

qft = cirq.Circuit()
# qft.append([cirq.X(cirq.LineQubit(i)) ** 0.5 for i in range(qbits_num)], strategy=InsertStrategy.NEW_THEN_INLINE)
# qft.append([cirq.H(cirq.LineQubit(i)) for i in range(qbits_num)], strategy=InsertStrategy.NEW_THEN_INLINE)

for i in range(qbits_num):
    qft.append(cirq.H(cirq.LineQubit(i)))
    for j in range(0, (qbits_num - 2) + 1 - i):
        qft.append(cirq.CZ(cirq.LineQubit(i), cirq.LineQubit(i + j + 1)) ** (1 / 2 ** (j + 1)), strategy=InsertStrategy.NEW)

qft.append(cirq.measure(*cirq.LineQubit.range(qbits_num), key='measrue'))
print(qft)
# print(cirq.sample(qft).data)

simulator = cirq.Simulator()
result = simulator.run(qft, repetitions=20)
#
print("result:")
print(result.data)


# qubits = cirq.LineQubit.range(4)
# qft_operation = cirq.qft(*qubits, without_reverse=True)
# qft_cirq = cirq.Circuit(qft_operation)
# print(qft_cirq)
# np.testing.assert_allclose(cirq.unitary(qft), cirq.unitary(qft_cirq))
