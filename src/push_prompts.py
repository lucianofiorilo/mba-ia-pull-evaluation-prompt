"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
        # Se username vazio ou push falhar com username, usar apenas o nome do prompt
        full_name = f"{username}/{prompt_name}" if username else prompt_name

        print(f"Fazendo push do prompt: {full_name}")

        try:
            hub.push(
                full_name,
                prompt_template,
                new_repo_is_public=True,
                new_repo_description=prompt_data.get("description", ""),
                tags=prompt_data.get("tags", []),
            )
        except Exception as pub_err:
            # Fallback 1: tentar sem username
            if username:
                print(f"[AVISO] Falha com username '{username}'. Tentando sem username...")
                try:
                    hub.push(
                        prompt_name,
                        prompt_template,
                        new_repo_is_public=True,
                        new_repo_description=prompt_data.get("description", ""),
                        tags=prompt_data.get("tags", []),
                    )
                    full_name = prompt_name
                    print(f"[OK] Push sem username funcionou!")
                    return True
                except Exception:
                    pass
            # Fallback 2: push privado
            print("[AVISO] Nao foi possivel publicar como publico. Publicando como privado...")
            print("        Acesse o LangSmith Hub e torne publico pelo icone de cadeado.")
            fallback_name = prompt_name if username else full_name
            hub.push(
                fallback_name,
                prompt_template,
                new_repo_description=prompt_data.get("description", ""),
                tags=prompt_data.get("tags", []),
            )

        print(f"[OK] Prompt publicado com sucesso: {full_name}")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["description", "system_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data or not prompt_data[field]:
            errors.append(f"Campo obrigatorio faltando ou vazio: {field}")

    system_prompt = prompt_data.get("system_prompt", "")
    if "TODO" in system_prompt or "[TODO]" in system_prompt:
        errors.append("system_prompt ainda contem TODOs")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Minimo de 2 tecnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("Push de Prompts para o LangSmith Hub")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    from pathlib import Path
    yaml_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"

    print(f"Carregando prompt de: {yaml_path}")
    data = load_yaml(str(yaml_path))

    if data is None:
        print("[ERRO] Falha ao carregar arquivo YAML.")
        return 1

    prompt_key = "bug_to_user_story_v2"
    prompt_data = data.get(prompt_key)

    if prompt_data is None:
        print(f"[ERRO] Chave '{prompt_key}' nao encontrada no YAML.")
        return 1

    # Validar prompt
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("[ERRO] Prompt invalido:")
        for err in errors:
            print(f"   - {err}")
        return 1

    print("[OK] Prompt validado com sucesso!")

    # Push para LangSmith
    if push_prompt_to_langsmith(prompt_key, prompt_data):
        print("\nPrompt publicado no LangSmith Hub!")
        username = os.getenv("USERNAME_LANGSMITH_HUB", "")
        print(f"Acesse: https://smith.langchain.com/hub/{username}/{prompt_key}")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
