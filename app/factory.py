from app.agent.search_agent import AgentSearchService
from app.connectors.mock_a import MockAConnector
from app.connectors.mock_b import MockBConnector


def build_agent_search_service() -> AgentSearchService:
    return AgentSearchService(connectors=[MockAConnector(), MockBConnector()])
