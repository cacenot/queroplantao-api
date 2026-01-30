"""
Business Rules tools for the MCP server.

These tools provide LLM-powered explanations of business rules,
workflow diagrams, and state machines.
"""

from __future__ import annotations

from queroplantao_mcp.config import (
    MODULES_DIR,
    MODULES_DOCS_DIR,
    get_module_docs_path,
)
from queroplantao_mcp.llm import get_llm_client
from queroplantao_mcp.parsers import get_enum_parser


async def explain_business_rule(
    topic: str,
    module: str | None = None,
    context: str | None = None,
) -> dict:
    """
    Explain a business rule using LLM analysis.

    This tool reads documentation and code to provide a comprehensive
    explanation of a business rule or concept.

    Args:
        topic: The topic or rule to explain (e.g., "validação de CPF em família",
               "fluxo de triagem", "reuso de documentos").
        module: Optional module to focus on.
        context: Additional context for the question.

    Returns:
        Explanation with related code references and frontend implications.
    """
    # Gather documentation
    documentation = ""

    if module:
        doc_path = get_module_docs_path(module)
        if doc_path and doc_path.exists():
            documentation = doc_path.read_text(encoding="utf-8")
    else:
        # Try to find relevant documentation based on topic keywords
        topic_lower = topic.lower()
        for doc_file in MODULES_DOCS_DIR.glob("*.md"):
            if any(
                keyword in topic_lower for keyword in [doc_file.stem.lower().replace("_module", "").replace("_", " ")]
            ):
                documentation = doc_file.read_text(encoding="utf-8")
                break

    # Find related code if possible
    related_code = ""
    if module:
        use_cases_dir = MODULES_DIR / module / "use_cases"
        if use_cases_dir.exists():
            # List available use cases for context
            use_case_files = list(use_cases_dir.rglob("*.py"))[:5]
            related_code = f"Available use cases in {module}:\n"
            for f in use_case_files:
                related_code += f"- {f.name}\n"

    # Call LLM
    llm = get_llm_client()
    explanation = await llm.explain_business_rule(
        topic=topic,
        related_code=related_code if related_code else None,
        documentation=documentation[:8000] if documentation else None,  # Limit size
    )

    return {
        "topic": topic,
        "module": module,
        "explanation": explanation,
        "documentation_used": bool(documentation),
        "code_context": bool(related_code),
    }


async def get_workflow_diagram(
    workflow: str,
    format: str = "mermaid",
) -> dict:
    """
    Generate a workflow diagram.

    Args:
        workflow: Name of the workflow (e.g., "screening_flow", "document_review",
                  "alert_handling", "professional_onboarding").
        format: Output format - "mermaid", "ascii", or "steps".

    Returns:
        Diagram in the specified format with metadata.
    """
    # Known workflows with their documentation sources
    workflow_docs: dict[str, str] = {}

    # Load screening workflow from documentation
    screening_doc = get_module_docs_path("screening")
    if screening_doc and screening_doc.exists():
        workflow_docs["screening_flow"] = screening_doc.read_text(encoding="utf-8")
        workflow_docs["document_review"] = workflow_docs["screening_flow"]
        workflow_docs["alert_handling"] = workflow_docs["screening_flow"]

    # Get context for the workflow
    context = workflow_docs.get(workflow, "")

    if format == "steps":
        # Return structured steps instead of diagram
        return await _get_workflow_steps(workflow, context)

    # Generate diagram with LLM
    llm = get_llm_client()
    diagram = await llm.generate_diagram(
        workflow=f"Generate a {format} diagram for the '{workflow}' workflow",
        format_=format,
        context=context[:6000] if context else None,
    )

    return {
        "workflow": workflow,
        "format": format,
        "diagram": diagram,
        "has_documentation": bool(context),
    }


