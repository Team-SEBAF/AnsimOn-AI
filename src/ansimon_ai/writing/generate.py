from schemas.complaint_writing import (
    ComplaintDocumentOutput,
    ComplaintWritingAiInput,
    DamageFactsStatementOutput,
)

def generate_complaint_document(
    ai_input: ComplaintWritingAiInput,
    *,
    llm_client,
) -> ComplaintDocumentOutput:
    raise NotImplementedError("Complaint document generation is not implemented yet.")

def generate_damage_facts_statement(
    ai_input: ComplaintWritingAiInput,
    *,
    llm_client,
) -> DamageFactsStatementOutput:
    raise NotImplementedError(
        "Damage facts statement generation is not implemented yet."
    )