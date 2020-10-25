# Welcome to Gameta

Gameta is a CLI tool that helps manage meta-repositories or metarepos. 
It is a play on the word gamete (reproductive cells), and akin to how 
gametes form the building blocks for life, gameta helps to manage the
many repositories that form the building blocks for more complex 
software.

## Metarepos?

A dichotomy exists in the way we store and manage code at present, at
one end of the spectrum we have the monorepo, a single repository 
containing all source code within a project or organisation. The 
monorepo has various advantages, for instance project discovery,
dependencies and versioning are much simpler to manage. However, this
comes at the expense of complicated, customised tooling, increasing 
complexity when scaling and upgrading the system and long CI/CD build
times. Proponents of this methodology include companies like Google, 
Facebook and Twitter, many of whom can afford huge teams to customise
tools to manage such an ecosystem.

At the other end of the spectrum, we have the multirepo architecture, 
where source code is split across many repositories. In this paradigm,
the advantages and disadvantages of the monorepo are reversed i.e. 
the project is dissociated into smaller organised parts and becomes 
easier to manage, whereas coordinating all of these fragmented pieces
becomes a nightmare.

Metarepos provide a middle ground between these 2 polar extremes. Source
code is stored across many repositories, allowing the organisation to
capitalise on the benefits of a multirepo architecture. The fragmented 
code landscape is pieced together in a single repository or metarepo
that stores links to the relevant code bases rather than the actual code
itself. Actual code is pulled from the child repositories whenever required
e.g. during build and delivery, enabling users to capitalise on the benefits
of a monorepo architecture.
