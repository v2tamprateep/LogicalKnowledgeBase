
from typing import Any, Iterable, Union

from logic.Logic import Clause, Entity, Sentence


class KnowledgeBase:

    def __init__(self):
        self._facts = dict()
        self._statements = set()

    def add_entity_attributes(self, entity_name: str, attributes: Union[str, Iterable[str]]):
        self.entities[entity_name].attributes.update(attributes)

    def entails(self, query: Sentence) -> bool:
        return query.evaluate(self.facts)

    @property
    def facts(self):
        return self._facts

    @property
    def statements(self):
        return self._statements

    def remove_entity_attributes(self, entity_name: str, attributes: Union[str, Iterable[str]]):
        entity = self.entities[entity_name]
        for attribute in attributes:
            entity.attributes.discard(attribute)

    def tell(self, sentence: Sentence):
        if type(sentence) is Entity:
            self._facts[sentence.name] = sentence
        else:
            self._statements.add(sentence.to_predicate())