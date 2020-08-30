
from typing import Any, Iterable, Union

from logic.Logic import AndClause, Clause, Entity, NotClause, OrClause, Sentence


class KnowledgeBase:

    def __init__(self):
        self._facts = set([Entity('True')])
        self._statements = set()


    # TODO: Is there a way to generalize this?
    def _entails_atom(self, atom: Entity) -> bool:
        if atom in self._facts:
            return True

        relevant_facts = [fact for fact in self._statements if fact.rhs == atom]
        for fact in relevant_facts:
            if self.entails(fact.lhs):
                return True

        return False

    def _entails_clause(self, clause: Clause) -> bool:
        clause_type, components = clause.get_components()

        results = [self.entails(component) for component in components]
        if issubclass(type(clause), AndClause):
            return all(results)
        elif issubclass(type(clause), OrClause):
            return any(results)
        else:
            return not results[0]

    def add_entity_attributes(self, entity_name: str, attributes: Union[str, Iterable[str]]):
        self.entities[entity_name].attributes.update(attributes)

    def entails(self, query: Union[Entity, Clause]) -> bool:
        if type(query) is Entity:
            return self._entails_atom(query)

        if issubclass(type(query), Clause):
            return self._entails_clause(query)

        return False

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
            self._facts.add(sentence)
        else:
            self._statements.add(sentence.to_predicate())