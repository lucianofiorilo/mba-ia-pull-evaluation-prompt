"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt 'leonanluppi/bug_to_user_story_v1' do LangSmith Hub
    e retorna os dados estruturados para salvar em YAML.
    """
    print_section_header("Pull de Prompts do LangSmith Hub")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return None

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    print(f"Fazendo pull do prompt: {prompt_name}")

    try:
        prompt = hub.pull(prompt_name)
        print(f"✓ Prompt obtido com sucesso!")

        # Extrair dados do prompt template
        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": "",
                "user_prompt": "",
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        # Extrair mensagens do ChatPromptTemplate
        for msg in prompt.messages:
            msg_type = msg.__class__.__name__
            content = msg.prompt.template if hasattr(msg, 'prompt') else str(msg.content)

            if "System" in msg_type:
                prompt_data["bug_to_user_story_v1"]["system_prompt"] = content
            elif "Human" in msg_type:
                prompt_data["bug_to_user_story_v1"]["user_prompt"] = content

        return prompt_data

    except Exception as e:
        print(f"✗ Erro ao fazer pull do prompt: {e}")
        return None


def main():
    """Função principal"""
    prompt_data = pull_prompts_from_langsmith()

    if prompt_data is None:
        print("\n✗ Falha ao obter prompts do LangSmith.")
        return 1

    output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"

    if save_yaml(prompt_data, str(output_path)):
        print(f"\n✓ Prompt salvo em: {output_path}")
        print("\nConteúdo salvo:")
        system = prompt_data["bug_to_user_story_v1"].get("system_prompt", "")
        print(f"  System prompt: {system[:100]}..." if len(system) > 100 else f"  System prompt: {system}")
        return 0
    else:
        print("\n✗ Falha ao salvar prompt.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
