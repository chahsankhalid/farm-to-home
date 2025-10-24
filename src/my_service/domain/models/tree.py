from dataclasses import dataclass
from typing import Callable, Any, TypeVar, Self

from <%my_service%>.serialization.serializable import Serializable

T = TypeVar('T', bound=Serializable)
ID = TypeVar('ID')
KEY = TypeVar('KEY')


@dataclass
class Tree:
    node: T
    parent: Self | None
    children: list[Self]

    def find(self, select_node: Callable[[T], bool]) -> Self | None:
        if select_node(self.node):
            return self
        else:
            for child in self.children:
                child_result = child.find(select_node)
                if child_result is not None:
                    return child_result
            return None

    def ancestors(self, transform: Callable[[T], KEY] = lambda it: it) -> list[KEY]:
        result = []
        tree = self.parent
        while tree:
            result.append(transform(tree.node))
            tree = tree.parent
        result.reverse()
        return result

    def descendants(self, transform: Callable[[T], KEY] = lambda it: it) -> list[KEY]:
        result = []
        stack = [self]
        while stack:
            current = stack.pop()
            for child in current.children:
                result.append(transform(child.node))
                stack.append(child)
        return result

    def to_dict(self, transform: Callable[[T], KEY]) -> dict[KEY, Any]:
        result = {}
        for child in self.children:
            result[transform(child.node)] = child.to_dict(transform)
        return result

    @classmethod
    def link(cls,
             nodes: list[T],
             identify: Callable[[T], ID],
             identify_parent: Callable[[T], ID | None]) -> Self | None:
        child_nodes_by_id = {}
        for node in nodes:
            parent_id = identify_parent(node)
            if parent_id in child_nodes_by_id:
                child_nodes_by_id[parent_id].append(node)
            else:
                child_nodes_by_id[parent_id] = [node]

        roots = child_nodes_by_id[None]
        if len(roots) != 1:
            logger.error(f'Failed to link tree: there were {len(roots)} roots, expected 1.')
            return None
        root = roots[0]
        return cls._link(root, child_nodes_by_id, identify, identify_parent)

    @classmethod
    def _link(cls,
              node: T,
              child_nodes_by_id: dict[ID | None, list[T]],
              identify: Callable[[T], ID],
              identify_parent: Callable[[T], ID | None]) -> Self:
        child_nodes = child_nodes_by_id.get(identify(node), [])
        child_trees: list[Self] = [
            cls._link(child_node, child_nodes_by_id, identify, identify_parent)
            for child_node in child_nodes
        ]
        # Since the tree is doubly-linked, we need to first create a detached tree without a parent
        tree = cls(node, None, child_trees)
        for child_tree in child_trees:
            child_tree.parent = tree
        return tree