async def _get_workflow_steps(workflow: str, context: str) -> dict:
    """Get structured workflow steps."""
    # Pre-defined workflows based on the codebase
    known_workflows = {
        "screening_flow": {
            "workflow": "screening_flow",
            "format": "steps",
            "steps": [
                {
                    "order": 1,
                    "type": "CONVERSATION",
                    "name": "Conversa Inicial",
                    "required": True,
                    "actor": "Gestor",
                    "actions": ["Registrar notas", "Definir outcome (PROCEED/REJECT)"],
                    "next_on_success": "PROFESSIONAL_DATA",
                    "next_on_failure": "REJECTED",
                },
                {
                    "order": 2,
                    "type": "PROFESSIONAL_DATA",
                    "name": "Dados do Profissional",
                    "required": True,
                    "actor": "Profissional (via link) ou Gestor",
                    "actions": [
                        "Preencher dados pessoais",
                        "Adicionar qualificações",
                        "Adicionar especialidades",
                        "Adicionar formação",
                    ],
                    "next_on_success": "DOCUMENT_UPLOAD",
                },
                {
                    "order": 3,
                    "type": "DOCUMENT_UPLOAD",
                    "name": "Upload de Documentos",
                    "required": True,
                    "actor": "Profissional (via link) ou Gestor",
                    "actions": [
                        "Upload de documentos obrigatórios",
                        "Reuso de documentos válidos",
                    ],
                    "next_on_success": "DOCUMENT_REVIEW",
                },
                {
                    "order": 4,
                    "type": "DOCUMENT_REVIEW",
                    "name": "Revisão de Documentos",
                    "required": True,
                    "actor": "Gestor",
                    "actions": [
                        "Aprovar documentos",
                        "Solicitar correção",
                        "Criar alerta se necessário",
                    ],
                    "next_on_success": "PAYMENT_INFO (se configurado) ou APPROVED",
                },
                {
                    "order": 5,
                    "type": "PAYMENT_INFO",
                    "name": "Informações de Pagamento",
                    "required": False,
                    "actor": "Profissional ou Gestor",
                    "actions": ["Informar conta bancária", "Cadastrar empresa PJ (se aplicável)"],
                    "next_on_success": "CLIENT_VALIDATION (se configurado) ou APPROVED",
                },
                {
                    "order": 6,
                    "type": "CLIENT_VALIDATION",
                    "name": "Validação do Cliente",
                    "required": False,
                    "actor": "Cliente",
                    "actions": ["Aprovar ou rejeitar profissional"],
                    "next_on_success": "APPROVED",
                    "next_on_failure": "REJECTED",
                },
            ],
        },
        "document_review": {
            "workflow": "document_review",
            "format": "steps",
            "steps": [
                {
                    "order": 1,
                    "state": "PENDING_UPLOAD",
                    "name": "Aguardando Upload",
                    "actor": "Profissional",
                    "action": "Fazer upload do documento",
                },
                {
                    "order": 2,
                    "state": "PENDING_REVIEW",
                    "name": "Aguardando Revisão",
                    "actor": "Gestor",
                    "action": "Revisar documento",
                },
                {
                    "order": 3,
                    "state": "APPROVED | CORRECTION_NEEDED",
                    "name": "Resultado da Revisão",
                    "actor": "Sistema",
                    "action": "Documento aprovado ou solicitada correção",
                },
            ],
        },
    }

    if workflow in known_workflows:
        return known_workflows[workflow]

    # Use LLM for unknown workflows
    llm = get_llm_client()
    steps_text = await llm.chat(
        user_message=f"Describe the steps for the '{workflow}' workflow in JSON format",
        system_message="Return a JSON object with a 'steps' array containing step objects with: order, name, actor, actions, next_on_success",
    )

    return {
        "workflow": workflow,
        "format": "steps",
        "raw_response": steps_text,
        "note": "Generated by LLM - verify accuracy",
    }


