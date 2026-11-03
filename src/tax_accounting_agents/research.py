"""TaxResearchAgent: looks up synthetic rules for a topic and jurisdiction."""

from .models import ResearchResult
from .rules import rules_for


class TaxResearchAgent:
    def research(self, topic, jurisdiction):
        rules = rules_for(jurisdiction, topic)
        return ResearchResult(jurisdiction=jurisdiction, topic=topic, rules=rules)

    def research_topics(self, topics, jurisdiction):
        return [self.research(topic, jurisdiction) for topic in topics]
