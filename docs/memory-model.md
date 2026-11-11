# Memory v0.1 — text-bearing neuronal assemblies

This is an isolated mathematical experiment. It does not modify the runtime.

## Purpose

Explore whether associations, pattern completion, interference and forgetting can arise in a plastic recurrent network. **A long text is attached to a group of neurons**, not to an individual neuron. Assemblies may overlap. Raw conversation remains the LLM's responsibility.

## State

- `activity`: $a\in[0,1]^N$, rapidly changing neuronal activity.
- `weights`: symmetric, nonnegative, zero-diagonal synaptic weights $W$.
- `thresholds`: per-neuron adaptive recruitment thresholds $\theta$.
- `records`: $(T_\mu,\xi^\mu)$, a text payload and its binary $k$-neuron assembly.
- `projection`: fixed random matrix $B$ mapping external embeddings into currents.

## Dynamical model

A rate-based network uses the Euler update

$$
a^+=a+\Delta t\left[\sigma_\beta\left(Wa+I-\theta-\frac gk(\mathbf1^Ta)\mathbf1\right)-a\right].
$$

The caller supplies a vector encoder $z(T)$; stimulus $I=Bz/\lVert z\rVert$. A new assembly consists of the $k$ largest components of

$$
d=Bz/\lVert z\rVert+\rho a-\theta+\epsilon.
$$

It reinforces connections with $\widetilde W_{ij}=W_{ij}+\eta\xi_i\xi_j/(k-1)$ for $i\ne j$. Symmetric resource scaling keeps the sum of weights in each row below a fixed budget. Thresholds adapt via $\theta_i^+=\operatorname{clip}(\theta_i+\gamma(\xi_i-k/N))$.

Text readout scores each assembly by mean activity inside minus mean activity outside its set. Multiple texts may be recalled simultaneously. The state snapshot can be serialized to JSON; the **same encoder must be supplied on restoration**.

## Recall schedule

`recall(cue)` drives the network with the cue for 8 Euler steps and **reads immediately** (`settle_steps=0` by default). An optional `settle_steps>0` advances the network **without input** before readout, and can suppress recall.

This is a correctness fix for Issue #10, **not proof of attractor-based pattern completion**. In the current parametrization, an input-free 30-step settling phase collapses cue-specific activity (lexical-v1 ten-fact regression: 3/10 correct top-1 with 30 steps versus 10/10 with 0). The model can return correct items due to the external encoder and stimulus even if recurrent connections are not contributing meaningful completion. Measure this using frozen, shuffled, or zeroed recurrent weights before claiming learned association. The default `recall_threshold=0.35` is coupled to cue drive duration and may need recalibration if drive steps change.

## Limitations

- Rate neurons and global inhibitory feedback are abstractions; this is not a spiking network.
- The external encoder is required. Random projection does **not** provide semantic comprehension; unit tests use a synthetic codebook.
- Tests check mechanical invariants and a simple retrieval case, not biological fidelity or long-term semantic learning.
- Interference, forgetting, **pattern completion**, and stable long-run behavior remain hypotheses requiring measured sequential-learning and frozen-weight controls.
- The `write` operation activates the newly allocated group; calling `clear_activity()` allows independent recall trials.

## Reproduce

Python 3.10+ with NumPy is required. From repository root:

```sh
python -m pip install numpy
python -m unittest discover -s tests -p 'test_memory_experiment.py' -v
```