async def get_state_machine(entity: str) -> dict:
    """
    Get the state machine for an entity.

    Args:
        entity: Name of the entity (e.g., "ScreeningProcess", "ScreeningDocument",
                "StepStatus").

    Returns:
        State machine with states, transitions, and UI hints.
    """
    # Get enum if it represents states
    enum_parser = get_enum_parser()

    # Known state machines based on the codebase
    state_machines: dict[str, dict] = {
        "ScreeningProcess": {
            "entity": "ScreeningProcess",
            "status_field": "status",
            "states": [
                "IN_PROGRESS",
                "PENDING_SUPERVISOR",
                "APPROVED",
                "REJECTED",
                "EXPIRED",
                "CANCELLED",
            ],
            "initial_state": "IN_PROGRESS",
            "terminal_states": ["APPROVED", "REJECTED", "EXPIRED", "CANCELLED"],
            "transitions": [
                {
                    "from": "IN_PROGRESS",
                    "to": "PENDING_SUPERVISOR",
                    "trigger": "create_alert()",
                    "description": "Alerta criado, aguardando supervisor",
                },
                {
                    "from": "IN_PROGRESS",
                    "to": "APPROVED",
                    "trigger": "complete_all_steps()",
                    "description": "Todas etapas completadas",
                },
                {
                    "from": "IN_PROGRESS",
                    "to": "REJECTED",
                    "trigger": "reject()",
                    "description": "Rejeitado em qualquer etapa",
                },
                {
                    "from": "IN_PROGRESS",
                    "to": "EXPIRED",
                    "trigger": "expire()",
                    "description": "Prazo expirado",
                },
                {
                    "from": "IN_PROGRESS",
                    "to": "CANCELLED",
                    "trigger": "cancel()",
                    "description": "Cancelado pela organização",
                },
                {
                    "from": "PENDING_SUPERVISOR",
                    "to": "IN_PROGRESS",
                    "trigger": "resolve_alert()",
                    "description": "Alerta resolvido, continua processo",
                },
                {
                    "from": "PENDING_SUPERVISOR",
                    "to": "REJECTED",
                    "trigger": "reject_via_alert()",
                    "description": "Rejeitado via alerta",
                },
            ],
            "ui_hints": {
                "IN_PROGRESS": {"color": "blue", "icon": "loader", "label": "Em Andamento"},
                "PENDING_SUPERVISOR": {
                    "color": "yellow",
                    "icon": "alert-triangle",
                    "label": "Aguardando Supervisor",
                },
                "APPROVED": {"color": "green", "icon": "check-circle", "label": "Aprovado"},
                "REJECTED": {"color": "red", "icon": "x-circle", "label": "Rejeitado"},
                "EXPIRED": {"color": "gray", "icon": "clock", "label": "Expirado"},
                "CANCELLED": {"color": "gray", "icon": "ban", "label": "Cancelado"},
            },
        },
        "ScreeningDocument": {
            "entity": "ScreeningDocument",
            "status_field": "status",
            "states": [
                "PENDING_UPLOAD",
                "PENDING_REVIEW",
                "APPROVED",
                "CORRECTION_NEEDED",
                "REUSED",
                "SKIPPED",
            ],
            "initial_state": "PENDING_UPLOAD",
            "terminal_states": ["APPROVED", "REUSED", "SKIPPED"],
            "transitions": [
                {
                    "from": "PENDING_UPLOAD",
                    "to": "PENDING_REVIEW",
                    "trigger": "upload()",
                    "endpoint": "POST /documents/{id}/upload",
                },
                {
                    "from": "PENDING_UPLOAD",
                    "to": "REUSED",
                    "trigger": "reuse()",
                    "endpoint": "POST /documents/{id}/reuse",
                },
                {
                    "from": "PENDING_UPLOAD",
                    "to": "SKIPPED",
                    "trigger": "skip()",
                    "endpoint": "POST /documents/{id}/skip",
                },
                {
                    "from": "PENDING_REVIEW",
                    "to": "APPROVED",
                    "trigger": "review(status=APPROVED)",
                    "endpoint": "POST /documents/{id}/review",
                },
                {
                    "from": "PENDING_REVIEW",
                    "to": "CORRECTION_NEEDED",
                    "trigger": "review(status=CORRECTION_NEEDED)",
                    "endpoint": "POST /documents/{id}/review",
                },
                {
                    "from": "CORRECTION_NEEDED",
                    "to": "PENDING_REVIEW",
                    "trigger": "upload() [re-upload]",
                    "endpoint": "POST /documents/{id}/upload",
                },
            ],
            "ui_hints": {
                "PENDING_UPLOAD": {
                    "color": "gray",
                    "icon": "upload",
                    "label": "Aguardando Upload",
                    "action": "Enviar",
                },
                "PENDING_REVIEW": {
                    "color": "yellow",
                    "icon": "clock",
                    "label": "Aguardando Revisão",
                    "action": None,
                },
                "APPROVED": {
                    "color": "green",
                    "icon": "check",
                    "label": "Aprovado",
                    "action": None,
                },
                "CORRECTION_NEEDED": {
                    "color": "red",
                    "icon": "alert-circle",
                    "label": "Correção Necessária",
                    "action": "Corrigir",
                },
                "REUSED": {
                    "color": "blue",
                    "icon": "refresh",
                    "label": "Reutilizado",
                    "action": None,
                },
                "SKIPPED": {
                    "color": "gray",
                    "icon": "skip-forward",
                    "label": "Pulado",
                    "action": None,
                },
            },
        },
        "StepStatus": {
            "entity": "StepStatus",
            "status_field": "status",
            "states": [
                "PENDING",
                "IN_PROGRESS",
                "COMPLETED",
                "APPROVED",
                "REJECTED",
                "SKIPPED",
                "CANCELLED",
                "CORRECTION_NEEDED",
            ],
            "initial_state": "PENDING",
            "terminal_states": ["APPROVED", "REJECTED", "SKIPPED", "CANCELLED"],
            "transitions": [
                {"from": "PENDING", "to": "IN_PROGRESS", "trigger": "start()"},
                {"from": "IN_PROGRESS", "to": "COMPLETED", "trigger": "submit()"},
                {"from": "COMPLETED", "to": "APPROVED", "trigger": "approve()"},
                {"from": "COMPLETED", "to": "REJECTED", "trigger": "reject()"},
                {"from": "COMPLETED", "to": "CORRECTION_NEEDED", "trigger": "request_correction()"},
                {"from": "CORRECTION_NEEDED", "to": "IN_PROGRESS", "trigger": "start_correction()"},
                {"from": "PENDING", "to": "SKIPPED", "trigger": "skip()"},
                {"from": "*", "to": "CANCELLED", "trigger": "cancel_process()"},
            ],
            "ui_hints": {
                "PENDING": {"color": "gray", "icon": "circle", "label": "Pendente"},
                "IN_PROGRESS": {"color": "blue", "icon": "loader", "label": "Em Andamento"},
                "COMPLETED": {"color": "yellow", "icon": "check", "label": "Concluído"},
                "APPROVED": {"color": "green", "icon": "check-circle", "label": "Aprovado"},
                "REJECTED": {"color": "red", "icon": "x-circle", "label": "Rejeitado"},
                "SKIPPED": {"color": "gray", "icon": "skip-forward", "label": "Pulado"},
                "CANCELLED": {"color": "gray", "icon": "ban", "label": "Cancelado"},
                "CORRECTION_NEEDED": {
                    "color": "orange",
                    "icon": "alert-circle",
                    "label": "Correção Necessária",
                },
            },
        },
    }

    if entity in state_machines:
        return state_machines[entity]

    # Try to find enum and generate state machine
    enum_info = enum_parser.get_enum(entity)
    if enum_info and "Status" in entity:
        states = [m["value"] for m in enum_info["members"]]
        ui_hints = {m["value"]: {"label": m["label_pt"] or m["value"]} for m in enum_info["members"]}

        return {
            "entity": entity,
            "status_field": "status",
            "states": states,
            "ui_hints": ui_hints,
            "note": "Generated from enum - transitions not defined",
        }

    return {
        "entity": entity,
        "error": f"State machine not found for entity: {entity}",
        "available": list(state_machines.keys()),
    }


