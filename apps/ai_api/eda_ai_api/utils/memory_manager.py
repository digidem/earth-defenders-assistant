"""
Centralized memory manager for the AI API.
Provides access to singleton instances of memory classes to prevent multiple expensive initializations.
"""

from typing import Optional
from loguru import logger

from eda_ai_api.utils.vector_memory import VectorMemory
from eda_ai_api.utils.memory import PocketBaseMemory


class MemoryManager:
    """Centralized memory manager providing singleton access to memory instances"""

    _vector_memory: Optional[VectorMemory] = None
    _pocketbase_memory: Optional[PocketBaseMemory] = None

    @classmethod
    def get_vector_memory(cls) -> VectorMemory:
        """Get the singleton VectorMemory instance"""
        if cls._vector_memory is None:
            logger.debug("Initializing VectorMemory singleton instance")
            cls._vector_memory = VectorMemory()
        return cls._vector_memory

    @classmethod
    def get_pocketbase_memory(cls) -> PocketBaseMemory:
        """Get the singleton PocketBaseMemory instance"""
        if cls._pocketbase_memory is None:
            logger.debug("Initializing PocketBaseMemory singleton instance")
            cls._pocketbase_memory = PocketBaseMemory()
        return cls._pocketbase_memory

    @classmethod
    def initialize(cls) -> None:
        """Pre-initialize all memory instances"""
        logger.info("Pre-initializing memory instances")
        cls.get_vector_memory()
        cls.get_pocketbase_memory()
        logger.info("Memory instances initialized successfully")


# Convenience functions for easy access
def get_vector_memory() -> VectorMemory:
    """Get the singleton VectorMemory instance"""
    return MemoryManager.get_vector_memory()


def get_pocketbase_memory() -> PocketBaseMemory:
    """Get the singleton PocketBaseMemory instance"""
    return MemoryManager.get_pocketbase_memory()
