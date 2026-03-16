"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

PROMPT_FILE = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")


class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Carrega o prompt v2 antes de cada teste."""
        data = load_prompts(PROMPT_FILE)
        self.prompt = data["bug_to_user_story_v2"]
        self.system_prompt = self.prompt.get("system_prompt", "")

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt, "Campo 'system_prompt' não encontrado"
        assert self.system_prompt.strip(), "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        role_keywords = ["você é um", "você é uma", "voce e um", "voce e uma"]
        text = self.system_prompt.lower()
        assert any(kw in text for kw in role_keywords), \
            "Prompt não define uma persona/role (ex: 'Você é um Product Manager')"

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        format_keywords = [
            "como um", "eu quero", "para que",
            "user story", "markdown",
            "given-when-then", "dado-quando-então",
            "dado que", "quando", "então",
            "critérios de aceitação", "criterios de aceitacao",
        ]
        text = self.system_prompt.lower()
        assert any(kw in text for kw in format_keywords), \
            "Prompt não menciona formato User Story ou Markdown"

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        example_keywords = ["exemplo", "example", "bug:", "user story:"]
        text = self.system_prompt.lower()
        matches = sum(1 for kw in example_keywords if kw in text)
        assert matches >= 2, \
            "Prompt não contém exemplos suficientes de entrada/saída (Few-shot)"

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum [TODO] no texto."""
        assert "[TODO]" not in self.system_prompt, \
            "system_prompt ainda contém [TODO]"
        assert "[todo]" not in self.system_prompt.lower(), \
            "system_prompt ainda contém [todo]"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt.get("techniques_applied", [])
        assert len(techniques) >= 2, \
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])