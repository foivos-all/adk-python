from google.adk.tools._gemini_schema_util import _dereference_schema


class TestDereferenceSchemaCircularRefs:
  """Test circular $ref detection and handling in _dereference_schema."""

  def test_simple_circular_ref(self):
    """Test detection of simple circular reference (linked list)."""
    schema = {
        "$defs": {
            "Node": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "next": {"$ref": "#/$defs/Node"},
                },
            }
        },
        "$ref": "#/$defs/Node",
    }

    # Should not raise RecursionError
    result = _dereference_schema(schema)
    assert result is not None
    assert "properties" in result

  def test_nested_circular_ref_binary_tree(self):
    """Test circular reference in binary tree structure."""
    schema = {
        "$defs": {
            "TreeNode": {
                "type": "object",
                "properties": {
                    "value": {"type": "integer"},
                    "left": {"$ref": "#/$defs/TreeNode"},
                    "right": {"$ref": "#/$defs/TreeNode"},
                },
            }
        },
        "type": "object",
        "properties": {"root": {"$ref": "#/$defs/TreeNode"}},
    }

    result = _dereference_schema(schema)
    assert result is not None
    assert "properties" in result
    assert "root" in result["properties"]

  def test_mutual_circular_refs(self):
    """Test mutually recursive circular references."""
    schema = {
        "$defs": {
            "Person": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "friends": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/Person"},
                    },
                    "spouse": {"$ref": "#/$defs/Person"},
                },
            }
        },
        "$ref": "#/$defs/Person",
    }

    result = _dereference_schema(schema)
    assert result is not None

  def test_deep_circular_ref_chain(self):
    """Test circular reference through multiple definition levels (A→B→C→A)."""
    schema = {
        "$defs": {
            "A": {"type": "object", "properties": {"b": {"$ref": "#/$defs/B"}}},
            "B": {"type": "object", "properties": {"c": {"$ref": "#/$defs/C"}}},
            "C": {"type": "object", "properties": {"a": {"$ref": "#/$defs/A"}}},
        },
        "$ref": "#/$defs/A",
    }

    result = _dereference_schema(schema)
    assert result is not None

  def test_non_circular_refs_still_dereference(self):
    """Test that non-circular refs are properly dereferenced."""
    schema = {
        "$defs": {
            "Address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                },
            },
            "Person": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"$ref": "#/$defs/Address"},
                },
            },
        },
        "$ref": "#/$defs/Person",
    }

    result = _dereference_schema(schema)
    assert result is not None
    assert "properties" in result
    assert "address" in result["properties"]
    # Non-circular refs should be fully dereferenced
    assert "properties" in result["properties"]["address"]

  def test_array_with_circular_items(self):
    """Test circular reference in array items (category tree)."""
    schema = {
        "$defs": {
            "Category": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "subcategories": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/Category"},
                    },
                },
            }
        },
        "$ref": "#/$defs/Category",
    }

    result = _dereference_schema(schema)
    assert result is not None
    assert "properties" in result

  def test_mixed_circular_and_non_circular(self):
    """Test schema with both circular and non-circular references."""
    schema = {
        "$defs": {
            "Metadata": {
                "type": "object",
                "properties": {"created": {"type": "string"}},
            },
            "Document": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "metadata": {"$ref": "#/$defs/Metadata"},
                    "parent": {"$ref": "#/$defs/Document"},
                },
            },
        },
        "$ref": "#/$defs/Document",
    }

    result = _dereference_schema(schema)
    assert result is not None
    assert "properties" in result
    assert "metadata" in result["properties"]

  def test_circular_ref_with_anyof(self):
    """Test circular reference inside anyOf composition."""
    schema = {
        "$defs": {
            "Node": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "child": {
                        "anyOf": [{"$ref": "#/$defs/Node"}, {"type": "null"}]
                    },
                },
            }
        },
        "$ref": "#/$defs/Node",
    }

    result = _dereference_schema(schema)
    assert result is not None

  def test_circular_ref_with_allof(self):
    """Test circular reference inside allOf composition."""
    schema = {
        "$defs": {
            "Base": {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
            },
            "Extended": {
                "allOf": [
                    {"$ref": "#/$defs/Base"},
                    {
                        "type": "object",
                        "properties": {"parent": {"$ref": "#/$defs/Extended"}},
                    },
                ]
            },
        },
        "$ref": "#/$defs/Extended",
    }

    result = _dereference_schema(schema)
    assert result is not None

  def test_circular_ref_with_oneof(self):
    """Test circular reference inside oneOf composition."""
    schema = {
        "$defs": {
            "PolymorphicNode": {
                "type": "object",
                "properties": {
                    "data": {"type": "string"},
                    "next": {
                        "oneOf": [
                            {"$ref": "#/$defs/PolymorphicNode"},
                            {"type": "string"},
                            {"type": "null"},
                        ]
                    },
                },
            }
        },
        "$ref": "#/$defs/PolymorphicNode",
    }

    result = _dereference_schema(schema)
    assert result is not None

  def test_multiple_independent_circular_refs(self):
    """Test schema with multiple independent circular structures."""
    schema = {
        "$defs": {
            "Tree": {
                "type": "object",
                "properties": {
                    "value": {"type": "integer"},
                    "children": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/Tree"},
                    },
                },
            },
            "Graph": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "neighbors": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/Graph"},
                    },
                },
            },
        },
        "type": "object",
        "properties": {
            "tree": {"$ref": "#/$defs/Tree"},
            "graph": {"$ref": "#/$defs/Graph"},
        },
    }

    result = _dereference_schema(schema)
    assert result is not None
    assert "properties" in result

  def test_empty_schema(self):
    """Test empty schema doesn't cause issues."""
    schema = {}
    result = _dereference_schema(schema)
    assert result == {}

  def test_schema_without_refs(self):
    """Test schema without any $ref works normally."""
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    }
    result = _dereference_schema(schema)
    assert result == schema

  def test_invalid_ref_graceful_handling(self):
    """Test graceful handling of invalid $ref."""
    schema = {
        "$defs": {
            "ValidType": {
                "type": "object",
                "properties": {"field": {"type": "string"}},
            }
        },
        "$ref": "#/$defs/NonExistentType",
    }
    # Should handle gracefully without crashing
    result = _dereference_schema(schema)
    assert result is not None

  def test_deeply_nested_non_circular_refs(self):
    """Test deeply nested but non-circular reference chain."""
    schema = {
        "$defs": {
            "Level1": {
                "type": "object",
                "properties": {"level2": {"$ref": "#/$defs/Level2"}},
            },
            "Level2": {
                "type": "object",
                "properties": {"level3": {"$ref": "#/$defs/Level3"}},
            },
            "Level3": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
            },
        },
        "$ref": "#/$defs/Level1",
    }

    result = _dereference_schema(schema)
    assert result is not None
    assert "properties" in result

  def test_circular_ref_with_additional_properties(self):
    """Test circular reference in additionalProperties."""
    schema = {
        "$defs": {
            "DynamicNode": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "additionalProperties": {"$ref": "#/$defs/DynamicNode"},
            }
        },
        "$ref": "#/$defs/DynamicNode",
    }

    result = _dereference_schema(schema)
    assert result is not None

  def test_self_referencing_with_nullable(self):
    """Test self-reference with nullable field (optional next pointer)."""
    schema = {
        "$defs": {
            "LinkedList": {
                "type": "object",
                "properties": {
                    "data": {"type": "string"},
                    "next": {
                        "anyOf": [
                            {"$ref": "#/$defs/LinkedList"},
                            {"type": "null"},
                        ]
                    },
                },
            }
        },
        "$ref": "#/$defs/LinkedList",
    }

    result = _dereference_schema(schema)
    assert result is not None

  def test_circular_ref_reproducing_issue_3870(self):
    """Reproduce the exact scenario from issue #3870."""
    # This is the type of schema that would cause RecursionError before the fix
    schema = {
        "$defs": {
            "RecursiveType": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "children": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/RecursiveType"},
                    },
                },
            }
        },
        "type": "object",
        "properties": {"root": {"$ref": "#/$defs/RecursiveType"}},
    }

    # Before the fix, this would raise RecursionError
    # After the fix, it should complete successfully
    result = _dereference_schema(schema)
    assert result is not None
    assert "properties" in result
    assert "root" in result["properties"]
