"""Test target properties (name and file_extension)."""

from dbterd.adapters.targets.d2 import D2Target
from dbterd.adapters.targets.dbml import DBMLTarget
from dbterd.adapters.targets.drawdb import DrawDBTarget
from dbterd.adapters.targets.graphviz import GraphvizTarget
from dbterd.adapters.targets.mermaid import MermaidTarget
from dbterd.adapters.targets.plantuml import PlantUMLTarget


class TestTargetProperties:
    """Test all target implementations have correct properties."""

    def test_d2_properties(self):
        """Test D2 target properties."""
        target = D2Target()
        assert target.name == "d2"
        assert target.file_extension == ".d2"

    def test_dbml_properties(self):
        """Test DBML target properties."""
        target = DBMLTarget()
        assert target.name == "dbml"
        assert target.file_extension == ".dbml"

    def test_drawdb_properties(self):
        """Test DrawDB target properties."""
        target = DrawDBTarget()
        assert target.name == "drawdb"
        assert target.file_extension == ".ddb"

    def test_graphviz_properties(self):
        """Test Graphviz target properties."""
        target = GraphvizTarget()
        assert target.name == "graphviz"
        assert target.file_extension == ".dot"

    def test_mermaid_properties(self):
        """Test Mermaid target properties."""
        target = MermaidTarget()
        assert target.name == "mermaid"
        assert target.file_extension == ".mmd"

    def test_plantuml_properties(self):
        """Test PlantUML target properties."""
        target = PlantUMLTarget()
        assert target.name == "plantuml"
        assert target.file_extension == ".plantuml"
