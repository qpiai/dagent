# Option 1: Empty file (just makes it a package)

# Option 2: Import key classes for easier access
from .dag import DAG, DAGNode, build_dag_from_plan

# Option 3: Control what's exported
__all__ = ['DAG', 'DAGNode', 'build_dag_from_plan']