# Tasks

- [ ] Task 1: Create Skill skeleton structure and configuration files
  - [ ] SubTask 1.1: Create autonomous-data-analyst directory structure under skills/
  - [ ] SubTask 1.2: Create skill manifest and configuration files
  - [ ] SubTask 1.3: Create README with usage instructions

- [ ] Task 2: Implement autonomous planning module
  - [ ] SubTask 2.1: Create Goal Parser to convert natural language to task graph
  - [ ] SubTask 2.2: Create Analysis Path Planner with dynamic adjustment
  - [ ] SubTask 2.3: Implement perception → judgment → action cycle

- [ ] Task 3: Implement data acquisition and processing module
  - [ ] SubTask 3.1: Create Data Source Detector for various data types
  - [ ] SubTask 3.2: Create Auto Data Pipeline (fetch, clean, process)
  - [ ] SubTask 3.3: Create Auto Dependency Installer

- [ ] Task 4: Implement multi-agent collaboration system
  - [ ] SubTask 4.1: Create SubAgent concurrent execution mode
  - [ ] SubTask 4.2: Create Independent Multi-Agent mode
  - [ ] SubTask 4.3: Create Plan → Execute mode (Planner, Executor, Reviewer)
  - [ ] SubTask 4.4: Implement parallelism decision rules

- [ ] Task 5: Implement goal-oriented analysis module
  - [ ] SubTask 5.1: Create Method Selector for analysis techniques
  - [ ] SubTask 5.2: Implement statistical analysis methods
  - [ ] SubTask 5.3: Implement machine learning methods
  - [ ] SubTask 5.4: Implement time series analysis
  - [ ] SubTask 5.5: Create assumption tracking and confidence scoring

- [ ] Task 6: Implement self-review and validation system
  - [ ] SubTask 6.1: Create data consistency checker
  - [ ] SubTask 6.2: Create sample size risk analyzer
  - [ ] SubTask 6.3: Create model effectiveness evaluator
  - [ ] SubTask 6.4: Create business rationality checker
  - [ ] SubTask 6.5: Implement risk level classification (Red/Yellow/Blue)

- [ ] Task 7: Implement visualization and reporting module
  - [ ] SubTask 7.1: Create chart selection rules engine
  - [ ] SubTask 7.2: Implement visualization generation
  - [ ] SubTask 7.3: Create report template engine
  - [ ] SubTask 7.4: Implement auto-summary generation

- [ ] Task 8: Implement skill persistence and reuse system
  - [ ] SubTask 8.1: Create skill extraction from successful analysis
  - [ ] SubTask 8.2: Create skill parameterization system
  - [ ] SubTask 8.3: Implement one-click replay mechanism

- [ ] Task 9: Create skill blueprint documentation
  - [ ] SubTask 9.1: Document Skill name, description, and use cases
  - [ ] SubTask 9.2: Document input/output specifications
  - [ ] SubTask 9.3: Document core process flow
  - [ ] SubTask 9.4: Document data processing rules
  - [ ] SubTask 9.5: Document analysis method selection rules
  - [ ] SubTask 9.6: Document visualization specifications
  - [ ] SubTask 9.7: Document multi-agent collaboration rules
  - [ ] SubTask 9.8: Document review rules and exception handling
  - [ ] SubTask 9.9: Document skill reuse template
  - [ ] SubTask 9.10: Provide example use cases (e-commerce, finance, user growth)
  - [ ] SubTask 9.11: Document version iteration suggestions

- [ ] Task 10: Integration testing and validation
  - [ ] SubTask 10.1: Test complete end-to-end workflow
  - [ ] SubTask 10.2: Validate all review checkpoints
  - [ ] SubTask 10.3: Test parallel execution scenarios
  - [ ] SubTask 10.4: Test fallback and exception handling

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 2, Task 3]
- [Task 5] depends on [Task 2, Task 3]
- [Task 6] depends on [Task 5]
- [Task 7] depends on [Task 5]
- [Task 8] depends on [Task 6, Task 7]
- [Task 9] can run in parallel with all implementation tasks
- [Task 10] depends on [Task 8, Task 9]
