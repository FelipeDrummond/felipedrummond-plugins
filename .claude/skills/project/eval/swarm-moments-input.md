# Fixture input — Swarm-Moments (idea + hypothesis + why)

**Idea.** Each agent in a decentralized swarm predicts the (mean, covariance) of its local
k-neighborhood latent state — a decoder-free (JEPA-style) distributional generalization of
Mean-Field MARL (Σ=0 recovers mean-field). Loss: Bures-Wasserstein (closed-form W2 between
Gaussians).

**Hypothesis.** An action-conditioned predictor g(z_i, a_i) → (μ̂, Σ̂) (arm D) improves a
decentralized cohesion-conditional-on-survival metric over MAPPO and MF-MAPPO at N=16 on a
predator-avoidance task; a representation-shaping auxiliary Bures loss (arm A) at minimum
improves probe-readout representation quality with no RL-return regression.

**Why.** Mean-field MARL collapses the neighborhood to its mean and loses the spread that
matters under a predator; modeling covariance should capture it. Decoder-free avoids
reconstruction. If the action-conditioned arm is too low-SNR, there is still a publishable
representation-shaping result.

**Known constraints.** Solo researcher, ~12 weeks, ~$300 compute. Simulator: VMAS. Baselines
available via BenchMARL/TorchRL. Target: a workshop/main-track submission.
