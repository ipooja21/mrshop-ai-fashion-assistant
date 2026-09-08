from app.memory.vector_memory import SemanticMemory


def test_vector_memory_structure():
    memory = SemanticMemory()

    assert memory.index is not None
    assert memory.metadata is not None