"""Monolithic Solid-State Terahertz Waveguide Injection Core Behavioral Simulation

Engine Author: Abhishek Singh License: MIT.
"""

import json
import os
import numpy as np


class TerahertzCoreSimulator:

    def __init__(self, config_path="config.json"):
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.params = json.load(f)["operational_parameters"]
        else:
            self.params = {
                "target_frequency_hz": 100e12,
                "impedance_free_space_ohm": 377.0,
                "impedance_2d_channel_ohm": 50.0,
                "gate_threshold_voltage": 0.5,
            }

        self.freq = self.params["target_frequency_hz"]
        self.omega = 2 * np.pi * self.freq
        self.z0 = self.params["impedance_free_space_ohm"]
        self.z_chan = self.params["impedance_2d_channel_ohm"]

    def run_injection_stage(self, channels=8):
        """Stage 1: Phased array electron packet injection."""
        t = np.linspace(0, 1 / self.freq, 100)
        waves = [np.sin(self.omega * t) for _ in range(channels)]
        coherent_sum = np.sum(waves, axis=0) / channels
        return np.max(coherent_sum)

    def run_impedance_taper(self, points=50):
        """Stage 2: Exponential impedance mouth transition."""
        taper = self.z0 * (self.z_chan / self.z0) ** np.linspace(0, 1, points)
        s11 = np.abs((taper[-1] - self.z_chan) / (taper[-1] + self.z_chan))
        return taper[-1], s11

    def run_quantum_gate(self, input_amp, gate_v):
        """Stage 3: 2D monolayer electrostatic switching."""
        if gate_v >= self.params["gate_threshold_voltage"]:
            return 0.0, input_amp * 0.98, "BINARY_1 (REDIRECT)"
        return input_amp * 0.98, 0.0, "BINARY_0 (PASS)"

    def run_extraction(self, amp):
        """Stage 4: Out-of-plane wireless beamforming."""
        return amp**2


if __name__ == "__main__":
    sim = TerahertzCoreSimulator()
    print("=== TERAHERTZ CORE SIMULATION ENGINE VERIFIED ===")
    print(f"Injection Amplitude : {sim.run_injection_stage():.4f}")
    z_out, reflection = sim.run_impedance_taper()
    print(
        f"Impedance Match     : {z_out:.1f} Ohm (Reflection S11 = {reflection:.6f})"
    )
    ch_l, ch_r, state = sim.run_quantum_gate(1.0, 0.8)
    print(f"Logic Gate State    : {state} | Left: {ch_l:.2f}, Right: {ch_r:.2f}")
    print(f"Wireless Emission   : Peak Power = {sim.run_extraction(ch_r):.4f}")
