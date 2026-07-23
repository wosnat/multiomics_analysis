# Figure 1 — The Plan→Run arc

Draft (mermaid source). The overall workflow: a grounded Plan phase converging on
one enumerated proposal, then a Run phase of three gated milestones. Diamonds are
researcher/critic gates.

```mermaid
flowchart TD
    Q[Research question] --> PLAN

    subgraph PLAN[PLAN PHASE · one grounded brainstorming conversation]
        direction TB
        G[Ground in live KG queries<br/>publications · experiments · counts] --> F[Enumerate framing<br/>hypothesis · approach ·<br/>explicit statistics decision ·<br/>named validation set]
        F --> SR{Self-review}
        SR --> CC{Critic<br/>interpretation-only}
        CC --> AP{Researcher<br/>approval}
    end

    AP -->|approved| PROP[(proposal.md<br/>the locked plan)]
    AP -.->|reopen on data reveal| G

    PROP --> M1
    subgraph RUN[RUN PHASE · execute the proposal]
        direction TB
        M1[methods<br/>build + toy-test the machinery] --> M2[analysis<br/>run it · scored outputs]
        M2 --> M3[evaluation<br/>judge vs framing · caveats · paper]
    end

    M3 --> OUT[Graded candidate catalog<br/>+ wet-lab follow-up shortlist]

    classDef gate fill:#fff,stroke:#555,stroke-dasharray:3 3;
    class SR,CC,AP gate;
```

## Notes for the rendered version
- Each Run milestone expands into the co-define→do→show→explore→decide loop
  (Fig 2) with two researcher gates.
- The dashed `reopen` edge (AP → G) is the upstream-lock-edited-by-downstream-
  reveal path — instantiated in the worked example when the medium reveal reopened
  the question.
- Keep the three domain-rule anchors visible somewhere on the final figure (KG =
  sole source · locus tags not names · scripts over chat) — they underlie every box.