async def validate_user_story(
    story: str,
    module: str | None = None,
) -> dict:
    """
    Validate if a user story can be implemented with the available API.

    Args:
        story: User story in natural language (e.g., "Como gestor, quero aprovar
               todos os documentos de uma triagem de uma vez").
        module: Optional module to focus the analysis.

    Returns:
        Validation result with implementability, required endpoints, and suggestions.
    """
    from queroplantao_mcp.parsers import get_openapi_parser

    # Get available endpoints
    openapi = get_openapi_parser()
    try:
        endpoints = openapi.get_endpoints(module=module)
    except FileNotFoundError:
        endpoints = []

    # Format endpoints for LLM
    endpoints_summary = "\n".join(
        [f"- {e['method']} {e['path']}: {e.get('summary', 'No description')}" for e in endpoints[:30]]
    )

    # Use LLM to analyze
    llm = get_llm_client()
    from queroplantao_mcp.llm.prompts import USER_STORY_VALIDATION_PROMPT

    analysis = await llm.chat(
        user_message=f"""## User Story

{story}

## Available API Endpoints

{endpoints_summary}

## Analysis Required

1. Is this story fully implementable with the available endpoints?
2. Which endpoints would be needed?
3. Are there any gaps or missing functionality?
4. What's the recommended implementation approach?
5. Any workarounds if something is missing?
""",
        system_message=USER_STORY_VALIDATION_PROMPT,
    )

    return {
        "story": story,
        "module": module,
        "endpoints_analyzed": len(endpoints),
        "analysis": analysis,
    }
