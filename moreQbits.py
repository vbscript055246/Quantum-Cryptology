from Qmath import *

module_n = 55
exp_x = 7
L = module_n.bit_length()

mod_exp = ModularExp([2] * L, [2] * (2 * L + 3), exp_x, module_n)
target = cirq.LineQubit.range(L)
exponent = cirq.LineQubit.range(L, 3 * L + 3)

c = cirq.Circuit(
    cirq.X(target[L - 1]),
    cirq.H.on_each(*exponent),
    mod_exp.on(*target, *exponent),
    # cirq.measure(*exponent, key='middle'),
    cirq.qft(*exponent),
    cirq.measure(*exponent, key='exponent'),
)

print(c)
# simulator = cirq.Simulator()
# result = simulator.run(c, repetitions=10)
# print("result:")
# print(result.data)

print(f"Finding the order of x = {exp_x} modulo n = {module_n}\n")
measurement = cirq.sample(c, repetitions=1)
print("Raw measurements:")
print(measurement)

print("\nInteger in exponent register:")
print(measurement.data)

r = process_measurement(measurement, exp_x, module_n)
print("\nOrder r =", r)
if r is not None:
    print(f"x^r mod n = {exp_x}^{r} mod {module_n} = {exp_x**r % module_n}")
